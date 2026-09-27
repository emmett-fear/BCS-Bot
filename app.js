function load() {
  // Use embedded data from bcs_data.js
  const data = BCS_DATA;

  document.getElementById("meta").innerHTML =
    `<div class="badge">Week: ${data.week}</div>`;

      const tbody = document.querySelector("#table tbody");
      tbody.innerHTML = "";

      data.rows.slice(0,25).forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${r.rank}</td>
          <td>${r.team}</td>
          <td>${r.bcs_score.toFixed(3)}</td>\n          <td>${r.bcs_plus_rank || "—"}</td>\n          <td>${r.bcs_plus_score != null ? r.bcs_plus_score.toFixed(3) : "—"}</td>\n          <td>${r.marbles != null ? r.marbles.toFixed(1) : "—"}</td>\n          <td>${r.marble_pct != null ? r.marble_pct.toFixed(3) : "—"}</td>
          <td>${r.computers.toFixed(3)}</td>
          <td>${r.comp_rank || '—'}</td>
          <td>${r.ap_pct.toFixed(3)}</td>
          <td>${r.ap_rank || '—'}</td>
          <td>${r.coaches_pct.toFixed(3)}</td>
          <td>${r.coaches_rank || '—'}</td>
        `;
        tbody.appendChild(tr);
      });
}
load();


