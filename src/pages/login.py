import base64
import streamlit as st
import streamlit.components.v1 as components
from src.styles import get_global_css
from src.repositories.auth_repository import AuthRepository


def _get_login_page_css():
    """CSS da página de login — responsivo para todas as telas."""
    return """
    <style>
        /* ── Reset Streamlit chrome ── */
        header {visibility: hidden !important; height: 0 !important; position: absolute !important;}
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        footer {display: none !important;}

        .stApp {
            background-color: #0d1117 !important;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(255,255,255,0.08) 0%, transparent 50%),
                radial-gradient(circle at 20% 80%, rgba(255,255,255,0.04) 0%, transparent 40%),
                radial-gradient(circle at 80% 20%, rgba(255,255,255,0.04) 0%, transparent 40%) !important;
        }

        section[data-testid="stMain"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            min-height: 100vh !important;
        }

        [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            max-width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
        }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Glassmorphic Card ── */
        [data-testid="stHorizontalBlock"] {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(40px) !important;
            -webkit-backdrop-filter: blur(40px) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 24px !important;
            padding: 60px 40px !important;
            max-width: 850px !important;
            width: 90% !important;
            margin: auto !important;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255,255,255,0.1) !important;
            align-items: center !important;
            gap: 3rem !important;
            z-index: 2;
        }

        /* ── TELA PEQUENA (MOBILE) ── */
        @media (max-width: 768px) {
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                padding: 40px 20px !important;
                gap: 2rem !important;
            }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {
                display: none !important; /* Hide carousel on mobile */
            }
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
                width: 100% !important;
            }
        }

        /* Brand section */
        .brand-section {
            text-align: center;
            margin-bottom: 30px;
        }
        .brand-name {
            font-size: 2rem;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 4px;
            letter-spacing: -0.5px;
        }
        .brand-sub {
            color: #A0AEC0;
            font-size: 0.95rem;
            font-weight: 400;
        }

        /* Inputs (Nuclear Approach) */
        /* 1. Neutraliza TUDO o que o Streamlit tenta colocar nos elementos internos */
        div[data-testid="stTextInput"] * {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* 2. Transforma o contêiner PAI em nossa "Pílula" (Pill) */
        div[data-testid="stTextInput"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 9999px !important;
            padding: 8px 16px !important;
            transition: all 0.3s ease !important;
            overflow: hidden !important;
            margin-bottom: 16px !important;
        }

        /* 3. Estado :focus-within no contêiner PAI (isso reage perfeitamente ao clique no input) */
        div[data-testid="stTextInput"]:focus-within {
            border: 1px solid rgba(255, 255, 255, 0.6) !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
            box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.2) !important;
        }

        /* 4. Cor do texto digitado e do placeholder */
        div[data-testid="stTextInput"] input {
            color: #FFFFFF !important;
            font-size: 0.95rem !important;
            -webkit-text-fill-color: #FFFFFF !important;
            padding: 4px 0 !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #A0AEC0 !important;
            -webkit-text-fill-color: #A0AEC0 !important;
        }

        /* Primary Button */
        html body div.stApp section[data-testid="stMain"] div.stButton > button {
            background: linear-gradient(180deg, #FFFFFF 0%, #E2E8F0 100%) !important;
            color: #000000 !important;
            border-radius: 9999px !important;
            border: none !important;
            padding: 8px 24px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            box-shadow: 0 8px 20px rgba(255, 255, 255, 0.15) !important;
            transition: all 0.3s ease !important;
            height: 48px !important;
            margin-top: 8px !important;
        }
        html body div.stApp section[data-testid="stMain"] div.stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 24px rgba(255, 255, 255, 0.25) !important;
            background: linear-gradient(180deg, #F8FAFC 0%, #E2E8F0 100%) !important;
        }

        /* Error Pill */
        .custom-error-pill {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: #A0AEC0;
            padding: 12px;
            text-align: center;
            font-size: 0.9rem;
            margin-top: 0px;
            margin-bottom: 20px;
        }

        /* Version Info */
        .version-label-container {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
            width: 100%;
            z-index: 1;
        }
        .version-label {
            color: #718096;
            font-size: 0.8rem;
            letter-spacing: 0.5px;
        }
    </style>
    """


