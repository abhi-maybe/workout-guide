#!/usr/bin/env python3
"""Rebuild workout-guide index.html — 6-day split, Monday OFF (train Tue→Sun).

Reuses the deployed <style> block verbatim; only the split, tables, badges, copy change.
"""
import re, pathlib

SRC = pathlib.Path("/opt/data/workout-guide/index.html")
OUT = SRC
original = SRC.read_text()
style_block = re.search(r"<style>.*?</style>", original, re.S).group(0)
# strip CSS injected by a previous run of this generator so rebuilds never stack duplicates
style_block = re.sub(r"\n  /\* ═══ INJECTED:BUILD ═══ \*/.*?(?=</style>)", "\n", style_block, flags=re.S)

EXTRA_CSS = """
  /* ═══ INJECTED:BUILD ═══ */
  /* ═══ DARK PALETTE (overrides the original light :root) ═══ */
  :root {
    --bg: #0a0b0e;
    --surface: #14171d;
    --surface-hover: #1b1f27;
    --border: #262b34;
    --border-light: #1d222a;
    --text: #eceff3;
    --text-secondary: #a8b1be;
    --text-tertiary: #8590a0;
    --accent: #4dabf7;
    --accent-hover: #74c0fc;
    --accent-light: rgba(77, 171, 247, 0.14);
    --green: #51cf66;
    --green-light: rgba(81, 207, 102, 0.14);
    --orange: #ff922b;
    --orange-light: rgba(255, 146, 43, 0.14);
    --red: #ff6b6b;
    --red-light: rgba(255, 107, 107, 0.14);
    --teal: #20c997;
    --teal-light: rgba(32, 201, 151, 0.14);
    --pink: #f06595;
    --pink-light: rgba(240, 101, 149, 0.14);
    --yellow: #ffc078;
    --yellow-light: rgba(255, 192, 120, 0.14);
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.50);
    --shadow-md: 0 2px 10px rgba(0, 0, 0, 0.55);
    --shadow-lg: 0 8px 28px rgba(0, 0, 0, 0.60);
  }
  body { background-image: radial-gradient(900px 420px at 50% -12%, rgba(77, 171, 247, 0.10), transparent 70%);
         background-repeat: no-repeat; }
  .hero h1 { background: linear-gradient(180deg, #ffffff 0%, #b9c2ce 100%); -webkit-background-clip: text;
             background-clip: text; -webkit-text-fill-color: transparent; }
  .day-number { border: 1px solid var(--border); }
  .exercise-table thead th { background: #0e1116; }
  .day-header { background: linear-gradient(180deg, #171b22, #12151a); }
  .day-card { background: var(--surface); }
  .ex-check.checked::after, .ab-check.checked::after { color: #05230d; }
  .footer { color: var(--text-tertiary); }
  .day-complete-banner { background: rgba(81, 207, 102, 0.12); }
  ::selection { background: rgba(77, 171, 247, 0.28); }

  /* ═══ INTENSITY BADGES ═══ */
  .day-badge.hv { background: var(--red-light); color: var(--red); }
  .day-badge.md { background: var(--accent-light); color: var(--accent); }
  .day-badge.lt { background: var(--green-light); color: var(--green); }
  .cond-block { padding: 18px 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }
  .cond-item { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px; }
  .cond-item h4 { font-size: 12px; font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
  .cond-item p { font-size: 11px; color: var(--text-tertiary); line-height: 1.5; }
  .day-banner-note { padding: 12px 20px; font-size: 12px; color: var(--text-secondary); background: var(--accent-light); border-top: 1px solid var(--border); }
  .day-banner-note b { color: var(--accent); }

  /* print stays on paper-friendly light */
  @media print {
    :root { --bg: #fff; --surface: #fff; --surface-hover: #fff; --border: #ccc; --border-light: #ddd;
            --text: #000; --text-secondary: #333; --text-tertiary: #666; --accent: #1c7ed6; }
    body { background-image: none; }
    .hero h1 { background: none; -webkit-text-fill-color: #000; color: #000; }
    .day-header, .exercise-table thead th { background: #f4f4f4; }
  }
"""

