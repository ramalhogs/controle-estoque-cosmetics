# 📦 Controle de Estoque

Aplicação web para controle de estoque com preços de compra e revenda.

## 🚀 Setup Rápido

### 1. Criar o projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e crie uma conta (gratuito)
2. Clique em **New Project** e crie um projeto
3. Vá no **SQL Editor** (menu lateral) e execute o SQL abaixo:

```sql
CREATE TABLE produtos (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    preco_compra NUMERIC(10,2) NOT NULL,
    preco_revenda NUMERIC(10,2) NOT NULL,
    data_cadastro TIMESTAMPTZ DEFAULT NOW()
);

-- Índice para buscas por nome
CREATE INDEX idx_produtos_nome ON produtos USING gin(nome gin_trgm_ops);

-- Habilitar extensão para busca fuzzy (necessário para o índice acima)
-- Se der erro no índice acima, execute esta linha primeiro:
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Habilitar RLS (Row Level Security) - recomendado pelo Supabase
ALTER TABLE produtos ENABLE ROW LEVEL SECURITY;

-- Política para permitir todas as operações via anon key
CREATE POLICY "Allow all operations" ON produtos
    FOR ALL
    USING (true)
    WITH CHECK (true);
```

4. Vá em **Settings > API** e copie:
   - **Project URL** (ex: `https://abc123.supabase.co`)
   - **anon/public key** (a chave longa que começa com `eyJ...`)

### 2. Configurar credenciais

Edite o arquivo `.streamlit/secrets.toml`:

```toml
[supabase]
url = "https://SEU-PROJETO.supabase.co"
key = "SUA-ANON-KEY-AQUI"
```

### 3. Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 4. Deploy no Streamlit Cloud

1. Suba o código para um repositório no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório e selecione `app.py`
4. Em **Advanced Settings > Secrets**, cole o conteúdo do `secrets.toml`
5. Clique em **Deploy**

> ⚠️ **Importante**: Não commite o `secrets.toml` com credenciais reais! Adicione ao `.gitignore`.

## 📁 Estrutura

```
├── app.py                  # Página principal (pesquisa)
├── pages/
│   └── 01_cadastro.py      # Cadastro de produtos
├── database/
│   ├── __init__.py
│   ├── connection.py       # Conexão Supabase
│   └── models.py           # Operações CRUD
├── .streamlit/
│   ├── config.toml         # Tema e configurações
│   └── secrets.toml        # Credenciais (NÃO commitar!)
├── requirements.txt
└── README.md
```

## ✨ Features

- ✅ Cadastro de produtos (nome + preço compra + preço revenda)
- ✅ Data de cadastro automática
- ✅ Pesquisa por nome
- ✅ Cálculo automático de margem de lucro
- ✅ Dashboard com métricas (total, margem média, ticket médio)
- ✅ Interface moderna com tema escuro
