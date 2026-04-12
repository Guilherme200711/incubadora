// ===============================
// SCROLL SUAVE (SEU CÓDIGO)
// ===============================
document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", function (e) {
        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            target.scrollIntoView({ behavior: "smooth" });
        }
    });
});

// ===============================
// ENVIO DO FORMULÁRIO
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formIdeia");

    if (!form) return; // evita erro em outras páginas

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const dados = Object.fromEntries(new FormData(form).entries());

        try {
            const resposta = await fetch("/api/ideias", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(dados)
            });

            if (resposta.ok) {
                alert("✅ Ideia enviada com sucesso!");
                form.reset();
            } else {
                alert("❌ Erro ao enviar ideia");
            }
        } catch (erro) {
            console.error(erro);
            alert("❌ Erro de conexão com o servidor");
        }
    });
});
