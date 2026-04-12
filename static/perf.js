document.addEventListener("DOMContentLoaded", carregarIdeias);

async function carregarIdeias() {
    const tbody = document.querySelector("tbody");
    tbody.innerHTML = "";

    try {
        const resposta = await fetch("/api/performance/ideias");
        const ideias = await resposta.json();

        ideias.forEach(i => {
            const tr = document.createElement("tr");

            tr.innerHTML = `
                <td>${i.id}</td>
                <td>${i.nome}</td>
                <td>${i.matricula}</td>
                <td>${i.area}</td>
                <td>${i.descricao}</td>
                <td>
                    <select data-id="${i.id}">
                        <option ${i.status === "Aprovada" ? "selected" : ""}>Aprovada</option>
                        <option ${i.status === "Em análise" ? "selected" : ""}>Em análise</option>
                        <option ${i.status === "Reprovada" ? "selected" : ""}>Reprovada</option>
                    </select>
                </td>
                <td>
                    <input type="number" value="${i.pontuacao || 0}" data-id="${i.id}">
                </td>
                <td>
                    <button onclick="salvar(${i.id})">💾</button>
                    <button onclick="excluir(${i.id})">🗑️</button>
                </td>
            `;

            tbody.appendChild(tr);
        });

    } catch (e) {
        console.error(e);
        alert("Erro ao carregar ideias");
    }
}

async function salvar(id) {
    const status = document.querySelector(`select[data-id="${id}"]`).value;
    const pontuacao = document.querySelector(`input[data-id="${id}"]`).value;

    await fetch("/api/performance/avaliar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            id,
            status,
            pontuacao,
            avaliador: "Performance"
        })
    });

    alert("✅ Avaliação salva");
}

async function excluir(id) {
    if (!confirm("Deseja excluir esta ideia?")) return;

    await fetch(`/api/performance/excluir/${id}`, {
        method: "DELETE"
    });

    carregarIdeias();
}