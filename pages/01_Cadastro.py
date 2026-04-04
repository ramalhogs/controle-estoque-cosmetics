import streamlit as st
from database.models import (
    adicionar_produto,
    listar_marcas,
    listar_categorias,
    listar_nomes_catalogo,
    adicionar_ao_catalogo,
)

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="Cadastro de Produto",
    page_icon="➕",
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

    .form-header {
        background: linear-gradient(135deg, #00B894 0%, #00A381 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 184, 148, 0.25);
    }
    .form-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .form-header p {
        color: rgba(255,255,255,0.8);
        font-size: 1.05rem;
        margin: 0.3rem 0 0 0;
    }

    .success-box {
        background: rgba(0, 184, 148, 0.1);
        border: 1px solid rgba(0, 184, 148, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .success-box h3 {
        color: #00B894;
        margin: 0 0 0.5rem 0;
    }

    .preview-card {
        background: #1A1D29;
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .preview-card .label {
        color: #888;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .preview-card .value {
        color: #FAFAFA;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .preview-card .margem {
        color: #6C63FF;
        font-size: 1.3rem;
        font-weight: 700;
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
    <div class="form-header">
        <h1>➕ Cadastro de Entrada</h1>
        <p>Registre uma compra de produto com quantidade e preços</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Carregar opções do banco ────────────────────────────────────────
try:
    marcas_disponiveis = listar_marcas()
    categorias_disponiveis = listar_categorias()
    produtos_catalogo = listar_nomes_catalogo()
except Exception as e:
    st.error(f"❌ Erro ao carregar opções do banco.\n\n`{e}`")
    st.stop()

if not marcas_disponiveis:
    st.warning("⚠️ Nenhuma marca cadastrada. Vá em **Gerenciar** para adicionar marcas.")
    st.stop()

# ── Seleção de produto ──────────────────────────────────────────────
OPCAO_NOVO = "➕ Criar novo produto..."
opcoes_produto = produtos_catalogo + [OPCAO_NOVO]

produto_selecionado = st.selectbox(
    "📦 Produto",
    options=opcoes_produto,
    key="produto_select",
    help="Selecione um produto existente ou crie um novo",
)

# Se "Criar novo", mostrar campo de texto
nome_novo_produto = None
if produto_selecionado == OPCAO_NOVO:
    nome_novo_produto = st.text_input(
        "📝 Nome do novo produto",
        placeholder="Ex: Desodorante Roll-on Kaiak",
        key="novo_produto_input",
    )

# ── Formulário ──────────────────────────────────────────────────────
with st.form("form_cadastro", clear_on_submit=True):
    col_marca, col_categoria = st.columns(2)
    with col_marca:
        marca = st.selectbox(
            "🏷️ Marca *",
            options=marcas_disponiveis,
            key="marca_input",
        )
    with col_categoria:
        categoria = st.selectbox(
            "📂 Categoria (opcional)",
            options=["— Nenhuma —"] + categorias_disponiveis,
            key="categoria_input",
        )

    col_qty, col_compra, col_revenda = st.columns([1, 1.5, 1.5])
    with col_qty:
        quantidade_str = st.text_input(
            "📊 Quantidade",
            placeholder="Ex: 5",
            key="quantidade_input",
        )
    with col_compra:
        preco_compra_str = st.text_input(
            "💰 Preço de Compra (R$)",
            placeholder="Ex: 25.90",
            key="preco_compra_input",
        )
    with col_revenda:
        preco_revenda_str = st.text_input(
            "💵 Preço de Revenda (R$)",
            placeholder="Ex: 49.90",
            key="preco_revenda_input",
        )

    # Tentar converter para preview
    try:
        preco_compra = float(preco_compra_str.replace(",", ".")) if preco_compra_str else 0.0
    except ValueError:
        preco_compra = 0.0
    try:
        preco_revenda = float(preco_revenda_str.replace(",", ".")) if preco_revenda_str else 0.0
    except ValueError:
        preco_revenda = 0.0
    try:
        quantidade = int(quantidade_str) if quantidade_str else 0
    except ValueError:
        quantidade = 0

    # Preview
    if preco_compra > 0 and preco_revenda > 0:
        margem = ((preco_revenda - preco_compra) / preco_compra) * 100
        lucro = preco_revenda - preco_compra
        lucro_total = lucro * max(quantidade, 1)
        cor_margem = "#00B894" if margem > 0 else "#FF6B6B"

        st.markdown(
            f"""
            <div class="preview-card">
                <div class="label">Preview</div>
                <div style="display: flex; justify-content: space-around; text-align: center;">
                    <div>
                        <div class="label">Lucro por unidade</div>
                        <div class="value" style="color: {cor_margem}">R$ {lucro:,.2f}</div>
                    </div>
                    <div>
                        <div class="label">Lucro total ({max(quantidade, 1)} un.)</div>
                        <div class="value" style="color: {cor_margem}">R$ {lucro_total:,.2f}</div>
                    </div>
                    <div>
                        <div class="label">Margem</div>
                        <div class="margem" style="color: {cor_margem}">{margem:.1f}%</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    submitted = st.form_submit_button(
        "✅ Registrar Entrada",
        use_container_width=True,
        type="primary",
    )

# ── Processamento ───────────────────────────────────────────────────
if submitted:
    cat_value = categoria if categoria != "— Nenhuma —" else None

    # Determinar nome do produto
    if produto_selecionado == OPCAO_NOVO:
        nome_final = nome_novo_produto
    else:
        nome_final = produto_selecionado

    # Converter preços
    try:
        preco_compra = float(preco_compra_str.replace(",", ".")) if preco_compra_str else 0.0
    except ValueError:
        preco_compra = -1
    try:
        preco_revenda = float(preco_revenda_str.replace(",", ".")) if preco_revenda_str else 0.0
    except ValueError:
        preco_revenda = -1
    try:
        quantidade = int(quantidade_str) if quantidade_str else 0
    except ValueError:
        quantidade = 0

    # Validações
    if not nome_final or not nome_final.strip():
        st.error("❌ O nome do produto é obrigatório.")
    elif quantidade <= 0:
        st.error("❌ A quantidade deve ser maior que zero.")
    elif preco_compra <= 0:
        st.error("❌ O preço de compra deve ser um número válido maior que zero. Ex: 25.90")
    elif preco_revenda <= 0:
        st.error("❌ O preço de revenda deve ser um número válido maior que zero. Ex: 49.90")
    else:
        try:
            # Se é produto novo, criar no catálogo primeiro
            if produto_selecionado == OPCAO_NOVO:
                adicionar_ao_catalogo(nome_final)

            produto = adicionar_produto(
                nome=nome_final,
                preco_compra=preco_compra,
                preco_revenda=preco_revenda,
                marca=marca,
                quantidade=quantidade,
                categoria=cat_value,
            )
            margem_final = ((preco_revenda - preco_compra) / preco_compra) * 100
            cat_display = cat_value or "—"

            st.markdown(
                f"""
                <div class="success-box">
                    <h3>✅ Entrada registrada com sucesso!</h3>
                    <p>
                        <strong>{quantidade}x {nome_final.strip()}</strong> ({marca})<br>
                        Categoria: {cat_display}<br>
                        Compra: R$ {preco_compra:,.2f} &nbsp;|&nbsp;
                        Revenda: R$ {preco_revenda:,.2f} &nbsp;|&nbsp;
                        Margem: {margem_final:.1f}%
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        except Exception as e:
            error_msg = str(e)
            if "duplicate key" in error_msg.lower() or "unique" in error_msg.lower():
                st.error("❌ Esse produto já existe no catálogo. Selecione-o na lista.")
            else:
                st.error(f"❌ Erro ao registrar entrada: `{e}`")

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
