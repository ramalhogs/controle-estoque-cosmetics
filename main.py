import streamlit as st
from google import genai
import pandas as pd
import json

st.set_page_config(page_title="Finanças Casal", page_icon="💰")

# --- BUSCA A CHAVE AUTOMATICAMENTE ---
# O Streamlit procura primeiro em .streamlit/secrets.toml (local) 
# ou nas configurações de Secrets (nuvem)
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Chave API não configurada nos Secrets!")
    st.stop()

client = genai.Client(api_key=API_KEY)

# --- RESTO DO CÓDIGO (Interface e Lógica) ---
st.title("📂 Analisador de Extrato Automático")
uploaded_file = st.file_uploader("Suba seu PDF bancário", type=['pdf'])

if uploaded_file:
    if st.button("Categorizar Gastos"):
        with st.spinner("IA processando o PDF..."):
            pdf_bytes = uploaded_file.read()
            
            prompt = """
            Retorne um JSON com os gastos deste extrato.
            Formato: [{"data": "DD/MM", "descricao": "texto", "valor": 0.0, "setor": "Mercado/Transporte/etc"}]
            Retorne APENAS o JSON.
            """

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, {"mime_type": "application/pdf", "data": pdf_bytes}]
            )

            # Processamento dos dados
            raw_json = response.text.replace("```json", "").replace("```", "").strip()
            df = pd.DataFrame(json.loads(raw_json))
            df['valor'] = pd.to_numeric(df['valor'])

            # Exibição
            st.subheader("Soma por Setor")
            resumo = df.groupby('setor')['valor'].sum().reset_index()
            st.table(resumo)
            
            st.metric("Total Geral", f"R$ {df['valor'].sum():.2f}")