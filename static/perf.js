document.addEventListener("DOMContentLoaded", async () => {
    const senha = prompt("🔒 Área restrita\nDigite a senha da Performance:");

    if (!senha) {
        alert("Acesso cancelado");
        window.location.href = "/";
        return;
    }

    const auth = await fetch("/api/performance/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ senha })
    });

    if (!auth.ok) {
        alert("❌ Senha incorreta");
        window.location.href = "/";
        return;
    }

    carregarIdeias();
});

async function carregarIdeias() {
    const tbody = document.getElementById("tabelaIdeias");
    tbody.innerHTML = "";

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
                    <option ${i.status==="Aprovada"?"selected":""}>Aprovada</option>
                    <option ${i.status==="Em análise"?"selected":""}>Em análise</option>
                    <option ${i.status==="Reprovada"?"selected":""}>Reprovada</option>
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
}

async function salvar(id) {
    const status = document.querySelector(`select[data-id="${id}"]`).value;
    const pontuacao = document.querySelector(`input[data-id="${id}"]`).value;

    await fetch("/api/performance/avaliar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id, status, pontuacao })
    });

    alert("✅ Avaliação salva");
}

async function excluir(id) {
    if (!confirm("Excluir ideia?")) return;

    await fetch(`/api/performance/excluir/${id}`, { method: "DELETE" });
    carregarIdeias();
}