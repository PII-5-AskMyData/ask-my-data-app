"""
styles.py — CSS centralizado do Ask My Data (Dark Premium Theme)
"""

def get_global_css():
    """Retorna o CSS global compartilhado entre todas as páginas."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ========== RESET GLOBAL ========== */
        html, body, [class*="css"], .stApp {
            font-family: 'Inter', sans-serif !important;
            background-color: #0A0E1A !important;
            color: #E2E8F0 !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 1800px;
        }

        /* ========== SCROLLBAR CUSTOM ========== */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0A0E1A; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }

        /* ========== SIDEBAR ========== */
        [data-testid="stSidebar"] {
            background-color: #0F1629 !important;
            border-right: 1px solid rgba(255,255,255,0.04) !important;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 2rem !important;
        }

        /* Sidebar nav buttons */
        .nav-btn {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.25s ease;
            margin-bottom: 6px;
            text-decoration: none;
            color: #94A3B8;
            font-size: 0.95rem;
            font-weight: 500;
            border: 1px solid transparent;
        }
        .nav-btn:hover {
            background: rgba(59, 130, 246, 0.08);
            color: #CBD5E1;
            border-color: rgba(59, 130, 246, 0.15);
        }
        .nav-btn.active {
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(139, 92, 246, 0.08) 100%);
            color: #F8FAFC;
            border-color: rgba(59, 130, 246, 0.2);
            font-weight: 600;
        }
        .nav-icon { font-size: 1.3rem; }

        /* ========== TIPOGRAFIA ========== */
        .title-gradient {
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #D946EF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 2.8rem;
            letter-spacing: -1.5px;
            line-height: 1.1;
        }
        .title-gradient-lg {
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #D946EF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 4rem;
            letter-spacing: -2px;
            line-height: 1.05;
        }
        .subtitle {
            color: #64748B;
            font-size: 1.05rem;
            font-weight: 400;
            margin-top: 6px;
            letter-spacing: 0.3px;
        }
        .section-label {
            color: #64748B;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
            margin-bottom: 18px;
        }

        /* ========== CARDS ========== */
        .glass-card {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.4) 100%);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 28px;
            color: #CBD5E1;
            font-size: 0.95rem;
            line-height: 1.7;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }
        .glass-card b, .glass-card strong {
            color: #F1F5F9;
            font-weight: 600;
        }

        .table-card {
            background: rgba(15, 23, 42, 0.6);
            border-left: 3px solid #3B82F6;
            border-top: 1px solid rgba(255,255,255,0.04);
            border-right: 1px solid rgba(255,255,255,0.04);
            border-bottom: 1px solid rgba(255,255,255,0.04);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
        }
        .table-card:hover {
            transform: translateX(4px);
            border-left-color: #8B5CF6;
            background: rgba(15, 23, 42, 0.8);
        }
        .table-card .title {
            color: #F1F5F9;
            font-weight: 600;
            font-size: 1.1rem;
            margin-bottom: 4px;
        }
        .table-card .desc {
            color: #94A3B8;
            font-size: 0.85rem;
        }

        .guide-card {
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.25s ease;
        }
        .guide-card:hover {
            border-color: rgba(59, 130, 246, 0.2);
            background: rgba(15, 23, 42, 0.7);
        }
        .guide-card .tag {
            display: inline-block;
            background: rgba(59, 130, 246, 0.15);
            color: #60A5FA;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }
        .guide-card .gtitle {
            color: #F1F5F9;
            font-weight: 600;
            font-size: 1.05rem;
            margin-bottom: 8px;
        }
        .guide-card .gdesc {
            color: #94A3B8;
            font-size: 0.85rem;
            margin-bottom: 12px;
            line-height: 1.5;
        }

        /* ========== INPUTS ========== */
        div[data-baseweb="textarea"],
        div[data-baseweb="input"] {
            border-radius: 12px !important;
            background-color: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid #1E293B !important;
            color: #F1F5F9 !important;
            transition: all 0.3s ease;
        }
        div[data-baseweb="textarea"]:focus-within,
        div[data-baseweb="input"]:focus-within {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
            background-color: rgba(30, 41, 59, 0.6) !important;
        }
        textarea, input {
            color: #F8FAFC !important;
            font-size: 0.95rem !important;
            font-family: 'Inter', sans-serif !important;
        }
        textarea::placeholder, input::placeholder {
            color: #475569 !important;
            opacity: 1 !important;
        }

        /* ========== BOTÕES ========== */
        div.stButton > button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
            color: #FFFFFF;
            border-radius: 10px;
            border: none;
            padding: 0.6rem 2.2rem;
            font-weight: 600;
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.3px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.25);
        }
        div.stButton > button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(59, 130, 246, 0.4);
        }
        div.stButton > button[data-testid="baseButton-primary"]:active {
            transform: translateY(1px);
            box-shadow: 0 2px 10px rgba(59, 130, 246, 0.2);
        }

        div.stButton > button[data-testid="baseButton-secondary"] {
            background: transparent;
            color: #94A3B8;
            border-radius: 10px;
            border: 1px solid #1E293B;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            font-size: 0.9rem;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
        }
        div.stButton > button[data-testid="baseButton-secondary"]:hover {
            border-color: #334155;
            color: #E2E8F0;
            background: rgba(30, 41, 59, 0.3);
        }

        /* ========== FORMS ========== */
        [data-testid="stForm"] {
            border: none !important;
            background: transparent !important;
            padding: 0 !important;
        }

        /* ========== CODE BLOCKS ========== */
        [data-testid="stCodeBlock"] {
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
            overflow: hidden;
        }

        /* ========== TABS ========== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
            background: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #64748B;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(59, 130, 246, 0.1) !important;
            color: #3B82F6 !important;
        }

        /* ========== DATAFRAMES ========== */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
        }

        /* ========== DIVIDERS ========== */
        hr {
            border-color: rgba(255,255,255,0.05) !important;
            margin: 24px 0 !important;
        }

        /* ========== ANIMAÇÃO DE ENTRADA ========== */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .animate-in {
            animation: fadeInUp 0.6s ease-out forwards;
        }
        .animate-in-delay {
            animation: fadeInUp 0.6s ease-out 0.15s forwards;
            opacity: 0;
        }
        .animate-in-delay-2 {
            animation: fadeInUp 0.6s ease-out 0.3s forwards;
            opacity: 0;
        }

        /* ========== MÉTRICAS / STATS ========== */
        .stat-box {
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 14px;
            padding: 20px 24px;
            text-align: center;
        }
        .stat-box .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #F1F5F9;
            margin-bottom: 4px;
        }
        .stat-box .stat-label {
            font-size: 0.8rem;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }
    </style>
    """


def get_login_css():
    """CSS adicional exclusivo da página de login."""
    return """
    <style>
        /* Login: esconder sidebar e header completamente */
        header {visibility: hidden !important;}
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}

        .login-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 85vh;
            text-align: center;
        }
        .login-box {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 24px;
            padding: 48px 42px;
            width: 100%;
            max-width: 420px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5);
            animation: fadeInUp 0.7s ease-out forwards;
        }
        .login-logo {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 6px;
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #D946EF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .login-tagline {
            color: #475569;
            font-size: 0.9rem;
            margin-bottom: 36px;
            font-weight: 400;
        }
        .login-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.08) 50%, transparent 100%);
            margin: 20px 0;
        }

        /* Glow decorativo atrás do login */
        .glow-bg {
            position: fixed;
            top: 15%;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 400px;
            background: radial-gradient(ellipse, rgba(59, 130, 246, 0.08) 0%, rgba(139, 92, 246, 0.04) 40%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }
    </style>
    """