# (num, cls, title, weekday, badge, badge_cls, focus, exercises, (abs_title, abs_items) | None, strap, done)
DAYS = [
 (1, "day-rest", "Rest Day — Off", "Monday", "Off", "lt",
  "<b>Monday is the recovery anchor.</b> Sunday's hinge day is the hardest session of the week — this is where it gets absorbed. Walk, stretch, eat, sleep. No lifting, no make-up session.",
  [], ("🌙 Recovery Checklist",
       [("Easy walk", "20–30 min"), ("Mobility — hips + T-spine", "10 min"),
        ("Sleep", "8 h target"), ("Creatine", "3 g")]),
  None, "Monday banked — recovery is training"),

 (2, "day-upper", "Push A — Chest & Shoulder Strength", "Tuesday", "Heavy", "hv",
  "First session off a full rest day — you are freshest here, so this is the heaviest pressing of the week.",
  [("Barbell Bench Press (Wide Grip)", 4, "5–6", "3 min", "Elbows ~75°, deep stretch"),
   ("Incline Barbell Press", 4, "6–8", "2 min", "30–45°, upper chest width"),
   ("Overhead Press", 4, "6–8", "2 min", "Standing, ribs down, no leg drive"),
   ("Cable Chest Fly (Low to High)", 3, "12–15", "60 sec", "Outer + upper chest squeeze"),
   ("Lateral Raises", 5, "15–20", "60 sec", "Key for broad shoulders"),
   ("Overhead Triceps Extension", 3, "12–15", "60 sec", "Long head = arm thickness"),
   ("Rope Pushdown", 3, "12–15", "60 sec", "Elbows pinned, spread at the bottom"),
   ("Reverse Barbell Curl", 3, "12–15", "60 sec", "Forearm thickness")],
  ("🔥 Core Finisher", [("Hanging Leg Raises", "3 × 12"), ("Cable Crunches", "3 × 15")]),
  None, "Day 2 Complete — Chest and shoulders loaded!"),

 (3, "day-pull", "Pull A — Back Width & Thickness", "Wednesday", "Heavy", "hv",
  "Pull heavy while pressing fatigue is still low.",
  [("Weighted Pull-Ups (Wide Grip)", 4, "6–8", "90 sec", "Lat width = V-taper"),
   ("Barbell Rows", 4, "6–8", "2 min", "Back thickness base"),
   ("Cable Rows (Wide Grip)", 3, "10–12", "90 sec", "Squeeze mid-back, no shrug"),
   ("Face Pulls", 4, "15–20", "60 sec", "Rear delt = shoulder roundness"),
   ("Incline DB Curl", 3, "12", "60 sec", "Bicep peak, arms behind body"),
   ("Hammer Curls", 3, "12–15", "60 sec", "Brachialis = arm width"),
   ("Behind-the-Back Wrist Curl", 3, "15–20", "45 sec", "Forearm flexors")],
  ("🔥 Core Finisher", [("Ab Wheel Rollout", "3 × 10"), ("Reverse Crunches", "3 × 15")]),
  "⚠️ Use straps on rows & pull-ups so back fails before grip. Train forearms after.",
  "Day 3 Complete — Back is fried!"),

 (4, "day-lower", "Legs A — Quad Strength", "Thursday", "Heavy", "hv",
  "Squat first, everything else supports it. Three clear days before the hinge day.",
  [("Barbell Back Squat", 5, "5–6", "3 min", "Main leg mass builder, full depth"),
   ("Leg Press (Wide & Low Feet)", 4, "8–10", "90 sec", "Wide stance hits inner quads"),
   ("Leg Extension", 3, "12–15", "60 sec", "Squeeze at the top, 2 sec hold"),
   ("Lying Leg Curl", 3, "10–12", "60 sec", "Hamstring fullness, slow negative"),
   ("Standing Calf Raises", 4, "15–20", "60 sec", "Heavy, full ROM"),
   ("Tibialis Raises", 3, "20", "45 sec", "Full lower leg development")],
  ("🔥 Core Finisher", [("Weighted Crunches", "3 × 15"), ("Dead Bug", "3 × 10")]),
  None, "Day 4 Complete — Quads wrecked!"),

 (5, "day-push", "Shoulders & Upper Chest", "Friday", "Moderate", "md",
  "Second push exposure — pump work, not max singles. Two days from the heavy hinge day.",
  [("Incline DB Press", 4, "8–10", "90 sec", "Primary chest width builder"),
   ("DB Shoulder Press", 4, "10–12", "90 sec", "Shoulder cap size"),
   ("Cable Lateral Raises", 5, "15–20", "60 sec", "Cable = constant tension"),
   ("Cable Rear Delt Fly", 4, "15", "60 sec", "Cables crossed, pull wide"),
   ("Cable Fly (High to Low)", 3, "12–15", "60 sec", "Stretches outer chest fibers"),
   ("EZ-Bar Skullcrusher", 3, "10–12", "60 sec", "Lower behind the forehead")],
  ("🔥 Core Finisher", [("Decline Crunches", "3 × 15"), ("Pallof Press", "3 × 12/side")]),
  "Keep 1–2 reps in reserve today.",
  "Day 5 Complete — Delts pumped!"),

 (6, "day-pull", "Back Detail, Arms & Grip", "Saturday", "Moderate", "md",
  "Rows and pulldowns at moderate load; arms and grip take the beating.",
  [("Lat Pulldown (Wide Grip)", 4, "10–12", "90 sec", "Lean back slightly, drive elbows down"),
   ("Chest-Supported Row", 4, "10–12", "90 sec", "Chest glued to pad, no momentum"),
   ("Single Arm DB Row", 3, "10–12/arm", "90 sec", "Full ROM stretch"),
   ("Straight-Arm Pulldown", 2, "12–15", "60 sec", "Lat isolation finisher"),
   ("Barbell Shrugs", 3, "12–15", "60 sec", "Straight up, 1 sec hold"),
   ("Preacher Curl (EZ Bar)", 3, "10–12", "60 sec", "No swing, full stretch"),
   ("Reverse Wrist Curl (DB)", 3, "15–20", "45 sec", "Extensors — don't skip"),
   ("Dead Hang (Pull-up Bar)", 2, "Max hold", "45 sec", "Grip endurance + shoulder stretch")],
  ("🔥 Core Finisher", [("Cable Crunches", "3 × 15"), ("Plank", "3 × 45 sec")]),
  "Straps off for the last row set and shrugs — let grip work.",
  "Day 6 Complete — Back and arms cooked!"),

 (7, "day-legs", "Legs B — Posterior Chain & Glutes", "Sunday", "Heavy", "hv",
  "Hardest session of the week, deliberately placed the day before Monday off.",
  [("Romanian Deadlift", 4, "6–8", "2 min", "Hamstring + glute thickness, bar shaves thighs"),
   ("Hack Squat", 4, "10–12", "2 min", "Best quad mass builder"),
   ("Bulgarian Split Squat", 3, "10–12/leg", "90 sec", "Fixes imbalance, quad sweep"),
   ("Hip Thrusts", 4, "12–15", "60 sec", "Glute size = leg appearance, 1 sec lockout"),
   ("Lying Leg Curl", 4, "12–15", "60 sec", "Hamstring fullness"),
   ("Seated Calf Raises", 5, "15–20", "60 sec", "Calves need high volume + stretch"),
   ("Farmer's Walk", 4, "35–40 sec", "60 sec", "Best forearm + grip builder")],
  ("🔥 Core Finisher", [("Hanging Knee Raises", "3 × 12"), ("Plank w/ Shoulder Taps", "3 × 20")]),
  None, "Day 7 Complete — Monday off earned! 🔥"),
]


