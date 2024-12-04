from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

# Função para obter a conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/produtos") 
    return await asyncpg.connect(DATABASE_URL)

# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para adicionar novos produtos
class Produto(BaseModel):
    id: Optional[int] = None
    nome: str
    marca: str
    animal: str
    idade: str
    quantidade: int
    preco: float

class ProdutoBase(BaseModel):
    nome: str
    marca: str
    animal: str
    idade: str
    quantidade: int
    preco: float

# Modelo para venda de produto
class VendaProduto(BaseModel):
    quantidade: int

# Modelo para atualizar atributos de um produto (exceto o ID)
class AtualizarProduto(BaseModel):
    nome: Optional[str] = None
    marca: Optional[str] = None
    animal: Optional[str] = None
    idade: Optional[str] = None
    quantidade: Optional[int] = None
    preco: Optional[float] = None

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

# Função para verificar se o produto existe usando nome e marca
async def produto_existe(nome: str, marca: str, conn: asyncpg.Connection):
    try:
        query = "SELECT * FROM produtos WHERE LOWER(nome) = LOWER($1) AND LOWER(marca) = LOWER($2)"
        result = await conn.fetchval(query, nome, marca)
        return result is not None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao verificar se o produto existe: {str(e)}")
    
# 1. Adicionar um novo produto
@app.post("/api/v1/produtos/", status_code=201)
async def adicionar_produto(produto: ProdutoBase):
    conn = await get_database()
    if await produto_existe(produto.nome, produto.marca, conn):
        raise HTTPException(status_code=400, detail="produto já existe.")
    try:
        query = "INSERT INTO produtos (nome, marca, animal, idade, quantidade, preco) VALUES ($1, $2, $3, $4, $5, $6)"
        async with conn.transaction():
            result = await conn.execute(query, produto.nome, produto.marca, produto.animal, produto.idade, produto.quantidade, produto.preco)
            return {"message": "Produto adicionado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao adicionar o produto: {str(e)}")
    finally:
        await conn.close()

# 2. Listar todas os produtos
@app.get("/api/v1/produtos/", response_model=List[Produto])
async def listar_produtos():
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos"
        rows = await conn.fetch(query)
        produtos = [dict(row) for row in rows]
        return produtos
    finally:
        await conn.close()

# 3. Buscar produto por ID
@app.get("/api/v1/produtos/{produto_id}")
async def listar_produto_por_id(produto_id: int):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")
        return dict(produto)
    finally:
        await conn.close()

# 4. Vender um produto (reduzir quantidade no estoque)
@app.put("/api/v1/produtos/{produto_id}/vender/")
async def vender_produto(produto_id: int, venda: VendaProduto):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        if produto['quantidade'] < venda.quantidade:
            raise HTTPException(status_code=400, detail="Quantidade insuficiente no estoque.")

        nova_quantidade = produto['quantidade'] - venda.quantidade
        update_query = "UPDATE produtos SET quantidade = $1 WHERE id = $2"
        await conn.execute(update_query, nova_quantidade, produto_id)

        valor_venda = produto['preco'] * venda.quantidade
        insert_venda_query = """
            INSERT INTO vendas (produto_id, quantidade_vendida, valor_venda) 
            VALUES ($1, $2, $3)
        """
        await conn.execute(insert_venda_query, produto_id, venda.quantidade, valor_venda)

        produto_atualizada = dict(produto)
        produto_atualizada['quantidade'] = nova_quantidade

        return {"message": "Venda realizada com sucesso!", "produto": produto_atualizada}
    finally:
        await conn.close()

# 5. Atualizar atributos de um produto pelo ID (exceto o ID)
@app.patch("/api/v1/produtos/{produto_id}")
async def atualizar_produto(produto_id: int, produto_atualizacao: AtualizarProduto):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        update_query = """
            UPDATE produtos
            SET nome = COALESCE($1, nome),
                marca = COALESCE($2, marca),
                animal = COALESCE($3, animal),
                idade = COALESCE($4, idade),
                quantidade = COALESCE($5, quantidade),
                preco = COALESCE($6, preco)
            WHERE id = $7
        """
        await conn.execute(
            update_query,
            produto_atualizacao.nome,
            produto_atualizacao.marca,
            produto_atualizacao.animal,
            produto_atualizacao.idade,
            produto_atualizacao.quantidade,
            produto_atualizacao.preco,
            produto_id
        )
        return {"message": "Produto atualizada com sucesso!"}
    finally:
        await conn.close()

# 6. Remover um produto pelo ID
@app.delete("/api/v1/produtos/{produto_id}")
async def remover_produto(produto_id: int):
    conn = await get_database()
    try:
        query = "SELECT * FROM produtos WHERE id = $1"
        produto = await conn.fetchrow(query, produto_id)
        if produto is None:
            raise HTTPException(status_code=404, detail="Produto não encontrado.")

        delete_query = "DELETE FROM produtos WHERE id = $1"
        await conn.execute(delete_query, produto_id)
        return {"message": "Produto removido com sucesso!"}
    finally:
        await conn.close()

# 7. Resetar banco de dados de produtos
@app.delete("/api/v1/produtos/")
async def resetar_produtos():
    init_sql = os.getenv("INIT_SQL", "db/init.sql")
    conn = await get_database()
    try:
        with open(init_sql, 'r') as file:
            sql_commands = file.read()
        await conn.execute(sql_commands)
        return {"message": "Banco de dados limpo com sucesso!"}
    finally:
        await conn.close()

# 8. Listar vendas
@app.get("/api/v1/vendas/")
async def listar_vendas():
    conn = await get_database()
    try:
        query = """
            SELECT v.id, v.quantidade_vendida, v.valor_venda, v.data_venda, o.nome as produto_nome
            FROM vendas v
            JOIN produtos o ON v.produto_id = o.id
        """
        rows = await conn.fetch(query)
        vendas = [{"id": row["id"], "quantidade_vendida": row["quantidade_vendida"],
                   "valor_venda": row["valor_venda"], "data_venda": row["data_venda"],
                   "produto_nome": row["produto_nome"]} for row in rows]
        return vendas
    finally:
        await conn.close()