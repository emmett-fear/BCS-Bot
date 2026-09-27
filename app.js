function fmt(v, digits = 3) { return v == null ? "—" : Number(v).toFixed(digits); }
function rank(v) { return v == null ? "—" : v; }

function load() {
  const data = BCS_DATA;
  const rows = [...data.rows].sort((a, b) =>
    (b.bcs_plus_score ?? b.bcs_score) - (a.bcs_plus_score ?? a.bcs_score)
  );

  document.getElementById("meta").innerHTML =
    `<div class="badge">Week: ${data.week}</div>`;

  const tbody = document.querySelector("#table tbody");
  tbody.innerHTML = "";

  rows.slice(0, 25).forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="primary-rank">${rank(r.bcs_plus_rank)}</td>
      <td>${r.team}</td>
      <td><strong>${fmt(r.bcs_plus_score)}</strong></td>
      <td>${r.marbles == null ? "—" : Number(r.marbles).toLocaleString()}</td>
      <td>${fmt(r.marble_pct)}</td>
      <td>${rank(r.rank)}</td>
      <td>${fmt(r.bcs_score)}</td>
      <td>${fmt(r.computers)}</td>
      <td>${rank(r.comp_rank)}</td>
      <td>${fmt(r.ap_pct)}</td>
      <td>${rank(r.ap_rank)}</td>
      <td>${fmt(r.coaches_pct)}</td>
      <td>${rank(r.coaches_rank)}</td>
    `;
    tbody.appendChild(tr);
  });
}
load();
