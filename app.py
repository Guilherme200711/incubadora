from flask import Flask, request, jsonify, render_template, session, redirect, send_file
from flask_cors import CORS
import psycopg2
import os
from openpyxl import load_workbook
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

# ✅ CONFIG DE SESSÃO (PRODUÇÃO)
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.secret_key = "incubadora-nissan"

CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")
SENHA_PERFORMANCE = "performance2026"


# ✅ CONEXÃO COMPATÍVEL COM SUPABASE + RENDER
def conectar_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


# ======================
# ROTAS DE PÁGINA
# ======================
@app.route("/")
def index():
    if "usuario_id" not in session:
        return redirect("/login")

    return render_template(
        "index.html",
        nome=session["nome"],
        matricula=session["matricula"]
    )


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/formulario")
def formulario():
    if "usuario_id" not in session:
        return redirect("/login")

    return render_template(
        "formulario.html",
        nome=session["nome"],
        matricula=session["matricula"],
        area=session.get("area")
    )


@app.route("/performance")
def performance():
    return render_template("performance.html")


@app.route("/baixar-excel")
def baixar_excel():
    return send_file("Performance_Projetos.xlsx", as_attachment=True)


@app.route("/ranking")
def ranking():
    return render_template("ranking.html")


@app.route("/contato")
def contato():
    return render_template("contato.html")


# ======================
# LOGIN
# ======================
@app.route("/api/login", methods=["POST"])
def api_login():
    d = request.get_json()
    if not d:
        return jsonify({"erro": "JSON inválido"}), 400

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, area
        FROM usuarios
        WHERE matricula = %s AND senha = %s
    """, (d["matricula"], d["senha"]))

    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        return jsonify({"erro": "Usuário não encontrado"}), 401

    session["usuario_id"] = user[0]
    session["nome"] = user[1]
    session["matricula"] = d["matricula"]
    session["area"] = user[2]

    cur.close()
    conn.close()

    return jsonify({"ok": True})


# ======================
# CADASTRO (SEM RETURNING — COMPATÍVEL COM POOLER)
# ======================
@app.route("/api/cadastro", methods=["POST"])
def api_cadastro():
    d = request.get_json()
    if not d:
        return jsonify({"erro": "JSON inválido"}), 400

    conn = conectar_db()
    cur = conn.cursor()

    # verifica duplicidade
    cur.execute("SELECT id FROM usuarios WHERE matricula = %s", (d["matricula"],))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"erro": "Usuário já existe"}), 400

    # INSERT SEM RETURNING
    cur.execute("""
        INSERT INTO usuarios (nome, matricula, senha)
        VALUES (%s, %s, %s)
    """, (d["nome"], d["matricula"], d["senha"]))

    conn.commit()

    # busca o id depois (seguro no pooler)
    cur.execute("SELECT id FROM usuarios WHERE matricula = %s", (d["matricula"],))
    user_id = cur.fetchone()[0]

    session["usuario_id"] = user_id
    session["nome"] = d["nome"]
    session["matricula"] = d["matricula"]

    cur.close()
    conn.close()

    return jsonify({"ok": True})


# ======================
# ENVIO DE IDEIA
# ======================
@app.route("/api/ideias", methods=["POST"])
def enviar_ideia():
    if "usuario_id" not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    d = request.get_json()
    if not d:
        return jsonify({"erro": "JSON inválido"}), 400

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ideias (
            usuario_id, nome, matricula, area, supervisor,
            descricao, antes_depois,
            equipamento, peca, material, part_number,
            ganho, area_aplicacao
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        session["usuario_id"],
        d["nome"],
        d["matricula"],
        d["area"],
        d["supervisor"],
        d["descricao"],
        d["antes_depois"],
        d.get("equipamento"),
        d.get("peca"),
        d.get("material"),
        d.get("part_number"),
        d["ganho"],
        d["area_aplicacao"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"ok": True})


# ======================
# PERFORMANCE
# ======================
@app.route("/api/performance/auth", methods=["POST"])
def auth_performance():
    d = request.get_json()
    if not d:
        return jsonify({"erro": "JSON inválido"}), 400

    if d.get("senha") == SENHA_PERFORMANCE:
        session["performance_autorizado"] = True
        return jsonify({"ok": True})

    return jsonify({"erro": "Senha incorreta"}), 401


def autorizado():
    return session.get("performance_autorizado") is True


@app.before_request
def proteger():
    if request.path.startswith("/api/performance") and not request.path.endswith("/auth"):
        if not autorizado():
            return jsonify({"erro": "Não autorizado"}), 401


@app.route("/api/performance/ideias")
def listar_ideias():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, matricula, area, descricao, status, pontuacao
        FROM ideias
        ORDER BY data_criacao DESC
    """)

    dados = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "nome": r[1],
            "matricula": r[2],
            "area": r[3],
            "descricao": r[4],
            "status": r[5],
            "pontuacao": r[6]
        } for r in dados
    ])


# ✅ ROTA DELETAR CORRETA
@app.route("/api/performance/deletar/<int:id>", methods=["DELETE"])
def deletar_ideia(id):
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM ideias WHERE id = %s", (id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"ok": True})


# ======================
if __name__ == "__main__":
    app.run(debug=True)