import streamlit as st
import pandas as pd
from database.models import buscar_produtos, listar_todos, listar_marcas, listar_categorias, listar_nomes_catalogo

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="Controle de Estoque",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
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

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #6C63FF 0%, #4834DF 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(108, 99, 255, 0.25);
    }
    .main-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
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
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(108, 99, 255, 0.15);
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

    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-natura {
        background: rgba(255, 107, 53, 0.15);
        color: #FF6B35;
    }
    .badge-boticario {
        background: rgba(0, 184, 148, 0.15);
        color: #00B894;
    }
    .badge-categoria {
        background: rgba(108, 99, 255, 0.15);
        color: #6C63FF;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #12141C;
    }

    /* Esconde o menu e footer do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>📦 Controle de Estoque</h1>
        <p>Pesquise e consulte seus produtos cadastrados</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Carregar opções de filtro ───────────────────────────────────────
try:
    marcas_disponiveis = listar_marcas()
    categorias_disponiveis = listar_categorias()
    nomes_catalogo = listar_nomes_catalogo()
except Exception as e:
    st.error(f"❌ Erro ao conectar com o banco de dados.\n\n`{e}`")
    st.stop()

# ── Barra de pesquisa e filtros ─────────────────────────────────────
col_search, col_marca, col_categoria = st.columns([3, 1.5, 1.5])
with col_search:
    filtro_nome = st.selectbox(
        "📝 Nome do produto",
        options=["Todos"] + nomes_catalogo,
        key="search_input",
    )
    termo_pesquisa = filtro_nome if filtro_nome != "Todos" else ""
with col_marca:
    filtro_marca = st.selectbox(
        "🏷️ Marca",
        options=["Todas"] + marcas_disponiveis,
        key="filtro_marca",
    )
with col_categoria:
    filtro_categoria = st.selectbox(
        "📂 Categoria",
        options=["Todas"] + categorias_disponiveis,
        key="filtro_categoria",
    )

# ── Buscar dados ────────────────────────────────────────────────────
marca_filter = filtro_marca if filtro_marca != "Todas" else None
categoria_filter = filtro_categoria if filtro_categoria != "Todas" else None

try:
    if termo_pesquisa or marca_filter or categoria_filter:
        produtos = buscar_produtos(
            termo=termo_pesquisa,
            marca=marca_filter,
            categoria=categoria_filter,
        )
    else:
        produtos = listar_todos()
except Exception as e:
    st.error(
        f"❌ Erro ao buscar produtos.\n\n`{e}`"
    )
    st.stop()

# ── Métricas resumo ─────────────────────────────────────────────────
total_produtos = len(produtos)

if total_produtos > 0:
    df = pd.DataFrame(produtos)

    # Calcular margem
    df["margem_pct"] = ((df["preco_revenda"] - df["preco_compra"]) / df["preco_compra"] * 100).round(1)
    margem_media = df["margem_pct"].mean()
    ticket_medio_revenda = df["preco_revenda"].mean()
    total_itens = int(df["quantidade"].sum()) if "quantidade" in df.columns else total_produtos

    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="value">{total_produtos}</div>
                <div class="label">{"Entrada" if total_produtos == 1 else "Entradas"}</div>
            </div>
            <div class="metric-card">
                <div class="value">{total_itens}</div>
                <div class="label">Itens registrados</div>
            </div>
            <div class="metric-card">
                <div class="value">{margem_media:.1f}%</div>
                <div class="label">Margem média</div>
            </div>
            <div class="metric-card">
                <div class="value">R$ {ticket_medio_revenda:,.2f}</div>
                <div class="label">Preço médio de revenda</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Lista de produtos ───────────────────────────────────────────
    st.markdown("#### 📋 Produtos")

    for produto in produtos:
        marca = produto.get("marca", "—")
        categoria = produto.get("categoria") or "—"
        quantidade = produto.get("quantidade", 1) or 1
        data_utc = pd.to_datetime(produto["data_cadastro"], utc=True)
        data = (data_utc - pd.Timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")
        margem = ((produto["preco_revenda"] - produto["preco_compra"]) / produto["preco_compra"] * 100)

        # Badge de marca
        badge_class = "badge-natura" if marca == "Natura" else "badge-boticario"

        col_info, col_precos = st.columns([3, 4])

        with col_info:
            badges_html = f'<span class="badge {badge_class}">{marca}</span>'
            if categoria != "—":
                badges_html += f' <span class="badge badge-categoria">{categoria}</span>'
            st.markdown(
                f"""
                <div style="padding: 0.3rem 0;">
                    <div style="font-weight: 600; font-size: 1.05rem; margin-bottom: 0.3rem;">
                        {quantidade}x {produto["nome"]}
                    </div>
                    <div>{badges_html}</div>
                    <div style="color: #666; font-size: 0.8rem; margin-top: 0.3rem;">📅 {data}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_precos:
            cor_margem = "#00B894" if margem > 0 else "#FF6B6B"
            st.markdown(
                f"""
                <div style="padding: 0.3rem 0; display: flex; gap: 2rem; align-items: center; height: 100%;">
                    <div>
                        <div style="color: #888; font-size: 0.75rem;">COMPRA</div>
                        <div style="font-weight: 600;">R$ {produto["preco_compra"]:,.2f}</div>
                    </div>
                    <div>
                        <div style="color: #888; font-size: 0.75rem;">REVENDA</div>
                        <div style="font-weight: 600;">R$ {produto["preco_revenda"]:,.2f}</div>
                    </div>
                    <div>
                        <div style="color: #888; font-size: 0.75rem;">MARGEM</div>
                        <div style="font-weight: 700; color: {cor_margem};">{margem:.1f}%</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

else:
    if termo_pesquisa or marca_filter or categoria_filter:
        st.info("🔍 Nenhum produto encontrado com os filtros selecionados.")
    else:
        st.info("📋 Nenhum produto cadastrado ainda. Vá até **Cadastro** no menu lateral para adicionar.")

# ── Sidebar info ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📦 Estoque App")
    st.markdown("---")
    st.markdown(
        """
        **Navegação:**
        - 🏠 **Início** — Pesquisa
        - ➕ **Cadastro** — Nova entrada
        - ⚙️ **Gerenciar** — Configurações
        - 📊 **Dashboard** — Gráficos
        - 📦 **Estoque** — Controle atual
        """
    )
    st.markdown("---")
    st.caption("v2.2 • Controle de Estoque")
