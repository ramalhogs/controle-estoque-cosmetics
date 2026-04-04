import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.models import (
    listar_todos,
    listar_catalogo,
    listar_marcas,
    listar_categorias,
    atualizar_estoque,
    ajustar_estoque,
)

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── CSS customizado ─────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .dash-header {
        background: linear-gradient(135deg, #0984E3 0%, #6C5CE7 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(9, 132, 227, 0.25);
    }
    .dash-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .dash-header p {
        color: rgba(255,255,255,0.8);
        font-size: 1.05rem;
        margin: 0.3rem 0 0 0;
    }

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

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Paleta de cores para gráficos
CORES = ["#6C63FF", "#00B894", "#FF6B35", "#FDCB6E", "#E17055", "#0984E3", "#A29BFE", "#55EFC4"]
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#FAFAFA"),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="rgba(108,99,255,0.1)"),
    yaxis=dict(gridcolor="rgba(108,99,255,0.1)"),
)

# ── Header ──────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="dash-header">
        <h1>📊 Dashboard</h1>
        <p>Visão geral do estoque, vendas e margens</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Carregar dados ──────────────────────────────────────────────────
try:
    entradas = listar_todos()
    catalogo_completo = listar_catalogo()
    marcas_disponiveis = listar_marcas()
    categorias_disponiveis = listar_categorias()
except Exception as e:
    st.error(f"❌ Erro ao carregar dados.\n\n`{e}`")
    st.stop()

if not entradas:
    st.info("📋 Nenhuma entrada registrada. Adicione produtos pela página de **Cadastro**.")
    st.stop()

df = pd.DataFrame(entradas)
df["data_cadastro"] = pd.to_datetime(df["data_cadastro"], utc=True)
df["data_local"] = df["data_cadastro"] - pd.Timedelta(hours=3)
df["data_dia"] = df["data_local"].dt.date
df["quantidade"] = df["quantidade"].fillna(1).astype(int)
df["margem_pct"] = ((df["preco_revenda"] - df["preco_compra"]) / df["preco_compra"] * 100).round(1)
df["lucro_unitario"] = (df["preco_revenda"] - df["preco_compra"]).round(2)
df["marca"] = df["marca"].fillna("Sem marca")
df["categoria"] = df["categoria"].fillna("Sem categoria")

# Filtrar catálogo para produtos com entradas
nomes_com_entradas = set(df["nome"].unique())
catalogo = [p for p in catalogo_completo if p["nome"] in nomes_com_entradas]

# ── Filtros globais ─────────────────────────────────────────────────
col_f1, col_f2, _ = st.columns([2, 2, 4])
with col_f1:
    filtro_marca = st.selectbox("🏷️ Marca", ["Todas"] + marcas_disponiveis, key="dash_marca")
with col_f2:
    filtro_cat = st.selectbox("📂 Categoria", ["Todas"] + categorias_disponiveis, key="dash_cat")

df_filtrado = df.copy()
if filtro_marca != "Todas":
    df_filtrado = df_filtrado[df_filtrado["marca"] == filtro_marca]
if filtro_cat != "Todas":
    df_filtrado = df_filtrado[df_filtrado["categoria"] == filtro_cat]

# ── Métricas ────────────────────────────────────────────────────────
total_entradas = len(df_filtrado)
total_itens = int(df_filtrado["quantidade"].sum())
margem_media = df_filtrado["margem_pct"].mean() if total_entradas > 0 else 0
preco_medio_revenda = df_filtrado["preco_revenda"].mean() if total_entradas > 0 else 0
total_estoque = sum((p.get("estoque_atual", 0) or 0) for p in catalogo)

