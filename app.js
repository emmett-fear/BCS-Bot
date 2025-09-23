function load() {
  // Use embedded data from bcs_data.js
  const data = BCS_DATA;

  document.getElementById("meta").innerHTML =
    `<div class="badge">Week: ${data.week}</div>`;

  const tbody = document.querySelector("#table tbody");
  tbody.innerHTML = "";
  let maxCompInputs = 0;
  data.rows.forEach(r => { if (r.comp_inputs_used > maxCompInputs) maxCompInputs = r.comp_inputs_used; });

  data.rows.slice(0,25).forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.rank}</td>
      <td>${r.team}</td>
      <td>${r.bcs_score.toFixed(3)}</td>
      <td>${r.computers.toFixed(3)}</td>
      <td>${r.comp_rank || '—'}</td>
      <td>${r.ap_pct.toFixed(3)}</td>
      <td>${r.ap_rank || '—'}</td>
      <td>${r.coaches_pct.toFixed(3)}</td>
      <td>${r.coaches_rank || '—'}</td>
    `;
    tbody.appendChild(tr);
  });

  const badge = document.getElementById("badge");
  if (maxCompInputs < 6) {
    badge.innerHTML = `<span class="badge">Computers used this week: ${maxCompInputs}/6 (drop-high/low suspended until all 6 are live)</span>`;
  } else {
    badge.innerHTML = `<span class="badge">Computers used this week: 6/6 (drop-high/low applied)</span>`;
  }
}
load();


