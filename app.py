from flask import Flask, request, jsonify, render_template, session, redirect, send_file
from flask_cors import CORS
import psycopg2
import os
from openpyxl import load_workbook
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.secret_key = "incubadora-nissan"
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")
SENHA_PERFORMANCE = "performance2026"

def conectar_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    if "usuario_id" not in session:
        return redirect("/login")

    return render_template("index.html",
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

    return render_template("formulario.html",
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

# ======================
# LOGIN
# ======================
@app.route("/api/login", methods=["POST"])
def api_login():
    d = request.json

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, area
        FROM usuarios
        WHERE matricula = %s AND senha = %s
    """, (
        d["matricula"],
        d["senha"]
    ))

    user = cur.fetchone()

    if not user:
        return jsonify({"erro": "Usuário não encontrado"}), 401

    session["usuario_id"] = user[0]
    session["nome"] = user[1]
    session["matricula"] = d["matricula"]
    session["area"] = user[2]

    cur.close()
    conn.close()

    return jsonify({"ok": True})

@app.route("/api/cadastro", methods=["POST"])
def api_cadastro():
    d = request.json

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM usuarios WHERE matricula = %s", (d["matricula"],))
    if cur.fetchone():
        return jsonify({"erro": "Usuário já existe"}), 400

    cur.execute("""
        INSERT INTO usuarios (nome, matricula, senha)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        d["nome"],
        d["matricula"],
        d["senha"]
    ))

    user_id = cur.fetchone()[0]
    conn.commit()

    session["usuario_id"] = user_id
    session["nome"] = d["nome"]
    session["matricula"] = d["matricula"]

    cur.close()
    conn.close()

    return jsonify({"ok": True})

@app.route("/api/ideias", methods=["POST"])
def enviar_ideia():
    if "usuario_id" not in session:
        return jsonify({"erro": "Não autorizado"}), 401

    d = request.json

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

@app.route("/ranking")
def ranking():
    return render_template("ranking.html")

@app.route("/api/ranking")
def api_ranking():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            nome,
            area,
            descricao,
            pontuacao
        FROM ideias
        WHERE status = 'Aprovada'
        ORDER BY pontuacao DESC
        LIMIT 10
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "nome": r[0],
            "area": r[1],
            "descricao": r[2],
            "pontuacao": r[3]
        } for r in rows
    ])

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/api/performance/auth", methods=["POST"])
def auth_performance():
    if request.json.get("senha") == SENHA_PERFORMANCE:
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

def salvar_excel(d):
    wb = load_workbook("Performance_Projetos.xlsx")
    ws = wb.active

    ws.append([
        datetime.now().strftime("%d/%m/%Y %H:%M"),

        d.get("nome"),
        d.get("matricula"),
        d.get("supervisor"),
        d.get("area"),
        d.get("descricao"),
        d.get("antes_depois"),
        d.get("saving"),
        d.get("part_number"),
        d.get("area_aplicacao"),

        # ✅ BENEFÍCIO
        d.get("qualidade"),
        d.get("seguranca"),
        d.get("kpi"),
        d.get("saving_beneficio"),
        d.get("norma"),

        # ✅ ESFORÇO
        d.get("custo"),
        d.get("tempo"),
        d.get("treinamento"),
        d.get("logistica"),
        d.get("mudanca"),

        # ✅ RESULTADOS
        d.get("total_beneficio"),
        d.get("total_esforco"),
        d.get("prioridade")
    ])

    wb.save("Performance_Projetos.xlsx")

@app.route("/api/performance/deletar/<int:id>", methods=["DELETE"])
def deletar_ideia(id):
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM ideias WHERE id = %s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"ok": True})

@app.route("/api/minhas-ideias")
def minhas_ideias():
    if "usuario_id" not in session:
        return jsonify([])

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT descricao, status
        FROM ideias
        WHERE usuario_id = %s
        ORDER BY data_criacao DESC
    """, (session["usuario_id"],))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {
            "descricao": r[0],
            "status": r[1]
        } for r in rows
    ])

@app.route("/api/performance/avaliar", methods=["POST"])
def avaliar():
    d = request.json

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ideias
        SET status = %s,
            pontuacao = %s,
            impacto = %s,
            avaliador = 'Performance'
        WHERE id = %s
        RETURNING 
            nome, matricula, area, descricao,
            antes_depois, supervisor,
            ganho, impacto,
            part_number, area_aplicacao
    """, (
        d["status"],
        float(d["pontuacao"]),
        d["impacto"],
        d["id"]
    ))

    r = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if d["status"] == "Aprovada":
        salvar_excel({
            "nome": r[0],
            "matricula": r[1],
            "area": r[2],
            "descricao": r[3],
            "antes_depois": r[4],
            "supervisor": r[5],
            "saving": r[6],
            "part_number": r[8],
            "area_aplicacao": r[9],

            # ✅ NOVOS CAMPOS (AGORA FUNCIONA 🔥)
            "qualidade": d.get("qualidade"),
            "seguranca": d.get("seguranca"),
            "kpi": d.get("kpi"),
            "saving_beneficio": d.get("saving_beneficio"),
            "norma": d.get("norma"),

            "custo": d.get("custo"),
            "tempo": d.get("tempo"),
            "treinamento": d.get("treinamento"),
            "logistica": d.get("logistica"),
            "mudanca": d.get("mudanca"),

            "total_beneficio": d.get("total_beneficio"),
            "total_esforco": d.get("total_esforco"),
            "prioridade": d.get("prioridade")
        })

    return jsonify({"ok": True})


# ======================
if __name__ == "__main__":
    app.run(debug=True)