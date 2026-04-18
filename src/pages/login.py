import streamlit as st
import streamlit.components.v1 as components
from src.styles import get_global_css


def _get_login_page_css():
    """CSS da página de login — responsivo para todas as telas."""
    return """
    <style>
        /* ── Reset Streamlit chrome ── */
        header {visibility: hidden !important; height: 0 !important; position: absolute !important;}
        [data-testid="stSidebar"] {display: none !important;}
        [data-testid="collapsedControl"] {display: none !important;}
        footer {display: none !important;}

        [data-testid="stMainBlockContainer"] {
            padding: 0 !important;
            max-width: 100% !important;
        }
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Layout Base e Desktop ── */
        [data-testid="stHorizontalBlock"] {
            gap: 0 !important;
            align-items: stretch !important;
        }

        /* ── TELA PEQUENA (MOBILE) ── */
        @media (max-width: 768px) {
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                flex-wrap: nowrap !important;
                min-height: 100vh !important;
            }
            
            /* Esconder Carrossel no celular */
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {
                display: none !important;
            }

            /* Login centralizado, ocupando toda tela sem scroll */
            [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
                width: 100% !important;
                min-height: 100vh !important;
                flex: 1 1 100% !important;
                display: flex !important; flex-direction: column !important; justify-content: center !important; align-items: center !important;
                padding: 32px !important;
            }

            .desktop-spacer { display: none !important; }
            .mobile-spacer { height: 8px; }
            .brand-section { margin-bottom: 24px; }
            .version-label { margin-top: 24px; }
            
            /* Compacta inputs no mobile */
            div[data-testid="stTextInput"] {
                margin-bottom: -10px !important;
            }

            /* Move o brilho de fundo para não interferir na legibilidade */
            .glow-bg-right {
                top: 70% !important;
                width: 250px !important;
                height: 250px !important;
            }
        }

        /* ── Elementos Estéticos ── */
        .desktop-spacer { height: 10vh; }
        
        .glow-bg-right {
            position: fixed;
            top: 10%;
            right: 0;
            width: 400px;
            height: 400px;
            background: radial-gradient(ellipse, rgba(59,130,246,0.06) 0%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }

        .brand-section {
            text-align: center;
            margin-bottom: 36px;
            animation: fadeSlideUp 0.8s ease-out forwards;
            width: 100%;
        }

        @keyframes fadeSlideUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .brand-icon {
            width: 56px; height: 56px;
            border-radius: 16px;
            background: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #D946EF 100%);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 8px 30px rgba(59,130,246,0.25);
        }

        .brand-name {
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #D946EF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .brand-sub {
            color: #475569;
            font-size: 0.88rem;
            font-weight: 400;
        }

        .login-divider {
            max-width: 380px;
            margin: 0 auto 8px;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
        }

        .version-label {
            text-align: center;
            margin-top: 28px;
            color: #334155;
            font-size: 0.75rem;
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
            }

            body {
                font-family: 'Inter', sans-serif;
                background: transparent;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #E2E8F0;
            }

            .carousel-container {
                width: 100%;
                max-width: 90%;
                padding: 0 clamp(12px, 3vw, 48px);
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
                padding: 0 clamp(8px, 2vw, 24px);
            }

            .slide-icon {
                width: clamp(56px, 8vw, 110px);
                height: clamp(56px, 8vw, 110px);
                border-radius: clamp(16px, 2.5vw, 28px);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: clamp(1.4rem, 3vw, 3rem);
                margin-bottom: clamp(16px, 3vh, 40px);
                position: relative;
                flex-shrink: 0;
            }
            .slide-icon::after {
                content: '';
                position: absolute;
                inset: -6px;
                border-radius: clamp(20px, 3vw, 32px);
                z-index: -1;
            }

            .slide-icon.icon-blue { background: linear-gradient(135deg, #2563EB, #3B82F6); box-shadow: 0 8px 30px rgba(37,99,235,0.3); }
            .slide-icon.icon-purple { background: linear-gradient(135deg, #7C3AED, #8B5CF6); box-shadow: 0 8px 30px rgba(124,58,237,0.3); }
            .slide-icon.icon-pink { background: linear-gradient(135deg, #DB2777, #D946EF); box-shadow: 0 8px 30px rgba(219,39,119,0.3); }

            .slide-title {
                font-size: clamp(1.1rem, 2.5vw, 2.2rem);
                font-weight: 700;
                color: #F1F5F9;
                margin-bottom: clamp(8px, 1.5vh, 18px);
                letter-spacing: -0.5px;
                line-height: 1.2;
            }

            .slide-desc {
                color: #94A3B8;
                font-size: clamp(0.8rem, 1.2vw, 1.1rem);
                line-height: 1.7;
                max-width: 90%;
            }

            .carousel-dots {
                display: flex;
                gap: clamp(6px, 1vw, 12px);
                justify-content: center;
                margin-top: clamp(24px, 4vh, 56px);
            }

            .c-dot {
                width: clamp(8px, 1vw, 12px);
                height: clamp(8px, 1vw, 12px);
                border-radius: 50%;
                background: rgba(255,255,255,0.12);
                cursor: pointer;
                transition: all 0.4s ease;
                border: none;
                display: inline-block;
            }
            .c-dot:hover { background: rgba(255,255,255,0.25); }
            .c-dot.active {
                background: #3B82F6;
                box-shadow: 0 0 12px rgba(59,130,246,0.5);
                width: clamp(20px, 3vw, 36px);
                border-radius: 6px;
            }

            .carousel-progress {
                width: 100%;
                max-width: clamp(120px, 20vw, 280px);
                height: 2px;
                background: rgba(255,255,255,0.06);
                border-radius: 2px;
                margin: clamp(12px, 2vh, 28px) auto 0;
                overflow: hidden;
            }
            .carousel-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #3B82F6, #8B5CF6);
                border-radius: 2px;
                width: 0%;
                animation: progressFill 4.5s linear infinite;
            }
            @keyframes progressFill {
                from { width: 0%; }
                to { width: 100%; }
            }

            .carousel-slide { opacity: 0; animation: slideIn 0.7s ease-out 0.2s forwards; }
            @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        </style>
    </head>
    <body>
        <div class="carousel-container">
            <div class="carousel-track" id="carouselTrack">
                <div class="carousel-slide">
                    <div class="slide-icon icon-blue">💬</div>
                    <div class="slide-title">Pergunte em linguagem natural</div>
                    <div class="slide-desc">
                        Faça perguntas complexas sobre seus dados usando português simples. 
                        Nossa IA converte automaticamente em consultas SQL precisas.
                    </div>
                </div>
                <div class="carousel-slide">
                    <div class="slide-icon icon-purple">📊</div>
                    <div class="slide-title">Visualizações inteligentes</div>
                    <div class="slide-desc">
                        Gere gráficos e dashboards automaticamente a partir das suas consultas. 
                        Explore tendências e padrões com facilidade.
                    </div>
                </div>
                <div class="carousel-slide">
                    <div class="slide-icon icon-pink">🔒</div>
                    <div class="slide-title">Seguro e integrado ao SAP</div>
                    <div class="slide-desc">
                        Conectado diretamente ao dicionário de dados SAP, com validação de 
                        esquemas e controle de acesso integrado.
                    </div>
                </div>
            </div>
            <div class="carousel-dots" id="carouselDots">
                <div class="c-dot active" onclick="goToSlide(0)"></div>
                <div class="c-dot" onclick="goToSlide(1)"></div>
                <div class="c-dot" onclick="goToSlide(2)"></div>
            </div>
            <div class="carousel-progress">
                <div class="carousel-progress-bar" id="progressBar"></div>
            </div>
        </div>

        <script>
            let currentSlide = 0;
            const totalSlides = 3;
            let autoplayTimer;
            const progressBar = document.getElementById('progressBar');

            function goToSlide(index) {
                currentSlide = index;
                const track = document.getElementById('carouselTrack');
                if (track) { track.style.transform = 'translateX(-' + (index * 33.3333) + '%)'; }
                
                const dots = document.querySelectorAll('.c-dot');
                dots.forEach((dot, i) => {
                    dot.classList.toggle('active', i === index);
                });
                
                if (progressBar) {
                    progressBar.style.animation = 'none';
                    progressBar.offsetHeight;
                    progressBar.style.animation = 'progressFill 4.5s linear infinite';
                }
                resetAutoplay();
            }

            function nextSlide() { goToSlide((currentSlide + 1) % totalSlides); }

            function resetAutoplay() {
                clearInterval(autoplayTimer);
                autoplayTimer = setInterval(nextSlide, 4500);
            }

            function sendHeight() {
                const h = document.body.scrollHeight;
                window.parent.postMessage({type: 'setFrameHeight', height: h}, '*');
            }

            resetAutoplay();
            window.addEventListener('load', sendHeight);
            window.addEventListener('resize', sendHeight);
        </script>
    </body>
    </html>
    """


