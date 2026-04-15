from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
import psycopg2
import os

# =====================
# APP
# =====================
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "incubadora-nissan-performance")
CORS(app)

# =====================
# CONFIG PERFORMANCE
# =====================
SENHA_PERFORMANCE = "performance2026"

def performance_autorizado():
    return session.get("performance_autorizado") is True

# =====================
# BANCO
# =====================
DATABASE_URL = os.getenv("DATABASE_URL")

def conectar_db():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL não definida")
    return psycopg2.connect(DATABASE_URL)

# =====================
# FRONTEND
# =====================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/formulario")
def formulario():
    return render_template("formulario.html")

@app.route("/ranking")
def ranking():
    return render_template("ranking.html")

@app.route("/contato")
def contato():
    return render_template("contato.html")

@app.route("/performance")
def performance():
    return render_template("performance.html")

# =====================
# AUTORIZAÇÃO PERFORMANCE
# =====================
@app.route("/api/performance/auth", methods=["POST"])
def auth_performance():
    dados = request.json

    if dados.get("senha") == SENHA_PERFORMANCE:
        session["performance_autorizado"] = True
        return jsonify({"ok": True}), 200

    return jsonify({"erro": "Senha incorreta"}), 401


@app.before_request
def proteger_apis_performance():
    if request.path.startswith("/api/performance"):
        if request.path.endswith("/auth"):
            return
        if not performance_autorizado():
            return jsonify({"erro": "Não autorizado"}), 401

# =====================
# API - IDEIAS (FORMULÁRIO)
# =====================
@app.route("/api/ideias", methods=["POST"])
def enviar_ideia():
    dados = request.json

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO ideias (
            nome, matricula, area, supervisor, descricao,
            equipamento, peca, material, part_number,
            antes, depois, ganho, area_aplicacao
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        dados.get("nome"),
        dados.get("matricula"),
        dados.get("area"),
        dados.get("supervisor"),
        dados.get("descricao"),
        dados.get("equipamento"),
        dados.get("peca"),
        dados.get("material"),
        dados.get("part_number"),
        dados.get("antes"),
        dados.get("depois"),
        dados.get("ganho"),
        dados.get("area_aplicacao")
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"mensagem": "Ideia enviada com sucesso"}), 201


@app.route("/api/ideias", methods=["GET"])
def listar_ideias():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, area, status, pontuacao
        FROM ideias
        ORDER BY data_criacao DESC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    ideias = []
    for r in rows:
        ideias.append({
            "id": r[0],
            "nome": r[1],
            "area": r[2],
            "status": r[3],
            "pontuacao": r[4]
        })

    return jsonify(ideias), 200

# =====================
# API - PERFORMANCE
# =====================
@app.route("/api/performance/ideias", methods=["GET"])
def listar_ideias_performance():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id, nome, matricula, area,
            descricao, status, pontuacao
        FROM ideias
        ORDER BY data_criacao DESC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    ideias = []
    for r in rows:
        ideias.append({
            "id": r[0],
            "nome": r[1],
            "matricula": r[2],
            "area": r[3],
            "descricao": r[4],
            "status": r[5],
            "pontuacao": r[6]
        })

    return jsonify(ideias), 200


@app.route("/api/performance/avaliar", methods=["POST"])
def avaliar_ideia():
    dados = request.json

    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ideias
        SET status = %s,
            pontuacao = %s,
            avaliador = %s
        WHERE id = %s
    """, (
        dados["status"],
        dados["pontuacao"],
        "Performance",
        dados["id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"mensagem": "Ideia avaliada"}), 200


@app.route("/api/performance/excluir/<int:ideia_id>", methods=["DELETE"])
def excluir_ideia(ideia_id):
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM ideias WHERE id = %s", (ideia_id,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"mensagem": "Ideia excluída"}), 200

# =====================
# START
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)