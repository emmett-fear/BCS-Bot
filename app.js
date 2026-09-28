function fmt(v,d=3){return v==null?"—":Number(v).toFixed(d)}
function rank(v){return v==null?"—":v}
function delta(now,old){
  if(now==null||old==null)return "";
  const d=old-now;
  return d>0?`<span class="move up">&#9650;${d}</span>`:d<0?`<span class="move down">&#9660;${Math.abs(d)}</span>`:`<span class="move flat">&#9679;</span>`;
}

// Build the week list from the season archive when present (four weeks and
// counting, added by scripts/backfill_season.py + the weekly workflow).
// Fall back to just the single embedded current week so the page still
// works if season_data.js hasn't been generated yet.
function seasonWeeks(){
  if (typeof SEASON_DATA !== "undefined" && SEASON_DATA.weeks && SEASON_DATA.weeks.length) {
    return SEASON_DATA.weeks;
  }
  return [{
    week_number: 1,
    week_tag: BCS_DATA.week,
    label: `Week of ${BCS_DATA.week}`,
    computer_systems: BCS_DATA.computer_systems || [],
    rows: BCS_DATA.rows,
    is_current: true,
  }];
}

function renderWeek(week){
  const hasPlus = week.rows.some(r => r.bcs_plus_score != null);
  const rows = [...week.rows].sort((a,b) => {
    const plusDiff = (b.bcs_plus_score ?? -1) - (a.bcs_plus_score ?? -1);
    if (plusDiff !== 0) return plusDiff;
    return (a.rank ?? 999) - (b.rank ?? 999);
  });

  const systems = week.computer_systems || [];
  const badges = [
    `<span class="badge">${week.label}</span>`,
    `<span class="badge">${systems.length}/6 computer systems reporting</span>`,
  ];
  if (!hasPlus) {
    badges.push(`<span class="badge badge-warn">Marbles not yet available &mdash; Classic BCS only this week</span>`);
  }
  document.getElementById("meta").innerHTML = badges.join("");

  document.querySelector(".table-heading p").textContent = hasPlus
    ? "Sorted by BCS+. Classic BCS remains alongside it for comparison."
    : "College Football Marbles hadn't published standings yet this week, so BCS+ isn't calculated. Sorted by Classic BCS.";

  const tbody = document.querySelector("#table tbody");
  tbody.innerHTML = "";
  rows.slice(0, 25).forEach(r => {
    const tr = document.createElement("tr");
    const plusMove = delta(r.bcs_plus_rank, r.previous_bcs_plus_rank);
    const classicMove = delta(r.rank, r.previous_rank);
    tr.innerHTML = `
     <td class="primary-rank">${rank(r.bcs_plus_rank)} ${plusMove}</td>
     <td class="team-cell">${r.team}</td><td><strong>${fmt(r.bcs_plus_score)}</strong></td>
     <td>${r.marbles==null?"—":Number(r.marbles).toLocaleString()}</td><td>${fmt(r.marble_pct)}</td>
     <td>${rank(r.rank)} ${classicMove}</td><td>${fmt(r.bcs_score)}</td><td>${fmt(r.computers)}</td><td>${rank(r.comp_rank)}</td>
     <td>${fmt(r.ap_pct)}</td><td>${rank(r.ap_rank)}</td><td>${fmt(r.coaches_pct)}</td><td>${rank(r.coaches_rank)}</td>`;
    tbody.appendChild(tr);
  });
}

function buildWeekPicker(weeks){
  const picker = document.getElementById("week-picker");
  if (!picker) return;
  picker.innerHTML = weeks.map((w,i) =>
    `<option value="${i}">${w.label}${w.is_current ? " (current)" : ""}</option>`
  ).join("");
  picker.value = String(weeks.length - 1);
  picker.addEventListener("change", () => renderWeek(weeks[Number(picker.value)]));
}

function load(){
  const weeks = seasonWeeks();
  buildWeekPicker(weeks);
  renderWeek(weeks[weeks.length - 1]);
}
load();
