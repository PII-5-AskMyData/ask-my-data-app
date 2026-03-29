import streamlit as st
from src.rag import process_user_query

st.set_page_config(
    page_title="Ask My Data",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
        background-color: #0B0F19 !important;
        color: #E2E8F0 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Adicionado padding customizado global seccionado pra Wide View */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1600px;
    }

    /* Topografia Principal */
    .title-gradient {
        background: linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3.2rem;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        font-weight: 300;
        margin-top: -10px;
        margin-bottom: 30px;
        letter-spacing: 0.5px;
    }

    /* Card Dark Texturizado Modificado pra Wide */
    .glass-card {
        background: rgba(30, 41, 59, 0.4); 
        border: 1px solid rgba(255, 255, 255, 0.05); 
        border-radius: 16px;
        padding: 24px;
        color: #CBD5E1;
        font-size: 1rem;
        line-height: 1.6;
        backdrop-filter: blur(10px); 
        -webkit-backdrop-filter: blur(10px);
        margin-bottom: 30px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }
    
    .glass-card b {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 1.1rem;
    }

    /* Área de Texto (Inputs) expandido */
    div[data-baseweb="textarea"] {
        border-radius: 12px !important;
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        color: #F1F5F9 !important;
        transition: all 0.3s ease;
    }
    
    div[data-baseweb="textarea"]:focus-within {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
        background-color: #1E293B !important;
    }
    
    textarea {
        color: #F8FAFC !important;
        font-size: 1.05rem !important; /* Fonte ligeiramente maior aqui */
    }
    textarea::placeholder {
        color: #64748B !important;
        opacity: 1 !important;
        font-size: 1.05rem !important;
    }

    /* Botão Primário Neon */
    div.stButton > button:first-child[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
        color: #FFFFFF;
        border-radius: 10px;
        border: none;
        padding: 0.6rem 2.5rem; /* Botao maior */
        font-weight: 600;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    div.stButton > button:first-child[data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%);
    }

    div.stButton > button:first-child[data-testid="baseButton-primary"]:active {
        transform: translateY(1px);
    }

    /* Form do Streamlit transparente */
    [data-testid="stForm"] {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }

    /* Divider */
    hr {
        border-color: #1E293B !important;
        margin-top: 50px !important;
        margin-bottom: 50px !important;
    }

    /* Resultado - Cards das Tabelas */
    .table-dark-card {
        background-color: #0F172A;
        border-left: 4px solid #3B82F6;
        border-top: 1px solid #1E293B;
        border-right: 1px solid #1E293B;
        border-bottom: 1px solid #1E293B;
        padding: 22px;
        border-radius: 10px;
        margin-bottom: 16px;
        transition: transform 0.2s;
    }
    .table-dark-card:hover {
        transform: translateX(4px);
    }
    .table-dtitle {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 1.15rem;
        margin-bottom: 8px;
    }
    .table-ddesc {
        color: #94A3B8;
        font-size: 0.95rem;
    }
    
    /* Code block dark style nativo modificado */
    [data-testid="stCodeBlock"] {
        border-radius: 12px;
        border: 1px solid #1E293B;
        background-color: #0B0F19 !important;
    }
    
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="title-gradient">Ask My Data</div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Why not make it easy?</p>', unsafe_allow_html=True)

st.markdown('''
    <div class="glass-card">
        <b>Descreva sua busca e a IA codifica</b><br>
        De forma transparente, buscamos as informações no diretório de dados SAP (MSEG, VBRK, etc.) para montar a query perfeita em SQL ou ABAP para os seus analistas e dashboards.
    </div>
''', unsafe_allow_html=True)

with st.form("query_form_dark"):
    st.markdown("<div style='font-size: 1.15rem; color: #E2E8F0; margin-bottom: 14px; font-weight: 500;'>Descreva seu Insight:</div>", unsafe_allow_html=True)
    query = st.text_area(
        "label oculto",
        placeholder="Ex: Quero analisar o volume de produção por planta nos últimos 3 meses...",
        height=160,
        label_visibility="collapsed"
    )
    
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)
    
    btn_col1, btn_col2 = st.columns([2, 5])
    with btn_col1:
        submit = st.form_submit_button("Gerar Script", type="primary", use_container_width=True)

if submit:
    if not query.strip():
        st.warning("O campo não pode estar vazio. Descreva a sua necessidade.")
    else:
        with st.spinner("Conectando ao catálogo semântico SAP..."):
            result = process_user_query(query)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #F8FAFC; font-weight: 600; font-size: 2rem; letter-spacing: -0.5px;'>Resultados Encontrados</h3>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            res_col1, res_col2 = st.columns([1, 2.5], gap="large")
            
            with res_col1:
                st.markdown("<div style='color: #94A3B8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; font-weight: 600;'>Catálogo de Mapeamento SAP</div>", unsafe_allow_html=True)
                if result.get("tables_identified"):
                    for table in result["tables_identified"]:
                        st.markdown(f'''
                        <div class="table-dark-card">
                            <div class="table-dtitle">{table['name']}</div>
                            <div class="table-ddesc">{table['description']}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.info("O mapeamento não encontrou tabelas compatíveis.")
                    
            with res_col2:
                st.markdown(f"<div style='color: #94A3B8; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; font-weight: 600;'>Script {result['script_type']} Recomendado</div>", unsafe_allow_html=True)
                st.code(result["generated_script"], language="sql")
                
                st.markdown("<div style='color: #64748B; font-size: 0.9rem; margin-top: 14px;'>✓ Copie e cole esse código no seu conector ou visualizador de dados.</div>", unsafe_allow_html=True)

