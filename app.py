import sqlite3
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


# Função para conectar ao banco de dados SQLite
def get_db_connection():
  conn = sqlite3.connect("database.db")
  conn.row_factory = (
      sqlite3.Row
  )  # Permite acessar as colunas pelo nome (ex: tarefa['titulo'])
  return conn


# Função para inicializar o banco de dados e criar a tabela se não existir
def init_db():
  conn = get_db_connection()
  conn.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'Pendente'
        )
    """)
  conn.commit()
  conn.close()


# Rota Principal: Visualizar e Cadastrar Tarefas
@app.route("/", methods=["GET", "POST"])
def index():
  conn = get_db_connection()

  if request.method == "POST":
    titulo = request.form["titulo"]
    descricao = request.form["descricao"]

    if titulo:
      conn.execute(
          "INSERT INTO tarefas (titulo, descricao, status) VALUES (?, ?, ?)",
          (titulo, descricao, "Pendente"),
      )
      conn.commit()
    conn.close()
    return redirect(url_for("index"))

  # Buscar todas as tarefas cadastradas
  tarefas = conn.execute("SELECT * FROM tarefas").fetchall()
  conn.close()
  return render_template("index.html", tarefas=tarefas)


# Rota para Alterar o Status da Tarefa (Pendente <-> Concluída)
@app.route("/alternar/<int:id>")
def alternar_status(id):
  conn = get_db_connection()
  tarefa = conn.execute(
      "SELECT status FROM tarefas WHERE id = ?", (id,)
  ).fetchone()

  if tarefa:
    # Alterna o status atual
    novo_status = (
        "Concluída" if tarefa["status"] == "Pendente" else "Pendente"
    )
    conn.execute(
        "UPDATE tarefas SET status = ? WHERE id = ?", (novo_status, id)
    )
    conn.commit()

  conn.close()
  return redirect(url_for("index"))


# Rota para Excluir uma Tarefa
@app.route("/excluir/<int:id>")
def excluir(id):
  conn = get_db_connection()
  conn.execute("DELETE FROM tarefas WHERE id = ?", (id,))
  conn.commit()
  conn.close()
  return redirect(url_for("index"))


if __name__ == "__main__":
  init_db()  # Garante que o banco de dados e a tabela existem ao iniciar
  app.run(debug=True)