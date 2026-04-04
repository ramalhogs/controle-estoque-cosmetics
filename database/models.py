from datetime import datetime, timezone
from database.connection import get_supabase_client


# ═══════════════════════════════════════════════════════════════════
#  MARCAS
# ═══════════════════════════════════════════════════════════════════

def listar_marcas() -> list[str]:
    """Retorna lista de nomes de marcas cadastradas, em ordem alfabética."""
    supabase = get_supabase_client()
    response = supabase.table("marcas").select("nome").order("nome").execute()
    return [r["nome"] for r in response.data]


def adicionar_marca(nome: str) -> dict:
    """Cadastra uma nova marca."""
    supabase = get_supabase_client()
    response = supabase.table("marcas").insert({"nome": nome.strip()}).execute()
    return response.data[0]


def deletar_marca(marca_id: int) -> None:
    """Remove uma marca pelo ID."""
    supabase = get_supabase_client()
    supabase.table("marcas").delete().eq("id", marca_id).execute()


def listar_marcas_completo() -> list[dict]:
    """Retorna lista completa de marcas (id + nome)."""
    supabase = get_supabase_client()
    response = supabase.table("marcas").select("*").order("nome").execute()
    return response.data


# ═══════════════════════════════════════════════════════════════════
#  CATEGORIAS
# ═══════════════════════════════════════════════════════════════════

def listar_categorias() -> list[str]:
    """Retorna lista de nomes de categorias cadastradas, em ordem alfabética."""
    supabase = get_supabase_client()
    response = supabase.table("categorias").select("nome").order("nome").execute()
    return [r["nome"] for r in response.data]


def adicionar_categoria(nome: str) -> dict:
    """Cadastra uma nova categoria."""
    supabase = get_supabase_client()
    response = supabase.table("categorias").insert({"nome": nome.strip()}).execute()
    return response.data[0]


def deletar_categoria(categoria_id: int) -> None:
    """Remove uma categoria pelo ID."""
    supabase = get_supabase_client()
    supabase.table("categorias").delete().eq("id", categoria_id).execute()


def listar_categorias_completo() -> list[dict]:
    """Retorna lista completa de categorias (id + nome)."""
    supabase = get_supabase_client()
    response = supabase.table("categorias").select("*").order("nome").execute()
    return response.data


# ═══════════════════════════════════════════════════════════════════
#  PRODUTOS
# ═══════════════════════════════════════════════════════════════════

def adicionar_produto(
    nome: str,
    preco_compra: float,
    preco_revenda: float,
    marca: str,
    categoria: str | None = None,
) -> dict:
    """Adiciona um novo produto ao banco de dados."""
    supabase = get_supabase_client()
    dados = {
        "nome": nome.strip(),
        "preco_compra": round(preco_compra, 2),
        "preco_revenda": round(preco_revenda, 2),
        "marca": marca,
        "data_cadastro": datetime.now(timezone.utc).isoformat(),
    }
    if categoria:
        dados["categoria"] = categoria

    response = supabase.table("produtos").insert(dados).execute()
    return response.data[0]


def buscar_produtos(
    termo: str = "",
    marca: str | None = None,
    categoria: str | None = None,
) -> list[dict]:
    """Busca produtos com filtros opcionais de nome, marca e categoria."""
    supabase = get_supabase_client()
    query = supabase.table("produtos").select("*")

    if termo:
        query = query.ilike("nome", f"%{termo}%")
    if marca:
        query = query.eq("marca", marca)
    if categoria:
        query = query.eq("categoria", categoria)

    response = query.order("data_cadastro", desc=True).execute()
    return response.data


def listar_todos() -> list[dict]:
    """Lista todos os produtos cadastrados, do mais recente ao mais antigo."""
    supabase = get_supabase_client()
    response = (
        supabase.table("produtos")
        .select("*")
        .order("data_cadastro", desc=True)
        .execute()
    )
    return response.data


def deletar_produto(produto_id: int) -> None:
    """Remove um produto pelo ID."""
    supabase = get_supabase_client()
    supabase.table("produtos").delete().eq("id", produto_id).execute()