def _get_carousel_component_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

            * { margin: 0; padding: 0; box-sizing: border-box; }

            html, body {
                width: 100%;
                height: 100%;
                overflow: hidden;
                background: transparent;
                font-family: 'Inter', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #FFFFFF;
            }

            .carousel-container {
                width: 100%;
                position: relative;
                overflow: hidden;
            }

            .carousel-track {
                display: flex;
                transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                width: 300%;
            }

            .carousel-slide {
                width: 33.3333%;
                flex-shrink: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                padding: 0 20px;
            }

            .slide-icon {
                width: 72px;
                height: 72px;
                margin-bottom: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                filter: drop-shadow(0 0 16px rgba(255,255,255,0.4));
            }
            .slide-icon svg {
                width: 100%;
                height: 100%;
                fill: none;
                stroke: #FFFFFF;
                stroke-width: 1.5;
                stroke-linecap: round;
                stroke-linejoin: round;
            }

            .slide-title {
                font-size: 1.5rem;
                font-weight: 700;
                color: #FFFFFF;
                margin-bottom: 16px;
                line-height: 1.3;
            }

            .slide-desc {
                color: #A0AEC0;
                font-size: 0.95rem;
                line-height: 1.6;
                font-weight: 400;
            }

            .carousel-dots {
                display: flex;
                gap: 8px;
                justify-content: center;
                margin-top: 40px;
            }

            .c-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: rgba(255,255,255,0.3);
                cursor: pointer;
                transition: all 0.4s ease;
                border: none;
                display: inline-block;
            }
            .c-dot:hover { background: rgba(255,255,255,0.6); }
            .c-dot.active {
                background: #FFFFFF;
                width: 24px;
                border-radius: 4px;
                box-shadow: 0 0 8px rgba(255,255,255,0.8);
            }
            
            /* Slide specific animations */
            .carousel-slide { opacity: 0; animation: slideIn 0.7s ease-out 0.2s forwards; }
            @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        </style>
    </head>
    <body>
        <div class="carousel-container">
            <div class="carousel-track" id="carouselTrack">
                <!-- Slide 1 -->
                <div class="carousel-slide">
                    <div class="slide-icon">
                        <svg viewBox="0 0 24 24">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                    </div>
                    <div class="slide-title">Pergunte em<br>linguagem natural</div>
                    <div class="slide-desc">
                        Faça perguntas complexas sobre seus<br>
                        dados usando português simples. Nossa<br>
                        IA converte automaticamente em<br>
                        consultas SQL precisas.
                    </div>
                </div>
                <!-- Slide 2 -->
                <div class="carousel-slide">
                    <div class="slide-icon">
                        <svg viewBox="0 0 24 24">
                            <line x1="18" y1="20" x2="18" y2="10"></line>
                            <line x1="12" y1="20" x2="12" y2="4"></line>
                            <line x1="6" y1="20" x2="6" y2="14"></line>
                        </svg>
                    </div>
                    <div class="slide-title">Visualizações<br>inteligentes</div>
                    <div class="slide-desc">
                        Gere gráficos e dashboards<br>
                        automaticamente a partir das suas consultas.<br>
                        Explore tendências com facilidade.
                    </div>
                </div>
                <!-- Slide 3 -->
                <div class="carousel-slide">
                    <div class="slide-icon">
                        <svg viewBox="0 0 24 24">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                        </svg>
                    </div>
                    <div class="slide-title">Seguro e<br>integrado ao SAP</div>
                    <div class="slide-desc">
                        Conectado diretamente ao dicionário de<br>
                        dados SAP, com validação de esquemas e<br>
                        controle de acesso integrado.
                    </div>
                </div>
            </div>
            <div class="carousel-dots" id="carouselDots">
                <div class="c-dot active" onclick="goToSlide(0)"></div>
                <div class="c-dot" onclick="goToSlide(1)"></div>
                <div class="c-dot" onclick="goToSlide(2)"></div>
            </div>
        </div>

        <script>
            let currentSlide = 0;
            const totalSlides = 3;
            let autoplayTimer;

            function goToSlide(index) {
                currentSlide = index;
                const track = document.getElementById('carouselTrack');
                if (track) { track.style.transform = 'translateX(-' + (index * 33.3333) + '%)'; }
                
                const dots = document.querySelectorAll('.c-dot');
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active', i === index);
                });
                resetAutoplay();
            }

            function nextSlide() { goToSlide((currentSlide + 1) % totalSlides); }

            function resetAutoplay() {
                clearInterval(autoplayTimer);
                autoplayTimer = setInterval(nextSlide, 5000);
            }

            resetAutoplay();
        </script>
    </body>
    </html>
    """


def render():
    """Renderiza a tela de login com carrossel e formulário responsivo no estilo Glassmorphism."""

    auth_repository = AuthRepository()

    # ── CSS Login ──
    st.markdown(_get_login_page_css(), unsafe_allow_html=True)

    # ── Layout split ──
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        # Altura suficiente para mostrar todo o conteúdo e ícones
        components.html(_get_carousel_component_html(), height=450)

    with col_right:
        # Brand header
        st.markdown("""
        <div class="brand-section">
            <div class="brand-name">Ask My Data</div>
            <div class="brand-sub">Why not make it easy?</div>
        </div>
        """, unsafe_allow_html=True)

        # Campos do formulário
        st.text_input(
            "Usuário",
            placeholder="Digite seu usuário",
            label_visibility="collapsed",
            key="login_user",
        )

        st.text_input(
            "Senha",
            placeholder="Digite sua senha",
            type="password",
            label_visibility="collapsed",
            key="login_pass",
        )

        # Error placeholder
        error_container = st.empty()

        if st.button("Entrar", type="primary", use_container_width=True):
            username = st.session_state.get("login_user", "").strip()
            password = st.session_state.get("login_pass", "")

            if not username or not password:
                error_container.markdown('<div class="custom-error-pill">Informe usuário e senha.</div>', unsafe_allow_html=True)
            elif auth_repository.available:
                user = auth_repository.authenticate(username, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = user["username"]
                    st.session_state["current_user_display_name"] = user["display_name"]
                    st.rerun()
                else:
                    error_container.markdown('<div class="custom-error-pill">Usuário ou senha inválidos.</div>', unsafe_allow_html=True)
            else:
                error_container.markdown('<div class="custom-error-pill">MongoDB não configurado.</div>', unsafe_allow_html=True)

    # ── Version Label fora do card ──
    st.markdown(
        "<div class='version-label-container'><div class='version-label'>v1.0 - Powered by LangChain + ChromaDB</div></div>",
        unsafe_allow_html=True,
    )
