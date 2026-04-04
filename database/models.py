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
#  CATÁLOGO DE PRODUTOS
# ═══════════════════════════════════════════════════════════════════

def listar_catalogo() -> list[dict]:
    """Retorna todos os produtos do catálogo (id, nome, estoque_atual)."""
    supabase = get_supabase_client()
    response = (
        supabase.table("produtos_catalogo")
        .select("*")
        .order("nome")
        .execute()
    )
    return response.data


def listar_nomes_catalogo() -> list[str]:
    """Retorna apenas os nomes de produtos do catálogo, em ordem alfabética."""
    supabase = get_supabase_client()
    response = (
        supabase.table("produtos_catalogo")
        .select("nome")
        .order("nome")
        .execute()
    )
    return [r["nome"] for r in response.data]


def adicionar_ao_catalogo(nome: str) -> dict:
    """Adiciona um novo produto ao catálogo com estoque 0."""
    supabase = get_supabase_client()
    response = (
        supabase.table("produtos_catalogo")
        .insert({"nome": nome.strip(), "estoque_atual": 0})
        .execute()
    )
    return response.data[0]


def deletar_do_catalogo(catalogo_id: int) -> None:
    """Remove um produto do catálogo."""
    supabase = get_supabase_client()
    supabase.table("produtos_catalogo").delete().eq("id", catalogo_id).execute()


def atualizar_estoque(nome_produto: str, novo_valor: int) -> None:
    """Define o estoque de um produto para um valor absoluto."""
    supabase = get_supabase_client()
    supabase.table("produtos_catalogo").update(
        {"estoque_atual": novo_valor}
    ).eq("nome", nome_produto).execute()


def ajustar_estoque(nome_produto: str, delta: int) -> None:
    """Incrementa (delta > 0) ou decrementa (delta < 0) o estoque de um produto.

    Busca o valor atual, calcula o novo, e atualiza. Nunca fica negativo.
    """
    supabase = get_supabase_client()
    response = (
        supabase.table("produtos_catalogo")
        .select("estoque_atual")
        .eq("nome", nome_produto)
        .execute()
    )
    if not response.data:
        return
    atual = response.data[0]["estoque_atual"] or 0
    novo = max(0, atual + delta)
    supabase.table("produtos_catalogo").update(
        {"estoque_atual": novo}
    ).eq("nome", nome_produto).execute()


# ═══════════════════════════════════════════════════════════════════
#  ENTRADAS DE PRODUTOS (histórico de compras)
# ═══════════════════════════════════════════════════════════════════

def adicionar_produto(
    nome: str,
    preco_compra: float,
    preco_revenda: float,
    marca: str,
    quantidade: int = 1,
    categoria: str | None = None,
) -> dict:
    """Registra uma nova entrada de produto e incrementa o estoque no catálogo."""
    supabase = get_supabase_client()
    dados = {
        "nome": nome.strip(),
        "preco_compra": round(preco_compra, 2),
        "preco_revenda": round(preco_revenda, 2),
        "marca": marca,
        "quantidade": quantidade,
        "data_cadastro": datetime.now(timezone.utc).isoformat(),
    }
    if categoria:
        dados["categoria"] = categoria

    response = supabase.table("produtos").insert(dados).execute()

    # Incrementar estoque no catálogo
    ajustar_estoque(nome.strip(), quantidade)

    return response.data[0]


def buscar_produtos(
    termo: str = "",
    marca: str | None = None,
    categoria: str | None = None,
) -> list[dict]:
    """Busca entradas com filtros opcionais de nome, marca e categoria."""
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
    """Lista todas as entradas, da mais recente à mais antiga."""
    supabase = get_supabase_client()
    response = (
        supabase.table("produtos")
        .select("*")
        .order("data_cadastro", desc=True)
        .execute()
    )
    return response.data


def deletar_produto(produto_id: int) -> None:
    """Remove uma entrada pelo ID."""
    supabase = get_supabase_client()
    supabase.table("produtos").delete().eq("id", produto_id).execute()


def renomear_produto(nome_antigo: str, nome_novo: str) -> None:
    """Renomeia um produto em todas as entradas e no catálogo."""
    supabase = get_supabase_client()
    nome_novo = nome_novo.strip()
    # Atualizar no catálogo
    supabase.table("produtos_catalogo").update(
        {"nome": nome_novo}
    ).eq("nome", nome_antigo).execute()
    # Atualizar em todas as entradas
    supabase.table("produtos").update(
        {"nome": nome_novo}
    ).eq("nome", nome_antigo).execute()

