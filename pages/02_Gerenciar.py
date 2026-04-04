import streamlit as st
from database.models import (
    listar_todos,
    deletar_produto,
    renomear_produto,
    listar_marcas_completo,
    adicionar_marca,
    deletar_marca,
    listar_categorias_completo,
    adicionar_categoria,
    deletar_categoria,
)
import pandas as pd

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="Gerenciar",
    page_icon="⚙️",
    layout="centered",
)

from auth import verificar_senha
if not verificar_senha():
    st.stop()

# ── CSS customizado ─────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .manage-header {
        background: linear-gradient(135deg, #E17055 0%, #D63031 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(214, 48, 49, 0.25);
    }
    .manage-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .manage-header p {
        color: rgba(255,255,255,0.8);
        font-size: 1.05rem;
        margin: 0.3rem 0 0 0;
    }

    .item-row {
        background: #1A1D29;
        border: 1px solid rgba(108, 99, 255, 0.12);
        border-radius: 10px;
        padding: 0.7rem 1.2rem;
        margin-bottom: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .item-name {
        font-weight: 500;
        font-size: 1rem;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="manage-header">
        <h1>⚙️ Gerenciar</h1>
        <p>Gerencie marcas, categorias e exclua produtos</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Abas ────────────────────────────────────────────────────────────
tab_produtos, tab_marcas, tab_categorias = st.tabs(
    ["🗑️ Excluir Produtos", "🏷️ Marcas", "📂 Categorias"]
)

# ═══════════════════════════════════════════════════════════════════
#  ABA: EXCLUIR PRODUTOS
# ═══════════════════════════════════════════════════════════════════
with tab_produtos:
    try:
        produtos = listar_todos()
    except Exception as e:
        st.error(f"❌ Erro ao carregar produtos.\n\n`{e}`")
        produtos = []

    if not produtos:
        st.info("📋 Nenhum produto cadastrado.")
    else:
        st.markdown(f"**{len(produtos)}** produto(s) cadastrado(s)")
        st.markdown("")

        for produto in produtos:
            marca = produto.get("marca", "—")
            categoria = produto.get("categoria") or "—"
            data_utc = pd.to_datetime(produto["data_cadastro"], utc=True)
            data = (data_utc - pd.Timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")

            col_name, col_details, col_edit, col_btn = st.columns([3, 4, 0.7, 0.7])

            with col_name:
                st.markdown(f"**{produto['nome']}**")
                st.caption(f"{marca} • {categoria}")

            with col_details:
                st.markdown(
                    f'<span style="color: #888; font-size: 0.85rem;">'
                    f"Compra: R\\$ {produto['preco_compra']:,.2f} | "
                    f"Revenda: R\\$ {produto['preco_revenda']:,.2f} | "
                    f"{data}"
                    f"</span>",
                    unsafe_allow_html=True,
                )

            with col_edit:
                with st.popover("✏️", help="Renomear produto"):
                    novo_nome = st.text_input(
                        "Novo nome",
                        value=produto["nome"],
                        key=f"rename_{produto['id']}",
                    )
                    if st.button("Salvar", key=f"save_rename_{produto['id']}", use_container_width=True):
                        if novo_nome and novo_nome.strip() and novo_nome.strip() != produto["nome"]:
                            try:
                                renomear_produto(produto["nome"], novo_nome)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: `{e}`")

            with col_btn:
                if st.button("🗑️", key=f"del_prod_{produto['id']}", help="Excluir"):
                    st.session_state[f"confirm_del_prod_{produto['id']}"] = True

            # Confirmação
            if st.session_state.get(f"confirm_del_prod_{produto['id']}", False):
                st.warning(f"⚠️ Excluir **{produto['nome']}**?")
                col_yes, col_no, _ = st.columns([1, 1, 6])
                with col_yes:
                    if st.button("✅ Sim", key=f"yes_prod_{produto['id']}"):
                        try:
                            deletar_produto(produto["id"])
                            del st.session_state[f"confirm_del_prod_{produto['id']}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: `{e}`")
                with col_no:
                    if st.button("❌ Não", key=f"no_prod_{produto['id']}"):
                        del st.session_state[f"confirm_del_prod_{produto['id']}"]
                        st.rerun()

            st.divider()

# ═══════════════════════════════════════════════════════════════════
#  ABA: MARCAS
# ═══════════════════════════════════════════════════════════════════
with tab_marcas:
    # Adicionar nova marca
    st.markdown("##### ➕ Adicionar marca")
    with st.form("form_marca", clear_on_submit=True):
        col_input, col_submit = st.columns([3, 1])
        with col_input:
            nova_marca = st.text_input(
                "Nome da marca",
                placeholder="Ex: Eudora",
                label_visibility="collapsed",
            )
        with col_submit:
            submit_marca = st.form_submit_button("Adicionar", use_container_width=True)

    if submit_marca:
        if not nova_marca or not nova_marca.strip():
            st.error("❌ Informe o nome da marca.")
        else:
            try:
                adicionar_marca(nova_marca)
                st.success(f"✅ Marca **{nova_marca.strip()}** adicionada!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao adicionar marca: `{e}`")

    # Listar marcas existentes
    st.markdown("##### 📋 Marcas cadastradas")
    try:
        marcas = listar_marcas_completo()
    except Exception as e:
        st.error(f"❌ Erro ao carregar marcas.\n\n`{e}`")
        marcas = []

    if not marcas:
        st.info("Nenhuma marca cadastrada.")
    else:
        for marca in marcas:
            col_name, col_btn = st.columns([5, 1])
            with col_name:
                st.markdown(f"**{marca['nome']}**")
            with col_btn:
                if st.button("🗑️", key=f"del_marca_{marca['id']}", help="Excluir marca"):
                    st.session_state[f"confirm_del_marca_{marca['id']}"] = True

            if st.session_state.get(f"confirm_del_marca_{marca['id']}", False):
                st.warning(f"⚠️ Excluir marca **{marca['nome']}**? Produtos com essa marca não serão afetados.")
                col_yes, col_no, _ = st.columns([1, 1, 6])
                with col_yes:
                    if st.button("✅ Sim", key=f"yes_marca_{marca['id']}"):
                        try:
                            deletar_marca(marca["id"])
                            del st.session_state[f"confirm_del_marca_{marca['id']}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: `{e}`")
                with col_no:
                    if st.button("❌ Não", key=f"no_marca_{marca['id']}"):
                        del st.session_state[f"confirm_del_marca_{marca['id']}"]
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════
#  ABA: CATEGORIAS
# ═══════════════════════════════════════════════════════════════════
with tab_categorias:
    # Adicionar nova categoria
    st.markdown("##### ➕ Adicionar categoria")
    with st.form("form_categoria", clear_on_submit=True):
        col_input, col_submit = st.columns([3, 1])
        with col_input:
            nova_categoria = st.text_input(
                "Nome da categoria",
                placeholder="Ex: Perfumes",
                label_visibility="collapsed",
            )
        with col_submit:
            submit_cat = st.form_submit_button("Adicionar", use_container_width=True)

    if submit_cat:
        if not nova_categoria or not nova_categoria.strip():
            st.error("❌ Informe o nome da categoria.")
        else:
            try:
                adicionar_categoria(nova_categoria)
                st.success(f"✅ Categoria **{nova_categoria.strip()}** adicionada!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao adicionar categoria: `{e}`")

    # Listar categorias existentes
    st.markdown("##### 📋 Categorias cadastradas")
    try:
        categorias = listar_categorias_completo()
    except Exception as e:
        st.error(f"❌ Erro ao carregar categorias.\n\n`{e}`")
        categorias = []

    if not categorias:
        st.info("Nenhuma categoria cadastrada.")
    else:
        for cat in categorias:
            col_name, col_btn = st.columns([5, 1])
            with col_name:
                st.markdown(f"**{cat['nome']}**")
            with col_btn:
                if st.button("🗑️", key=f"del_cat_{cat['id']}", help="Excluir categoria"):
                    st.session_state[f"confirm_del_cat_{cat['id']}"] = True

            if st.session_state.get(f"confirm_del_cat_{cat['id']}", False):
                st.warning(f"⚠️ Excluir categoria **{cat['nome']}**? Produtos com essa categoria não serão afetados.")
                col_yes, col_no, _ = st.columns([1, 1, 6])
                with col_yes:
                    if st.button("✅ Sim", key=f"yes_cat_{cat['id']}"):
                        try:
                            deletar_categoria(cat["id"])
                            del st.session_state[f"confirm_del_cat_{cat['id']}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: `{e}`")
                with col_no:
                    if st.button("❌ Não", key=f"no_cat_{cat['id']}"):
                        del st.session_state[f"confirm_del_cat_{cat['id']}"]
                        st.rerun()

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📦 Estoque App")
    st.markdown("---")
    st.markdown(
        """
        **Navegação:**
        - 🏠 **Início** — Pesquisa
        - ➕ **Cadastro** — Nova entrada
        - 📊 **Dashboard** — Gráficos
        - 📦 **Estoque** — Controle atual
        - ⚙️ **Gerenciar** — Configurações
        """
    )
    st.markdown("---")
    st.caption("v2.2 • Controle de Estoque")

