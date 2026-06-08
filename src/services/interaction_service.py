from datetime import date, datetime, timezone
from uuid import uuid4

import pandas as pd

from src.rag import get_chart_data
from src.repositories.interactions_repository import InteractionsRepository


def _to_bson_safe(value):
    if value is None or isinstance(value, (bool, str, int, float)):
        return value
    if isinstance(value, (datetime, date)):
        return value
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def _serialize_chart_data(data) -> list[dict]:
    if isinstance(data, pd.DataFrame):
        records = data.to_dict(orient="records")
    elif isinstance(data, list):
        records = data
    else:
        records = []

    return [
        {key: _to_bson_safe(val) for key, val in row.items()}
        for row in records
        if isinstance(row, dict)
    ]


def _chart_to_payload(chart: dict | None) -> dict | None:
    if not chart:
        return None

    return {
        "chart_type": chart.get("chart_type"),
        "title": chart.get("title"),
        "x": chart.get("x"),
        "y": chart.get("y"),
        "data": _serialize_chart_data(chart.get("data")),
    }


def _infer_visualizacoes(user_query: str) -> list[dict]:
    query = user_query.lower()
    visualizacoes: list[dict] = []
    seen_cenarios: set[str] = set()

    rules = [
        (
            ["faturamento", "receita", "faturou", "faturamento médio"],
            "faturamento",
            "line",
            "Faturamento",
        ),
        (
            ["produção", "producao", "planta", "volume", "ton", "produz"],
            "comparacao",
            "bar",
            "Produção por planta",
        ),
        (
            ["fornecedor", "compra", "compras", "insumo"],
            "compras",
            "bar",
            "Compras por insumo",
        ),
        (
            ["cliente", "top 10", "ranking", "fornecedores"],
            "comparacao",
            "bar",
            "Ranking",
        ),
        (
            ["mês", "meses", "mensal", "últimos", "ultimos", "evolução", "evolucao"],
            "evolucao",
            "line",
            "Evolução no período",
        ),
        (
            ["dia", "melhor dia", "distribui", "status", "entrega"],
            "distribuicao",
            "pie",
            "Distribuição",
        ),
    ]

    for keywords, cenario, chart_type, title in rules:
        if cenario in seen_cenarios:
            continue
        if any(keyword in query for keyword in keywords):
            visualizacoes.append(
                {
                    "cenario": cenario,
                    "tipo_grafico": chart_type,
                    "titulo": title,
                }
            )
            seen_cenarios.add(cenario)

    defaults = [
        {"cenario": "faturamento", "tipo_grafico": "line", "titulo": "Faturamento"},
        {"cenario": "comparacao", "tipo_grafico": "bar", "titulo": "Comparativo por planta"},
        {"cenario": "distribuicao", "tipo_grafico": "pie", "titulo": "Distribuição geral"},
    ]
    for default in defaults:
        if len(visualizacoes) >= 3:
            break
        if default["cenario"] not in seen_cenarios:
            visualizacoes.append(default)
            seen_cenarios.add(default["cenario"])

    return visualizacoes[:4]


def build_charts_from_visualizacoes(visualizacoes: list[dict]) -> list[dict]:
    charts: list[dict] = []
    for visualizacao in visualizacoes:
        chart = get_chart_data(
            cenario=visualizacao.get("cenario", "comparacao"),
            tipo_grafico=visualizacao.get("tipo_grafico", "bar"),
            titulo_ia=visualizacao.get("titulo", "Gráfico"),
        )
        if not chart:
            continue
        payload = _chart_to_payload(chart)
        if payload:
            charts.append(payload)
    return charts


def _charts_to_payload(charts: list | None) -> list[dict]:
    if not charts:
        return []

    payloads = []
    for chart in charts:
        payload = _chart_to_payload(chart)
        if payload:
            payloads.append(payload)
    return payloads


class InteractionService:
    def __init__(self) -> None:
        self.repository = InteractionsRepository()

    def build_interaction_payload(
        self,
        username: str | None,
        session_id: str | None,
        user_query: str,
        translated_query: str,
        result: dict,
    ) -> dict:
        charts_payload = _charts_to_payload(result.get("charts", []))
        visualizacoes = result.get("visualizacoes") or _infer_visualizacoes(user_query)

        return {
            "history_id": str(uuid4()),
            "username": username,
            "session_id": session_id,
            "user_query": user_query,
            "translated_query": translated_query,
            "tables_identified": result.get("tables_identified", []),
            "generated_script": result.get("generated_script", ""),
            "explanation": result.get("explanation", ""),
            "script_type": result.get("script_type", "SQL"),
            "visualizacoes": visualizacoes,
            "chart": None,
            "charts": charts_payload,
            "created_at": datetime.now(timezone.utc),
        }

    def save_query_run(
        self,
        username: str | None,
        session_id: str | None,
        user_query: str,
        translated_query: str,
        result: dict,
    ) -> dict:
        payload = self.build_interaction_payload(
            username, session_id, user_query, translated_query, result
        )
        saved = self.repository.save_interaction(payload)
        if not saved:
            print(
                "Aviso: nao foi possivel salvar a interacao no MongoDB. "
                "Verifique a conexao e o schema da collection."
            )
        return payload

    def resolve_charts_for_history_item(self, item: dict) -> list[dict]:
        charts = item.get("charts") or []
        if charts:
            return charts

        chart = item.get("chart")
        if isinstance(chart, dict):
            return [chart]

        visualizacoes = item.get("visualizacoes") or _infer_visualizacoes(
            item.get("user_query", "")
        )
        item["visualizacoes"] = visualizacoes
        return build_charts_from_visualizacoes(visualizacoes)

    def persist_rebuilt_charts(
        self,
        item: dict,
        username: str | None,
        charts: list[dict],
        visualizacoes: list[dict] | None = None,
    ) -> bool:
        item["charts"] = charts
        if visualizacoes:
            item["visualizacoes"] = visualizacoes

        return self.repository.update_interaction_charts(
            username=username,
            mongo_id=item.get("id"),
            history_id=item.get("history_id"),
            charts=charts,
            visualizacoes=visualizacoes or item.get("visualizacoes"),
        )
