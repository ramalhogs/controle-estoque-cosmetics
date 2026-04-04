import streamlit as st


def verificar_senha() -> bool:
    """Verifica se o usuário digitou a senha correta.

    A senha é definida em st.secrets["app"]["senha"].
    Retorna True se autenticado, False se não.
    """
    # Se já autenticou nesta sessão, pula
    if st.session_state.get("autenticado", False):
        return True

    # Tela de login
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown(
            """
            <div style="text-align: center; padding: 3rem 0 1rem 0;">
                <div style="font-size: 4rem;">📦</div>
                <h1 style="margin: 0.5rem 0; font-size: 1.8rem;">Controle de Estoque</h1>
                <p style="color: #888;">Digite a senha para acessar</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            senha_digitada = st.text_input(
                "🔒 Senha",
                type="password",
                placeholder="Digite a senha...",
            )
            submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")

        if submitted:
            senha_correta = st.secrets.get("app", {}).get("senha", "")
            if senha_digitada == senha_correta:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ Senha incorreta.")

    return False