def table(exs):
    rows = "\n".join(
        f'        <tr><td class="check-cell"><div class="ex-check" onclick="toggleCheck(event,this)"></div></td>'
        f'<td>{n}</td><td class="sets-cell">{s}</td><td class="reps-cell">{r}</td>'
        f'<td class="rest-cell">{rest}</td><td class="notes-cell">{note}</td></tr>'
        for n, s, r, rest, note in exs)
    return ('    <table class="exercise-table">\n'
            '      <thead><tr><th></th><th>Exercise</th><th>Sets</th><th>Reps</th><th>Rest</th><th>Notes</th></tr></thead>\n'
            f'      <tbody>\n{rows}\n      </tbody>\n    </table>')


def abs_block(spec):
    if not spec:
        return ""
    title, items = spec
    cells = "\n".join(
        f'      <div class="ab-exercise" onclick="toggleAb(this)"><div class="ab-check"></div>'
        f'<span class="name">{n}</span><span class="detail">{d}</span></div>' for n, d in items)
    return (f'    <div class="ab-finisher"><div class="ab-finisher-title">{title}</div>'
            f'<div class="ab-exercises">\n{cells}\n    </div></div>')


cards = []
for num, cls, title, wd, badge, bcls, focus, exs, abspec, strap, done in DAYS:
    set_total = sum(e[1] for e in exs)
    meta = f"{len(exs)} exercises · {set_total} sets" if exs else "off — walk, mobility, sleep"
    parts = [f'''  <!-- ═══ DAY {num} — {title.upper()} ═══ -->
  <div class="day-card {cls}" data-day="{num}">
    <div class="day-header">
      <div class="day-header-left"><div class="day-number">{num}</div><div class="day-info"><h3>{title}</h3><span class="day-label">{wd} · {meta}</span></div></div>
      <span class="day-badge {bcls}">{badge}</span>
    </div>
    <div class="day-banner-note">{focus}</div>''']
    if exs:
        parts.append(table(exs))
    parts.append(abs_block(abspec))
    if strap:
        parts.append(f'    <div class="strap-note">{strap}</div>')
    parts.append(f'    <div class="day-complete-banner">✅ {done}!</div>\n  </div>')
    cards.append("\n".join(p for p in parts if p))

