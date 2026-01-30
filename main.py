import streamlit as st
from google import genai
import pandas as pd
import plotly.express as px
import json

# Configurações iniciais
st.set_page_config(page_title="Nossa Grana", layout="wide")
st.title("💰 Analisador de Gastos do Casal")

# --- ÁREA DE CONFIGURAÇÃO (SECRETS) ---
# No Streamlit Cloud, você configuraria isso no painel lateral em "Secrets"
API_KEY = st.sidebar.text_input("Cole sua API Key do Gemini aqui", type="password")

if not API_KEY:
    st.info("Por favor, insira sua API Key para começar.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# --- UPLOAD ---
uploaded_file = st.file_uploader("Suba o PDF do seu banco", type=['pdf'])

if uploaded_file:
    if st.button("🚀 Processar Extrato"):
        with st.spinner("Gemini analisando e categorizando..."):
            pdf_bytes = uploaded_file.read()
            
            prompt = """
            Leia as transações deste extrato. Ignore saldos e transferências entre contas próprias se identificar.
            Extraia: Data, Descrição, Valor (numérico) e Categoria.
            Categorias permitidas: Mercado, Lazer, Transporte, Saúde, Moradia, Assinaturas, Outros.
            Retorne APENAS um JSON puro (lista de objetos).
            """

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, {"mime_type": "application/pdf", "data": pdf_bytes}]
            )

            try:
                # Limpeza básica do retorno da IA
                raw_json = response.text.replace("```json", "").replace("```", "").strip()
                dados = json.loads(raw_json)
                
                # Transformando em DataFrame (Tabela do Python)
                df = pd.DataFrame(dados)
                df['valor'] = pd.to_numeric(df['valor'])

                # --- VISUALIZAÇÃO ---
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Lista de Gastos")
                    st.dataframe(df, use_container_width=True)

                with col2:
                    st.subheader("Gasto por Categoria")
                    fig = px.pie(df, values='valor', names='categoria', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)

                st.metric("Total Gasto", f"R$ {df['valor'].sum():.2f}")

            except Exception as e:
                st.error(f"Erro ao processar: {e}")