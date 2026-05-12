document.addEventListener("DOMContentLoaded", () => {

    // ===============================
    // LOGIN
    // ===============================
    const loginForm = document.getElementById("loginForm");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(loginForm);

            const dados = {
                matricula: formData.get("matricula"),
                senha: formData.get("senha")
            };

            try {
                const resp = await fetch("/api/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(dados)
                });

                if (resp.ok) {
                    window.location.href = "/";
                } else {
                    alert("❌ Login inválido. Verifique matrícula e senha.");
                }

            } catch (err) {
                console.error(err);
                alert("❌ Erro de conexão com o servidor");
            }
        });
    }

    // ===============================
    // ENVIO DE IDEIA
    // ===============================
    const formIdeia = document.getElementById("formIdeia");

    if (formIdeia) {
        formIdeia.addEventListener("submit", async (e) => {
            e.preventDefault();

            const formData = new FormData(formIdeia);

            const dados = {
                nome: formData.get("nome"),
                matricula: formData.get("matricula"),
                area: formData.get("area"),
                supervisor: formData.get("supervisor"),
                descricao: formData.get("descricao"),
                antes_depois: formData.get("antes_depois"),
                equipamento: formData.get("equipamento"),
                peca: formData.get("peca"),
                material: formData.get("material"),
                part_number: formData.get("part_number"),
                ganho: Number(formData.get("ganho")),
                area_aplicacao: formData.get("area_aplicacao")
            };

            try {
                const resp = await fetch("/api/ideias", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(dados)
                });

                if (resp.ok) {
                    alert("✅ Ideia enviada com sucesso!");
                    formIdeia.reset();

                    // 🔥 Atualiza a lista na home automaticamente
                    carregarMinhasIdeias();

                } else {
                    alert("❌ Erro ao enviar ideia");
                }

            } catch (err) {
                console.error(err);
                alert("❌ Erro de conexão");
            }
        });
    }

    // ===============================
    // MINHAS IDEIAS (HOME)
    // ===============================
    carregarMinhasIdeias();

});


// ✅ FUNÇÃO PRINCIPAL (HOME)
async function carregarMinhasIdeias() {

    const container = document.getElementById("listaIdeias");

    if (!container) return;

    try {
        const resp = await fetch("/api/minhas-ideias");
        const ideias = await resp.json();

        if (!ideias.length) {
            container.innerHTML = `
                <div class="sem-ideias">
                    Você ainda não enviou nenhuma ideia.
                </div>
            `;
            return;
        }

        let html = "";

        ideias.slice(0, 3).forEach(i => {

            let classe = "analise";
            let emoji = "⏳";

            if (i.status === "Aprovada") {
                classe = "aprovada";
                emoji = "✅";
            } else if (i.status === "Reprovada") {
                classe = "reprovada";
                emoji = "❌";
            }

            html += `
                <div class="ideia-card ${classe}">
                    <div class="ideia-info">
                        <span class="ideia-desc">${i.descricao}</span>
                    </div>
                    <div class="ideia-status">${emoji} ${i.status}</div>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (err) {
        console.error(err);

        container.innerHTML = `
            <div class="sem-ideias">
                Erro ao carregar ideias.
            </div>
        `;
    }
}