def _get_brand_header():
    """HTML do cabeçalho da marca no painel de login."""
    return """
    <div class="brand-section">
        <div class="brand-icon">✦</div>
        <div class="brand-name">Ask My Data</div>
        <div class="brand-sub">Why not make it easy?</div>
    </div>
    <div class="login-divider"></div>
    """


def render():
    """Renderiza a tela de login com carrossel e formulário responsivo."""

    # ── CSS Global + Login ──
    st.markdown(get_global_css(), unsafe_allow_html=True)
    st.markdown(_get_login_page_css(), unsafe_allow_html=True)
    st.markdown('<div class="glow-bg-right"></div>', unsafe_allow_html=True)

    # ── Layout split ──
    col_left, col_right = st.columns([1.3, 0.7], gap="small")

    with col_left:
        # Altura declarada de 700px no desktop, mas sobrescrita pelo CSS para 380px no mobile
        components.html(
            _get_carousel_component_html(),
            height=700,
            scrolling=False,
        )

    with col_right:
        # Espaçamento gerenciado por CSS para não criar um buraco negro no celular
        st.markdown("<div class='desktop-spacer'></div>", unsafe_allow_html=True)

        # Brand header
        st.markdown(_get_brand_header(), unsafe_allow_html=True)

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

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

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.button("Entrar", type="primary", use_container_width=True):
            st.session_state["logged_in"] = True
            st.rerun()

        st.markdown(
            "<div class='version-label'>"
            "v1.0 · Powered by LangChain + ChromaDB"
            "</div>",
            unsafe_allow_html=True,
        )
        