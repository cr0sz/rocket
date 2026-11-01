"""Dashboard page for the AeroRL Bench API. Served at / and /dashboard."""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AeroRL Bench</title>
<style>
:root{--bg:#070b14;--panel:#0e1524;--panel2:#131c30;--line:rgba(255,255,255,.07);--text:#e8edf6;--muted:#8a96ab}
*{box-sizing:border-box;margin:0;padding:0}
body{min-height:100vh;color:var(--text);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:radial-gradient(1100px 560px at 85% -10%,rgba(91,155,213,.18),transparent 60%),radial-gradient(900px 480px at -10% 5%,rgba(61,220,151,.12),transparent 55%),var(--bg);background-attachment:fixed}
.wrap{max-width:1180px;margin:0 auto;padding:36px 20px 72px}
header{display:flex;align-items:center;gap:16px;margin-bottom:28px}
.logo{width:52px;height:52px;flex:none}
h1{font-size:30px;letter-spacing:-.02em;line-height:1.1}
.sub{color:var(--muted);font-size:14px;margin-top:4px}
.grid{display:grid;gap:16px;margin-bottom:16px}
.kpis{grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.charts{grid-template-columns:1fr 1fr}
@media(max-width:900px){.charts{grid-template-columns:1fr}}
.card{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:18px;padding:20px;min-width:0}
.k-label{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.09em}
.k-value{font-size:40px;font-weight:700;letter-spacing:-.03em;margin-top:6px;font-variant-numeric:tabular-nums;line-height:1.1}
.k-note{color:var(--muted);font-size:13px;margin-top:6px}
.card h2{font-size:17px;letter-spacing:-.01em}
.hint{color:var(--muted);font-size:13px;margin:2px 0 14px}
.box{position:relative;height:360px}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:8px}
.thead{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap}
select{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:8px 12px;font:inherit}
.tw{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);white-space:nowrap}
th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em;cursor:pointer;user-select:none}
th:hover{color:var(--text)}
tbody tr:hover{background:rgba(255,255,255,.03)}
.rate{display:flex;align-items:center;gap:10px;min-width:180px}
.rate .bar{flex:1;height:8px;border-radius:6px;background:rgba(255,255,255,.07);overflow:hidden}
.rate .bar i{display:block;height:100%;border-radius:6px}
.rate b{width:62px;text-align:right;font-weight:600}
footer{color:var(--muted);font-size:13px;margin-top:20px;display:flex;gap:18px;flex-wrap:wrap}
footer a{color:var(--muted)}
footer a:hover{color:var(--text)}
.err{border-color:rgba(255,99,99,.45);color:#ffb4b4;margin-bottom:16px}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <svg class="logo" viewBox="0 0 48 48" fill="none">
      <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3ddc97"/><stop offset="1" stop-color="#5b9bd5"/></linearGradient></defs>
      <rect width="48" height="48" rx="14" fill="url(#g)" opacity=".18"/>
      <path d="M24 8c5 4 7 10 7 17l-3 5h-8l-3-5c0-7 2-13 7-17z" fill="url(#g)"/>
      <circle cx="24" cy="21" r="3" fill="#070b14"/>
      <path d="M20 31l-4 5 4-1zM28 31l4 5-4-1z" fill="#5b9bd5"/>
      <path d="M22 33h4l-2 7z" fill="#e0b341"/>
    </svg>
    <div><h1>AeroRL Bench</h1><div class="sub" id="sub">Loading…</div></div>
  </header>
  <div id="err"></div>
  <section class="grid kpis" id="kpis"></section>
  <section class="grid charts">
    <div class="card"><h2>Landing rate by controller</h2><p class="hint">Bars show the average over seeds, white dots show individual seeds.</p><div class="box"><canvas id="c1"></canvas></div></div>
    <div class="card"><h2>Landing rate by start altitude</h2><p class="hint" id="hint2"></p><div class="box"><canvas id="c2"></canvas></div></div>
  </section>
  <section class="card">
    <div class="thead"><div><h2>All runs</h2><p class="hint">Click a column to sort.</p></div><select id="filter"></select></div>
    <div class="tw"><table><thead><tr id="thr"></tr></thead><tbody id="tb"></tbody></table></div>
  </section>
  <footer><span>Live from the API, every number is computed from stored landing counts</span><a href="/docs">API docs</a><a href="/summary">/summary</a><a href="/runs">/runs</a></footer>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
(function(){
'use strict';
const $ = s => document.querySelector(s);
const COLOR = {'random':'#8b93a1','hand_rule':'#e0b341','ppo|basic':'#5b9bd5','ppo|extended':'#3ddc97'};
const ORDER = ['random','hand_rule','ppo|basic','ppo|extended'];
const colorOf = k => COLOR[k] || '#c084fc';
const keyOf = (c, m) => c === 'ppo' ? 'ppo|' + m : c;
const labelOf = (c, m) => c === 'ppo' ? 'PPO · ' + m : c === 'hand_rule' ? 'Hand rule' : c === 'random' ? 'Random' : c;
const rateOf = r => r.landings / r.games * 100;

Chart.defaults.color = '#8a96ab';
Chart.defaults.font.family = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
Chart.defaults.borderColor = 'rgba(255,255,255,0.07)';
Chart.defaults.plugins.tooltip.backgroundColor = '#0b1220';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.12)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 10;

const valueLabels = {
  id: 'valueLabels',
  afterDatasetsDraw(chart) {
    const ctx = chart.ctx, meta = chart.getDatasetMeta(0);
    ctx.save();
    ctx.fillStyle = '#e8edf6';
    ctx.font = '600 13px system-ui, sans-serif';
    ctx.textAlign = 'center';
    meta.data.forEach((bar, i) => {
      ctx.fillText(chart.data.datasets[0].data[i].toFixed(1) + '%', bar.x, bar.y - 14);
    });
    ctx.restore();
  }
};

async function getJSON(u) {
  const r = await fetch(u);
  if (!r.ok) throw new Error(u + ' returned ' + r.status);
  return r.json();
}

function countUp(el, to, fmt) {
  const t0 = performance.now(), ms = 900;
  (function f(t) {
    const p = Math.min(1, (t - t0) / ms);
    el.textContent = fmt(to * (1 - Math.pow(1 - p, 3)));
    if (p < 1) requestAnimationFrame(f);
  })(t0);
}

function kpi(label, value, fmt, note) {
  const d = document.createElement('div'); d.className = 'card';
  const a = document.createElement('div'); a.className = 'k-label'; a.textContent = label;
  const b = document.createElement('div'); b.className = 'k-value'; b.textContent = fmt(0);
  const c = document.createElement('div'); c.className = 'k-note'; c.textContent = note;
  d.append(a, b, c);
  $('#kpis').append(d);
  countUp(b, value, fmt);
}

async function main() {
  const [summary, list] = await Promise.all([getJSON('/summary'), getJSON('/runs')]);
  const runs = await Promise.all(list.map(r => getJSON('/runs/' + r.id)));

  const sumBy = {};
  summary.forEach(s => { sumBy[keyOf(s.controller, s.obs_mode)] = s; });

  const groups = {};
  runs.forEach(r => {
    r.key = keyOf(r.controller, r.obs_mode);
    r.label = labelOf(r.controller, r.obs_mode);
    r.rate = rateOf(r);
    const g = groups[r.key] ??= {key: r.key, controller: r.controller, obs_mode: r.obs_mode, label: r.label, runs: []};
    g.runs.push(r);
  });
  const gl = Object.values(groups).sort((a, b) => {
    const i = ORDER.indexOf(a.key), j = ORDER.indexOf(b.key);
    return (i < 0 ? 99 : i) - (j < 0 ? 99 : j);
  });
  gl.forEach(g => {
    g.runs.sort((a, b) => (a.seed ?? 0) - (b.seed ?? 0));
    g.rates = g.runs.map(r => r.rate);
    const s = sumBy[g.key];
    g.avg = s ? s.avg_landing_rate : g.rates.reduce((a, b) => a + b, 0) / g.rates.length;
    const bm = {};
    g.runs.forEach(r => r.bands.forEach(b => {
      const m = bm[b.alt_min] ??= {min: b.alt_min, max: b.alt_max, games: 0, wins: 0};
      m.games += b.games; m.wins += b.landings;
    }));
    g.bands = Object.values(bm).sort((a, b) => a.min - b.min);
  });

  const gamesPer = runs[0].games, evalSeed = runs[0].eval_seed;
  const allBands = gl.flatMap(g => g.bands);
  const lo = Math.min(...allBands.map(b => b.min)), hi = Math.max(...allBands.map(b => b.max));
  const nBands = gl[0].bands.length, bandW = gl[0].bands[0].max - gl[0].bands[0].min;

  $('#sub').textContent = runs.length + ' runs · ' + gl.length + ' controllers · ' + gamesPer.toLocaleString('en-US') + ' games each';

  // KPI cards
  const best = gl.reduce((a, b) => b.avg > a.avg ? b : a);
  kpi('Best controller', best.avg, v => v.toFixed(1) + '%', best.label + ' · average of ' + best.runs.length + ' seeds');
  const basic = groups['ppo|basic'], ext = groups['ppo|extended'];
  if (basic && ext) kpi('Forecast inputs gain', ext.avg - basic.avg, v => (v >= 0 ? '+' : '') + v.toFixed(1) + ' pp', 'PPO extended vs PPO basic, average over seeds');
  kpi('Runs evaluated', runs.length, v => String(Math.round(v)), gl.length + ' controllers');
  kpi('Games per run', gamesPer, v => Math.round(v).toLocaleString('en-US'),
      'same start altitudes' + (evalSeed != null ? ' · eval seed ' + evalSeed : '') + ' · ' + lo + '–' + hi + ' m');

  // Chart 1: bars (average) + dots (seeds)
  const nmax = Math.max(...gl.map(g => g.rates.length));
  const dots = [];
  for (let i = 0; i < nmax; i++) {
    dots.push({type: 'line', label: 'seed', data: gl.map(g => g.rates[i] ?? null), showLine: false,
      pointRadius: 5, pointHoverRadius: 7, pointBackgroundColor: '#ffffff', pointBorderColor: '#070b14', pointBorderWidth: 1.5, order: 0});
  }
  const ymax = Math.min(100, Math.ceil((Math.max(...gl.map(g => g.avg)) + 10) / 10) * 10);
  new Chart($('#c1'), {
    type: 'bar',
    data: {
      labels: gl.map(g => g.label),
      datasets: [{label: 'average', data: gl.map(g => g.avg), backgroundColor: gl.map(g => colorOf(g.key)),
                  borderRadius: 10, borderSkipped: false, maxBarThickness: 76, order: 1}, ...dots]
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: {duration: 900},
      scales: {x: {grid: {display: false}}, y: {min: 0, max: ymax, ticks: {callback: v => v + '%'}}},
      plugins: {
        legend: {display: false},
        tooltip: {callbacks: {label: c => {
          const g = gl[c.dataIndex];
          if (c.datasetIndex === 0) return 'average ' + c.parsed.y.toFixed(2) + '% over ' + g.runs.length + ' run' + (g.runs.length > 1 ? 's' : '');
          const r = g.runs[c.datasetIndex - 1];
          return 'seed ' + (r.seed ?? '—') + ': ' + c.parsed.y.toFixed(2) + '% (' + r.landings + '/' + r.games + ')';
        }}}
      }
    },
    plugins: [valueLabels]
  });

  // Chart 2: landing rate by altitude band (pooled over seeds)
  $('#hint2').textContent = 'Each point pools the landings in a ' + bandW + ' m band (about ' + Math.round(gamesPer / nBands) +
    ' games per run), so a few points of difference between neighbouring bands is noise.';
  new Chart($('#c2'), {
    type: 'line',
    data: {
      labels: gl[0].bands.map(b => b.min + '–' + b.max),
      datasets: gl.map(g => ({
        label: g.label, data: g.bands.map(b => b.wins / b.games * 100), bands: g.bands, nruns: g.runs.length,
        borderColor: colorOf(g.key), backgroundColor: colorOf(g.key), tension: 0.35, borderWidth: 2.5, pointRadius: 3, pointHoverRadius: 6
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: {duration: 900},
      interaction: {mode: 'index', intersect: false},
      scales: {
        x: {grid: {display: false}, title: {display: true, text: 'start altitude (m)'}},
        y: {min: 0, max: 100, ticks: {callback: v => v + '%'}}
      },
      plugins: {
        legend: {position: 'bottom', labels: {usePointStyle: true, boxWidth: 8, padding: 16}},
        tooltip: {callbacks: {label: c => {
          const b = c.dataset.bands[c.dataIndex];
          return c.dataset.label + ': ' + c.parsed.y.toFixed(1) + '% (' + b.wins + '/' + b.games + (c.dataset.nruns > 1 ? ', ' + c.dataset.nruns + ' seeds pooled' : '') + ')';
        }}}
      }
    }
  });

  // Table
  const cols = [['id', '#'], ['label', 'Controller'], ['seed', 'Seed'], ['games', 'Games'], ['landings', 'Landings'], ['rate', 'Landing rate']];
  let sortKey = 'id', sortDir = 1, filt = 'all';
  const thr = $('#thr');
  cols.forEach(([k, t]) => {
    const th = document.createElement('th'); th.textContent = t;
    th.onclick = () => { if (sortKey === k) sortDir = -sortDir; else { sortKey = k; sortDir = 1; } render(); };
    thr.append(th);
  });
  const sel = $('#filter');
  [['all', 'All controllers'], ...gl.map(g => [g.key, g.label])].forEach(([v, t]) => {
    const o = document.createElement('option'); o.value = v; o.textContent = t; sel.append(o);
  });
  sel.onchange = () => { filt = sel.value; render(); };

  function render() {
    const tb = $('#tb'); tb.replaceChildren();
    runs.filter(r => filt === 'all' || r.key === filt).sort((a, b) => {
      const x = a[sortKey], y = b[sortKey];
      const c = typeof x === 'string' ? x.localeCompare(y) : (x ?? -1) - (y ?? -1);
      return c * sortDir || a.id - b.id;
    }).forEach(r => {
      const tr = document.createElement('tr');
      const cell = t => { const td = document.createElement('td'); td.textContent = t; tr.append(td); return td; };
      cell(r.id);
      const c = cell('');
      const dot = document.createElement('span'); dot.className = 'dot'; dot.style.background = colorOf(r.key);
      c.append(dot, document.createTextNode(r.label));
      cell(r.seed ?? '—'); cell(r.games.toLocaleString('en-US')); cell(r.landings.toLocaleString('en-US'));
      const td = document.createElement('td'), w = document.createElement('div'); w.className = 'rate';
      const bar = document.createElement('div'); bar.className = 'bar';
      const fill = document.createElement('i'); fill.style.width = r.rate + '%'; fill.style.background = colorOf(r.key); bar.append(fill);
      const num = document.createElement('b'); num.textContent = r.rate.toFixed(2) + '%';
      w.append(bar, num); td.append(w); tr.append(td);
      tb.append(tr);
    });
  }
  render();
}

main().catch(e => {
  const d = document.createElement('div'); d.className = 'card err';
  d.textContent = 'Could not load data: ' + e.message;
  $('#err').append(d);
  $('#sub').textContent = 'Failed to load';
});
})();
</script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return HTML
