import pandas as pd

from src.repositories.interactions_repository import InteractionsRepository


def _chart_to_payload(chart: dict | None) -> dict | None:
    if not chart:
        return None

    data = chart.get("data")
    if isinstance(data, pd.DataFrame):
        chart_data = data.to_dict(orient="records")
    else:
        chart_data = data

    return {
        "chart_type": chart.get("chart_type"),
        "title": chart.get("title"),
        "x": chart.get("x"),
        "y": chart.get("y"),
        "data": chart_data,
    }


class InteractionService:
    def __init__(self) -> None:
        self.repository = InteractionsRepository()

    def save_query_run(
        self,
        username: str | None,
        session_id: str | None,
        user_query: str,
        translated_query: str,
        result: dict,
    ) -> None:
        payload = {
            "username": username,
            "session_id": session_id,
            "user_query": user_query,
            "translated_query": translated_query,
            "tables_identified": result.get("tables_identified", []),
            "generated_script": result.get("generated_script", ""),
            "explanation": result.get("explanation", ""),
            "script_type": result.get("script_type", "SQL"),
            "chart": _chart_to_payload(result.get("chart")),
        }
        self.repository.save_interaction(payload)