st.markdown(
    f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="value">{total_entradas}</div>
            <div class="label">Entradas</div>
        </div>
        <div class="metric-card">
            <div class="value">{total_itens}</div>
            <div class="label">Itens registrados</div>
        </div>
        <div class="metric-card">
            <div class="value">{total_estoque}</div>
            <div class="label">Em estoque</div>
        </div>
        <div class="metric-card">
            <div class="value">{margem_media:.1f}%</div>
            <div class="label">Margem média</div>
        </div>
        <div class="metric-card">
            <div class="value">R\\$ {preco_medio_revenda:,.2f}</div>
            <div class="label">Preço médio revenda</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════
#  GRÁFICO 1: ENTRADAS POR DIA
# ═══════════════════════════════════════════════════════════════════
st.markdown("#### 📅 Entradas por dia")

entradas_dia = df_filtrado.groupby("data_dia").agg(
    total_quantidade=("quantidade", "sum"),
    total_entradas=("id", "count"),
).reset_index()
entradas_dia = entradas_dia.sort_values("data_dia")

if not entradas_dia.empty:
    fig_dia = px.bar(
        entradas_dia,
        x="data_dia",
        y="total_quantidade",
        text="total_quantidade",
        labels={"data_dia": "Data", "total_quantidade": "Quantidade"},
        color_discrete_sequence=[CORES[0]],
    )
    fig_dia.update_traces(textposition="outside", textfont_size=12)
    fig_dia.update_layout(
        **PLOTLY_LAYOUT,
        xaxis_title="",
        yaxis_title="Itens registrados",
        showlegend=False,
        height=350,
    )
    st.plotly_chart(fig_dia, use_container_width=True)
else:
    st.info("Nenhuma entrada para os filtros selecionados.")

# ═══════════════════════════════════════════════════════════════════
#  GRÁFICO 2: MARGEM E PREÇO POR MARCA / CATEGORIA
# ═══════════════════════════════════════════════════════════════════
st.markdown("#### 💰 Preço e margem")

col_chart1, col_chart2 = st.columns(2)

# Margem por marca
with col_chart1:
    st.markdown("##### Por marca")
    margem_marca = df_filtrado.groupby("marca").agg(
        margem_media=("margem_pct", "mean"),
        preco_compra_medio=("preco_compra", "mean"),
        preco_revenda_medio=("preco_revenda", "mean"),
        total_itens=("quantidade", "sum"),
    ).reset_index().sort_values("margem_media", ascending=True)

    if not margem_marca.empty:
        fig_marca = go.Figure()
        fig_marca.add_trace(go.Bar(
            y=margem_marca["marca"],
            x=margem_marca["preco_compra_medio"],
            name="Preço Compra",
            orientation="h",
            marker_color=CORES[2],
            text=margem_marca["preco_compra_medio"].apply(lambda x: f"R$ {x:.2f}"),
            textposition="inside",
        ))
        fig_marca.add_trace(go.Bar(
            y=margem_marca["marca"],
            x=margem_marca["preco_revenda_medio"],
            name="Preço Revenda",
            orientation="h",
            marker_color=CORES[1],
            text=margem_marca["preco_revenda_medio"].apply(lambda x: f"R$ {x:.2f}"),
            textposition="inside",
        ))
        fig_marca.update_layout(
            **PLOTLY_LAYOUT,
            barmode="group",
            height=300,
            legend=dict(orientation="h", y=-0.15),
            yaxis_title="",
            xaxis_title="Preço médio (R$)",
        )
        st.plotly_chart(fig_marca, use_container_width=True)

        # Margem como métrica
        for _, row in margem_marca.iterrows():
            cor = "#00B894" if row["margem_media"] > 0 else "#FF6B6B"
            st.markdown(
                f'<span style="font-weight: 600;">{row["marca"]}</span> — '
                f'margem: <span style="color: {cor}; font-weight: 700;">{row["margem_media"]:.1f}%</span> '
                f'({int(row["total_itens"])} itens)',
                unsafe_allow_html=True,
            )

# Margem por categoria
with col_chart2:
    st.markdown("##### Por categoria")
    margem_cat = df_filtrado.groupby("categoria").agg(
        margem_media=("margem_pct", "mean"),
        preco_compra_medio=("preco_compra", "mean"),
        preco_revenda_medio=("preco_revenda", "mean"),
        total_itens=("quantidade", "sum"),
    ).reset_index().sort_values("margem_media", ascending=True)

    if not margem_cat.empty:
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            y=margem_cat["categoria"],
            x=margem_cat["preco_compra_medio"],
            name="Preço Compra",
            orientation="h",
            marker_color=CORES[2],
            text=margem_cat["preco_compra_medio"].apply(lambda x: f"R$ {x:.2f}"),
            textposition="inside",
        ))
        fig_cat.add_trace(go.Bar(
            y=margem_cat["categoria"],
            x=margem_cat["preco_revenda_medio"],
            name="Preço Revenda",
            orientation="h",
            marker_color=CORES[1],
            text=margem_cat["preco_revenda_medio"].apply(lambda x: f"R$ {x:.2f}"),
            textposition="inside",
        ))
        fig_cat.update_layout(
            **PLOTLY_LAYOUT,
            barmode="group",
            height=300,
            legend=dict(orientation="h", y=-0.15),
            yaxis_title="",
            xaxis_title="Preço médio (R$)",
        )
        st.plotly_chart(fig_cat, use_container_width=True)

        for _, row in margem_cat.iterrows():
            cor = "#00B894" if row["margem_media"] > 0 else "#FF6B6B"
            st.markdown(
                f'<span style="font-weight: 600;">{row["categoria"]}</span> — '
                f'margem: <span style="color: {cor}; font-weight: 700;">{row["margem_media"]:.1f}%</span> '
                f'({int(row["total_itens"])} itens)',
                unsafe_allow_html=True,
            )

# ═══════════════════════════════════════════════════════════════════
#  TABELA DE ESTOQUE COM CONTROLES
# ═══════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("#### 📦 Estoque atual")
st.caption("Use os botões ➖/➕ para ajuste rápido ou ✏️ para definir valor exato.")

if not catalogo:
    st.info("Nenhum produto com entradas registradas.")
else:
    for produto in catalogo:
        nome = produto["nome"]
        estoque = produto.get("estoque_atual", 0) or 0

        # Verificar se este produto passa nos filtros
        produto_entradas = df_filtrado[df_filtrado["nome"] == nome]
        if produto_entradas.empty and (filtro_marca != "Todas" or filtro_cat != "Todas"):
            continue

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
        - 📊 **Dashboard** — Gráficos e estoque
        - ⚙️ **Gerenciar** — Configurações
        """
    )
    st.markdown("---")
    st.caption("v2.1 • Controle de Estoque")