GOALS = """
    <table class="goal-table">
      <thead><tr><th>Goal</th><th>How It's Trained</th><th>Frequency</th></tr></thead>
      <tbody>
        <tr><td>Wider Chest</td><td>Incline press + cable flyes (Tue Push A + Friday)</td><td>2× / week</td></tr>
        <tr><td>Abs</td><td>Core finisher on all six lifting days</td><td>6× / week</td></tr>
        <tr><td>Big Legs</td><td>Quad day (Thu) + posterior chain day (Sun)</td><td>2× / week</td></tr>
        <tr><td>Broad Shoulders</td><td>10 sets lateral raises + 8 sets rear delt</td><td>2× / week</td></tr>
        <tr><td>Bigger Forearms</td><td>Reverse curls, wrist work, farmer's walk, dead hangs</td><td>4× / week</td></tr>
      </tbody>
    </table>"""

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>6-Day Workout Plan</title>
{style_block.replace('</style>', EXTRA_CSS + '</style>')}
</head>
<body>

<div class="confetti-container" id="confettiContainer"></div>

<div class="container">

  <div class="hero">
    <div class="hero-icon">🏋️</div>
    <h1>6-Day Split</h1>
    <p class="subtitle">Monday off · <strong>Train Tuesday → Sunday · Strength + Hypertrophy</strong></p>
    <div class="goals-strip">
      <span class="goal-tag">Wider Chest</span>
      <span class="goal-tag">Abs</span>
      <span class="goal-tag">Big Legs</span>
      <span class="goal-tag">Broad Shoulders</span>
      <span class="goal-tag">Bigger Forearms</span>
    </div>
  </div>

  <div class="day-switcher" id="daySwitcher"></div>

  <div class="progress-section">
    <span class="progress-label">Today's Progress</span>
    <div class="progress-bar-track"><div class="progress-bar-fill" id="progressFill"></div></div>
    <span class="progress-pct" id="progressPct">0%</span>
  </div>

