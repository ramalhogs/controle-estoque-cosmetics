import streamlit as st
from database.models import listar_catalogo, listar_todos, atualizar_estoque, ajustar_estoque

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="Estoque",
    page_icon="📦",
    layout="wide",
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

    .stock-header {
        background: linear-gradient(135deg, #0984E3 0%, #6C5CE7 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(9, 132, 227, 0.25);
    }
    .stock-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .stock-header p {
        color: rgba(255,255,255,0.8);
        font-size: 1.05rem;
        margin: 0.3rem 0 0 0;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #1A1D29;
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        flex: 1;
        text-align: center;
    }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #6C63FF;
    }
    .metric-card .label {
        font-size: 0.85rem;
        color: #888;
        margin-top: 0.25rem;
    }

    /* Stock level indicators */
    .stock-high { color: #00B894; }
    .stock-medium { color: #FDCB6E; }
    .stock-low { color: #FF6B6B; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="stock-header">
        <h1>📦 Controle de Estoque</h1>
        <p>Visualize e ajuste as quantidades em estoque</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Carregar catálogo ───────────────────────────────────────────────
try:
    catalogo_completo = listar_catalogo()
    entradas = listar_todos()
    # Filtrar: só mostrar produtos que têm entradas registradas
    nomes_com_entradas = {e["nome"] for e in entradas}
    catalogo = [p for p in catalogo_completo if p["nome"] in nomes_com_entradas]
except Exception as e:
    st.error(f"❌ Erro ao carregar catálogo.\n\n`{e}`")
    st.stop()

if not catalogo:
    st.info("📋 Nenhum produto com entradas registradas. Adicione produtos pela página de **Cadastro**.")
    st.stop()

# ── Métricas ────────────────────────────────────────────────────────
total_produtos = len(catalogo)
total_estoque = sum(p.get("estoque_atual", 0) or 0 for p in catalogo)
zerados = sum(1 for p in catalogo if (p.get("estoque_atual", 0) or 0) == 0)

st.markdown(
    f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="value">{total_produtos}</div>
            <div class="label">Produtos no catálogo</div>
        </div>
        <div class="metric-card">
            <div class="value">{total_estoque}</div>
            <div class="label">Total de itens em estoque</div>
        </div>
        <div class="metric-card">
            <div class="value" style="color: {'#FF6B6B' if zerados > 0 else '#00B894'}">{zerados}</div>
            <div class="label">Produtos sem estoque</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Lista de produtos ──────────────────────────────────────────────
st.markdown("#### 📦 Produtos em estoque")
st.caption("Use os botões ➖/➕ para ajuste rápido ou digite um valor exato.")
st.markdown("")

for produto in catalogo:
    nome = produto["nome"]
    estoque = produto.get("estoque_atual", 0) or 0

    # Cor do indicador
    if estoque > 5:
        cor_hex = "#00B894"
    elif estoque > 0:
        cor_hex = "#FDCB6E"
    else:
        cor_hex = "#FF6B6B"

    col_name, col_stock, col_minus, col_plus, col_set = st.columns([3, 1.5, 0.7, 0.7, 1.5])

    with col_name:
        st.markdown(f"**{nome}**")

    with col_stock:
        st.markdown(
            f'<div style="font-size: 1.4rem; font-weight: 700; color: {cor_hex}; text-align: center; padding-top: 0.2rem;">{estoque}</div>',
            unsafe_allow_html=True,
        )

    with col_minus:
        if st.button("➖", key=f"minus_{produto['id']}", help="Diminuir 1"):
            if estoque > 0:
                ajustar_estoque(nome, -1)
                st.rerun()

    with col_plus:
        if st.button("➕", key=f"plus_{produto['id']}", help="Aumentar 1"):
            ajustar_estoque(nome, 1)
            st.rerun()

    with col_set:
        with st.popover("✏️ Definir"):
            novo_valor = st.number_input(
                f"Estoque de {nome}",
                min_value=0,
                value=estoque,
                step=1,
                key=f"set_{produto['id']}",
            )
            if st.button("Salvar", key=f"save_{produto['id']}", use_container_width=True):
                atualizar_estoque(nome, novo_valor)
                st.rerun()

    st.divider()

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
