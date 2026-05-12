document.addEventListener("DOMContentLoaded", async () => {

    const senha = prompt("🔒 Digite a senha da Performance:");

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

    const res = await fetch("/api/performance/ideias");
    const ideias = await res.json();

    ideias.forEach(i => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${i.id}</td>
            <td>${i.nome}</td>
            <td>${i.matricula}</td>
            <td>${i.area}</td>
            <td>${i.descricao}</td>

            <td>
                <select data-impacto="${i.id}">
                    <option>Material</option>
                    <option>Processo</option>
                    <option>Qualidade</option>
                    <option>Segurança</option>
                    <option>Custo</option>
                </select>
            </td>

            ${inputs(i.id, "beneficio")}
            ${inputs(i.id, "esforco")}

            <td id="beneficio-${i.id}">0</td>
            <td id="esforco-${i.id}">0</td>
            <td id="prioridade-${i.id}">0</td>

            <td>
                <select data-status="${i.id}">
                    <option>Em análise</option>
                    <option>Aprovada</option>
                    <option>Reprovada</option>
                </select>
            </td>

            <td>
                <button onclick="salvar(${i.id})">💾</button>
                <button onclick="deletar(${i.id})">🗑️</button>
            </td>
        `;

        tbody.appendChild(tr);
    });
}

function selectOpcao(id, tipo) {
    return `
        <select data-${tipo}="${id}" onchange="calcular(${id})">
            <option value="0">-</option>
            <option value="3">Baixo</option>
            <option value="6">Médio</option>
            <option value="9">Alto</option>
        </select>
    `;
}

function inputs(id, tipo) {
    return `
        <td>${selectOpcao(id, tipo)}</td>
        <td>${selectOpcao(id, tipo)}</td>
        <td>${selectOpcao(id, tipo)}</td>
        <td>${selectOpcao(id, tipo)}</td>
        <td>${selectOpcao(id, tipo)}</td>
    `;
}

function calcular(id) {

    const b = Array.from(document.querySelectorAll(`[data-beneficio="${id}"]`)).map(i => Number(i.value) || 0);
    const e = Array.from(document.querySelectorAll(`[data-esforco="${id}"]`)).map(i => Number(i.value) || 0);

    const ben = (b[0]*0.2)+(b[1]*0.2)+(b[2]*0.1)+(b[3]*0.5);
    const esf = (e[0]*0.2)+(e[1]*0.25)+(e[2]*0.3)+(e[3]*0.05)+(e[4]*0.2);
    const total = ben + esf;

    document.getElementById(`beneficio-${id}`).innerText = ben.toFixed(2);
    document.getElementById(`esforco-${id}`).innerText = esf.toFixed(2);
    document.getElementById(`prioridade-${id}`).innerText = total.toFixed(2);
}

async function salvar(id) {

    const status = document.querySelector(`[data-status="${id}"]`).value;
    const impacto = document.querySelector(`[data-impacto="${id}"]`).value;

    const b = Array.from(document.querySelectorAll(`[data-beneficio="${id}"]`)).map(i => i.value);
    const e = Array.from(document.querySelectorAll(`[data-esforco="${id}"]`)).map(i => i.value);

    const totalBen = document.getElementById(`beneficio-${id}`).innerText;
    const totalEsf = document.getElementById(`esforco-${id}`).innerText;
    const prioridade = document.getElementById(`prioridade-${id}`).innerText;

    const payload = {
        id,
        status,
        impacto,
        pontuacao: prioridade,

        qualidade: b[0],
        seguranca: b[1],
        kpi: b[2],
        saving_beneficio: b[3],
        norma: b[4],

        custo: e[0],
        tempo: e[1],
        treinamento: e[2],
        logistica: e[3],
        mudanca: e[4],

        total_beneficio: totalBen,
        total_esforco: totalEsf,
        prioridade: prioridade
    };

    console.log("ENVIANDO:", payload);   

    const resp = await fetch("/api/performance/avaliar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    if (resp.ok) {
        alert("✅ Salvou completo!");
    } else {
        alert("❌ erro");
    }
}

async function deletar(id) {

    const confirmar = confirm("Tem certeza que deseja excluir essa ideia?");

    if (!confirmar) return;

    try {
        const resp = await fetch(`/api/performance/deletar/${id}`, {
            method: "DELETE"
        });

        if (resp.ok) {
            alert("🗑️ Ideia excluída com sucesso!");
            carregarIdeias(); 
        } else {
            alert("❌ Erro ao excluir");
        }

    } catch (err) {
        console.error(err);
        alert("❌ Erro de conexão");
    }
}