{chr(10).join(cards)}

  <div class="extras-toggle">
    <button class="extras-btn" onclick="toggleExtras(this)">📋 Rules, Recovery, Supplements & Nutrition <span class="chevron">▼</span></button>
  </div>
  <div class="extras-content" id="extrasContent">
    <div class="section-title"><span class="icon">📈</span> Progressive Overload</div>
    <div class="rules-grid">
      <div class="rule-card"><span class="rule-icon">⬆️</span><div><h4>Add Weight</h4><p>+2.5–5 kg on compounds every 1–2 weeks, only when the top of the rep range is clean</p></div></div>
      <div class="rule-card"><span class="rule-icon">🎯</span><div><h4>Rep Target</h4><p>Hit top of rep range on every set → increase weight next session</p></div></div>
      <div class="rule-card"><span class="rule-icon">📓</span><div><h4>Track Everything</h4><p>Logbook or app — non-negotiable. No numbers, no progression</p></div></div>
      <div class="rule-card"><span class="rule-icon">😴</span><div><h4>Sleep</h4><p>7–9 hours, and Monday is not a training day — it is a recovery day</p></div></div>
    </div>

    <div class="section-title"><span class="icon">⚙️</span> Why Monday Off, Midweek On</div>
    <div class="rules-grid">
      <div class="rule-card"><span class="rule-icon">🔁</span><div><h4>72-Hour Spacing</h4><p>Every muscle is trained twice with ≥3 days between hits: chest Tue/Fri, back Wed/Sat, legs Thu/Sun</p></div></div>
      <div class="rule-card"><span class="rule-icon">🪫</span><div><h4>Deload Every 5th Week</h4><p>Cut sets by 40%, load to ~70%, keep the movements. Six sessions a week needs a scheduled exit ramp</p></div></div>
      <div class="rule-card"><span class="rule-icon">📉</span><div><h4>Autoregulate</h4><p>Resting HR +7 bpm, or under 6 h sleep → drop the top set and take 20% off the bar</p></div></div>
      <div class="rule-card"><span class="rule-icon">🚫</span><div><h4>No Grinding</h4><p>Never take squats, RDLs or hip thrusts to failure. Keep 1–2 reps in reserve everywhere</p></div></div>
      <div class="rule-card"><span class="rule-icon">⏱️</span><div><h4>Cap the Session</h4><p>75 min hard ceiling. Past that you are adding fatigue, not stimulus</p></div></div>
      <div class="rule-card"><span class="rule-icon">🩹</span><div><h4>Don't Stack Mondays</h4><p>Missed a session? Skip it, don't train Tue and Wed back to back — that breaks the 72 h spacing that makes this split work</p></div></div>
    </div>

    <div class="section-title"><span class="icon">💊</span> Supplement Protocol</div>
    <div class="supplement-grid">
      <div class="supp-card supp-morning"><div class="supp-icon">🌅</div><div><h4>Morning</h4><p>Take with breakfast</p><div class="dose">Creatine — ½ scoop (3g)</div></div></div>
      <div class="supp-card supp-workout"><div class="supp-icon">🏋️</div><div><h4>Post-Workout</h4><p>With 400ml milk</p><div class="dose">Mass Gainer — 2 scoops</div></div></div>
      <div class="supp-card supp-bed"><div class="supp-icon">🌙</div><div><h4>Before Bed (Optional)</h4><p>Extra calories for surplus</p><div class="dose">1 scoop Mass Gainer or whole food</div></div></div>
    </div>

    <div class="section-title"><span class="icon">🍽️</span> Nutrition Targets</div>
    <div class="nutrition-grid">
      <div class="nutri-card nutri-cal"><div class="icon">🔥</div><div class="label">Daily Calories</div><div class="value">3,000 – 3,300</div><div class="unit">kcal · keep it flat on Monday too</div></div>
      <div class="nutri-card nutri-pro"><div class="icon">🥩</div><div class="label">Protein</div><div class="value">150 – 165g</div><div class="unit">per day</div></div>
      <div class="nutri-card"><div class="icon">🍗</div><div class="label">Pre-Workout</div><div class="value">Rice + Chicken</div><div class="unit">90 min before</div></div>
      <div class="nutri-card"><div class="icon">🥤</div><div class="label">Post-Workout</div><div class="value">~430–500</div><div class="unit">kcal · 35–40g protein</div></div>
    </div>

    <div class="section-title"><span class="icon">🎯</span> Goal Tracker</div>
{GOALS}
  </div>

  <div class="footer">Generated by Hermes ⚡ · 6-day split · Monday off · Progressive overload wins</div>
</div>

<script>
const jsDay = new Date().getDay();
const today = jsDay === 0 ? 7 : jsDay;

const dayNames = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const switcher = document.getElementById('daySwitcher');
for (let i = 1; i <= 7; i++) {{
  const btn = document.createElement('div');
  btn.className = 'day-btn' + (i === today ? ' today' : '');
  btn.dataset.day = i;
  btn.innerHTML = `${{i}}<span class="day-name">${{dayNames[i]}}</span>`;
  btn.onclick = () => switchDay(i);
  switcher.appendChild(btn);
}}

let currentDay = today;
function switchDay(day) {{
  currentDay = day;
  document.querySelectorAll('.day-btn').forEach(b => b.classList.toggle('active', parseInt(b.dataset.day) === day));
  document.querySelectorAll('.day-card').forEach(c => c.classList.toggle('visible', parseInt(c.dataset.day) === day));
  updateProgress();
}}
switchDay(today);

function toggleCheck(event, el) {{
  event.stopPropagation();
  el.classList.toggle('checked');
  const row = el.closest('tr');
  row.classList.toggle('row-done', el.classList.contains('checked'));
  updateProgress();
  checkDayComplete(row.closest('.day-card'));
}}

