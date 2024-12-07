from flask import Blueprint, render_template, redirect, request, url_for, flash, session
import requests

API_BASE_URL = "http://backend:8000/api/v1/produtos/"

main = Blueprint("main", __name__)

# Listar todos os produtos
@main.route("/")
def index():
    try:
        # Obter todos os produtos da API
        response = requests.get(API_BASE_URL)
        produtos = response.json()

        # Aplicar filtros
        animal = request.args.get("animal")
        idade = request.args.get("idade")
        order_by = request.args.get("order_by")
        order = request.args.get("order", "asc")

        if animal:
            produtos = [p for p in produtos if p["animal"] == animal]
        if idade:
            produtos = [p for p in produtos if p["idade"] == idade]

        # Aplicar ordenação
        if order_by:
            produtos = sorted(produtos, key=lambda x: x[order_by], reverse=(order == "desc"))

        filters = {"animal": animal, "idade": idade, "order_by": order_by, "order": order}
        return render_template("index.html", produtos=produtos, filters=filters)
    except Exception as e:
        return render_template("error.html", message="Erro ao buscar produtos.")


# Formulário para adicionar produto
@main.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        produto = {
            "nome": request.form["nome"],
            "marca": request.form["marca"],
            "animal": request.form["animal"],
            "idade": request.form["idade"],
            "quantidade": int(request.form["quantidade"]),
            "preco": float(request.form["preco"]),
        }
        try:
            response = requests.post(API_BASE_URL, json=produto)
            if response.status_code == 201:
                flash("Produto adicionado com sucesso!", "success")
                return redirect(url_for("main.index"))
            else:
                flash("Erro ao adicionar produto.", "danger")
        except Exception:
            flash("Erro ao conectar à API.", "danger")
    return render_template("add.html")

# Editar produto
@main.route("/edit/<int:produto_id>", methods=["GET", "POST"])
def edit(produto_id):
    if request.method == "POST":
        produto = {
            "nome": request.form.get("nome"),
            "marca": request.form.get("marca"),
            "animal": request.form.get("animal"),
            "idade": request.form.get("idade"),
            "quantidade": request.form.get("quantidade"),
            "preco": request.form.get("preco"),
        }
        try:
            response = requests.patch(f"{API_BASE_URL}{produto_id}", json=produto)
            if response.status_code == 200:
                flash("Produto atualizado com sucesso!", "success")
                return redirect(url_for("main.index"))
            else:
                flash("Erro ao atualizar produto.", "danger")
        except Exception:
            flash("Erro ao conectar à API.", "danger")
    produto = requests.get(f"{API_BASE_URL}{produto_id}").json()
    return render_template("edit.html", produto=produto)

# Vender produto (reduzir quantidade no estoque)
@main.route("/vender/<int:produto_id>", methods=["GET", "POST"])
def vender(produto_id):
    if request.method == "POST":
        quantidade_vendida = int(request.form["quantidade"])
        try:
            venda_data = {"quantidade": quantidade_vendida}
            response = requests.put(f"{API_BASE_URL}{produto_id}/vender/", json=venda_data)
            if response.status_code == 200:
                flash("Venda realizada com sucesso!", "success")
            else:
                flash(response.json().get("detail", "Erro ao realizar venda"), "danger")
        except Exception:
            flash("Erro ao conectar à API.", "danger")
        return redirect(url_for("main.index"))
    produto = requests.get(f"{API_BASE_URL}{produto_id}").json()
    return render_template("vender.html", produto=produto)

# Listar vendas
@main.route("/vendas")
def listar_vendas():
    try:
        response = requests.get("http://backend:8000/api/v1/vendas/")
        vendas = response.json()
        return render_template("vendas.html", vendas=vendas)
    except Exception as e:
        flash("Erro ao conectar à API ou buscar vendas.", "danger")
        return redirect(url_for("main.index"))

# Deletar produto
@main.route("/delete/<int:produto_id>", methods=["POST"])
def delete(produto_id):
    try:
        response = requests.delete(f"{API_BASE_URL}{produto_id}")
        if response.status_code == 200:
            flash("Produto removido com sucesso!", "success")
        else:
            flash("Erro ao remover produto.", "danger")
    except Exception:
        flash("Erro ao conectar à API.", "danger")
    return redirect(url_for("main.index"))

# Resetar banco de dados
@main.route("/reset", methods=["POST"])
def reset_db():
    try:
        response = requests.delete(API_BASE_URL)
        if response.status_code == 200:
            flash("Banco de dados resetado com sucesso!", "success")
        else:
            flash("Erro ao resetar banco de dados.", "danger")
    except Exception:
        flash("Erro ao conectar à API.", "danger")
    return redirect(url_for("main.index"))