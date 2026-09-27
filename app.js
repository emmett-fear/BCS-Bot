function fmt(v,d=3){return v==null?"—":Number(v).toFixed(d)}
function rank(v){return v==null?"—":v}
function delta(now,old){
  if(now==null||old==null)return "";
  const d=old-now;
  return d>0?`↑${d}`:d<0?`↓${Math.abs(d)}`:"—";
}
function load(){
 const data=BCS_DATA, rows=[...data.rows].sort((a,b)=>(b.bcs_plus_score??-1)-(a.bcs_plus_score??-1));
 document.getElementById("meta").innerHTML=
  `<div class="badge">Week: ${data.week}</div><div class="badge">${(data.computer_systems||[]).length}/6 computers reporting</div>`;
 const tbody=document.querySelector("#table tbody"); tbody.innerHTML="";
 rows.slice(0,25).forEach(r=>{
  const tr=document.createElement("tr");
  const move=r.previous_bcs_plus_rank?delta(r.bcs_plus_rank,r.previous_bcs_plus_rank):"";
  tr.innerHTML=`
   <td class="primary-rank">${rank(r.bcs_plus_rank)} <span class="move">${move}</span></td>
   <td>${r.team}</td><td><strong>${fmt(r.bcs_plus_score)}</strong></td>
   <td>${r.marbles==null?"—":Number(r.marbles).toLocaleString()}</td><td>${fmt(r.marble_pct)}</td>
   <td>${rank(r.rank)}</td><td>${fmt(r.bcs_score)}</td><td>${fmt(r.computers)}</td><td>${rank(r.comp_rank)}</td>
   <td>${fmt(r.ap_pct)}</td><td>${rank(r.ap_rank)}</td><td>${fmt(r.coaches_pct)}</td><td>${rank(r.coaches_rank)}</td>`;
  tbody.appendChild(tr);
 });
}
load();