function toggleAb(el) {{
  const check = el.querySelector('.ab-check');
  check.classList.toggle('checked');
  el.classList.toggle('done', check.classList.contains('checked'));
  updateProgress();
  checkDayComplete(el.closest('.day-card'));
}}

function checkDayComplete(dayCard) {{
  const allChecks = dayCard.querySelectorAll('.ex-check, .ab-check');
  if (allChecks.length === 0) return;
  const checked = dayCard.querySelectorAll('.ex-check.checked, .ab-check.checked');
  const banner = dayCard.querySelector('.day-complete-banner');
  const navBtn = document.querySelector(`.day-btn[data-day="${{dayCard.dataset.day}}"]`);
  if (checked.length === allChecks.length) {{
    banner.classList.add('show');
    dayCard.classList.add('completed-day');
    if (navBtn) navBtn.classList.add('completed');
    fireConfetti();
  }} else {{
    banner.classList.remove('show');
    dayCard.classList.remove('completed-day');
    if (navBtn) navBtn.classList.remove('completed');
  }}
}}

function updateProgress() {{
  const card = document.querySelector(`.day-card[data-day="${{currentDay}}"]`);
  if (!card) return;
  const allChecks = card.querySelectorAll('.ex-check, .ab-check');
  const checked = card.querySelectorAll('.ex-check.checked, .ab-check.checked');
  const pct = allChecks.length > 0 ? Math.round((checked.length / allChecks.length) * 100) : 0;
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('progressPct').textContent = pct + '%';
}}

function toggleExtras(btn) {{
  btn.classList.toggle('open');
  document.getElementById('extrasContent').classList.toggle('open');
}}

function fireConfetti() {{
  const container = document.getElementById('confettiContainer');
  const colors = ['#228be6', '#37b24d', '#f76707', '#e03131', '#0ca678', '#f59f00'];
  for (let i = 0; i < 30; i++) {{
    const piece = document.createElement('div');
    piece.className = 'confetti-piece';
    piece.style.left = Math.random() * 100 + '%';
    piece.style.top = '-10px';
    piece.style.background = colors[Math.floor(Math.random() * colors.length)];
    piece.style.animationDelay = Math.random() * 0.4 + 's';
    piece.style.animationDuration = (1 + Math.random()) + 's';
    container.appendChild(piece);
    setTimeout(() => piece.remove(), 2000);
  }}
}}

function saveState() {{
  const state = {{}};
  document.querySelectorAll('.day-card').forEach(card => {{
    const day = card.dataset.day;
    state[day] = {{
      exChecks: [...card.querySelectorAll('.ex-check')].map(c => c.classList.contains('checked')),
      abChecks: [...card.querySelectorAll('.ab-check')].map(c => c.classList.contains('checked'))
    }};
  }});
  try {{ localStorage.setItem('workout-6day-v3', JSON.stringify(state)); }} catch (e) {{}}
}}

function loadState() {{
  try {{
    const state = JSON.parse(localStorage.getItem('workout-6day-v3'));
    if (!state) return;
    Object.entries(state).forEach(([day, data]) => {{
      const card = document.querySelector(`.day-card[data-day="${{day}}"]`);
      if (!card) return;
      data.exChecks.forEach((checked, i) => {{
        if (checked) {{ const el = card.querySelectorAll('.ex-check')[i]; if (el) {{ el.classList.add('checked'); el.closest('tr').classList.add('row-done'); }} }}
      }});
      data.abChecks.forEach((checked, i) => {{
        if (checked) {{ const el = card.querySelectorAll('.ab-check')[i]; if (el) {{ el.classList.add('checked'); el.closest('.ab-exercise').classList.add('done'); }} }}
      }});
      checkDayComplete(card);
    }});
    updateProgress();
  }} catch(e) {{}}
}}

document.addEventListener('click', () => setTimeout(saveState, 100));
loadState();
</script>

</body>
</html>
"""

OUT.write_text(HTML)
total = sum(sum(e[1] for e in d[7]) for d in DAYS)
print(f"wrote {OUT}  {len(HTML)//1024} KB · lifting days={sum(1 for d in DAYS if d[7])} · sets/week={total}")
for d in DAYS:
    print(f"  day {d[0]} {d[3]:9s} {d[4]:8s} {d[2][:44]:46s} ex={len(d[7])} sets={sum(e[1] for e in d[7])}")
