"""ASTRABIO data layer.

* Check-in engine: manual measurements, personal baselines, status bands, guidance, score, streak.
* Mission time series: read from ``data/astronaut_data.csv`` (one row per mission day). If the file is
  missing it is regenerated from the demo formulas below, so you can swap in real data by replacing the
  CSV as long as the column names stay the same.
* ``state()``: builds the dashboard payload (body markers, modules, check-in) for a mission day.

ALL VALUES ARE DEMO DATA. RANGES ARE PLACEHOLDERS (general adult references). Replace them with
NASA HRP / flight-surgeon approved ranges before any real use.
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_CSV = ROOT / "data" / "astronaut_data.csv"

ORDER = ["normal", "watch", "warning", "critical"]
PEN = {"normal": 0, "watch": 5, "warning": 15, "critical": 30}
SRC = "PLACEHOLDER range: replace with a NASA HRP / flight surgeon source."

# --------------------------------------------------------------------------------------------------
# Check-in engine
# --------------------------------------------------------------------------------------------------
# n = normal range, w = watch range, c = warning range; outside c = critical. lim = typo guard.
SPEC = {
    "hr": dict(label="Resting heart rate", unit="bpm", n=(50, 90), w=(45, 100), c=(40, 120), lim=(20, 250), base=62, amp=2,
        why="Fluid shifts and deconditioning in microgravity change heart rate; stress and radiation can too.",
        how="Wrist sensor, or two fingers on the neck for 30 s (double it), after 5 min of rest.",
        act=("Keep up your exercise routine.", "Rest, drink water, and re-measure in 30 minutes.",
             "Rest 10 minutes and re-measure. If it stays out of range, contact the flight surgeon.")),
    "sys": dict(label="Blood pressure (systolic)", unit="mmHg", n=(90, 120), w=(85, 130), c=(80, 140), lim=(50, 250), base=112, amp=3,
        why="Blood pressure shifts as fluids move toward the head and the heart adapts to microgravity.",
        how="Upper-arm cuff, seated and rested for 5 minutes, arm at heart level.",
        act=("Keep up your exercise routine.", "Rest, reduce salt at the next meal, and re-measure in 30 minutes.",
             "Re-measure after 10 minutes of rest. If still out of range, contact the flight surgeon.")),
    "dia": dict(label="Blood pressure (diastolic)", unit="mmHg", n=(60, 80), w=(55, 85), c=(50, 90), lim=(30, 150), base=74, amp=2,
        why="Together with systolic pressure it shows how hard the heart and vessels are working in space.",
        how="Same reading as systolic: upper-arm cuff, seated, rested for 5 minutes.",
        act=("Keep up your exercise routine.", "Rest and re-measure in 30 minutes.",
             "Re-measure after 10 minutes of rest. If still out of range, contact the flight surgeon.")),
    "glucose": dict(label="Blood sugar", unit="mg/dL", n=(70, 100), w=(65, 125), c=(55, 180), lim=(20, 600), base=88, amp=4,
        why="Diet changes, stress and less activity can shift blood sugar on long missions.",
        how="Finger-prick meter before eating, with a fresh lancet and test strip.",
        act=("Keep balanced meals.", "Review recent meals, drink water, and re-test before the next meal.",
             "Re-test. If still out of range, contact the flight surgeon.")),
    "temp": dict(label="Body temperature", unit="C", n=(36.1, 37.2), w=(35.8, 37.8), c=(35.0, 38.5), lim=(30, 43), base=36.6, amp=0.15,
        why="Immune changes and infections in a closed habitat can show up first as a temperature change.",
        how="Forehead or ear thermometer, away from air vents, after 10 minutes of rest.",
        act=("Nothing needed.", "Rest, drink water, and re-measure in 1 hour. Limit close contact with crewmates.",
             "Isolate from crewmates if possible and contact the flight surgeon.")),
    "sleep": dict(label="Sleep last night", unit="hours", n=(7, 9), w=(6, 10), c=(4.5, 12), lim=(0, 24), base=7.3, amp=0.4,
        why="Light cycles, noise and isolation disrupt sleep, which affects mood, immunity and performance.",
        how="Wearable sleep tracker, or a sleep log. Enter last night's total hours.",
        act=("Keep your sleep schedule.", "Follow the circadian lighting schedule and a wind-down routine tonight.",
             "Tell the crew medical officer; the flight surgeon can review sleep support options.")),
    "mood": dict(label="Mood", unit="/10", n=(6, 10), w=(5, 10), c=(3.5, 10), lim=(1, 10), base=7.5, amp=0.5,
        why="Isolation and confinement affect mood, and low mood is a behavioral health warning sign.",
        how="Rate your mood from 1 (very low) to 10 (very good).",
        act=("Keep regular contact with crew and Earth.", "Try a breathing exercise or call someone from home.",
             "Please speak with a crew member and your flight surgeon soon.")),
}
# check-in indicator -> body marker id, and -> hazard module
LINK = {"heart": ["hr", "sys", "dia"], "brain": ["sleep", "mood"], "skin": ["temp"], "gut": ["glucose"]}
HAZ = {"gravity": ["hr", "sys", "dia"], "immune": ["temp", "glucose"], "mind": ["sleep", "mood"]}

LOGS, TODAY, STREAK = {}, set(), [6, False]


def reset():
    """Reset the in-memory check-in log to the demo baseline."""
    LOGS.clear()
    TODAY.clear()
    STREAK[:] = [6, False]
    for k, s in SPEC.items():
        LOGS[k] = [round(s["base"] + s["amp"] * math.sin(i * 1.3 + len(k)), 1) for i in range(13)] + [s["base"]]


def band(v, s):
    inr = lambda r: r[0] <= v <= r[1]
    return "normal" if inr(s["n"]) else "watch" if inr(s["w"]) else "warning" if inr(s["c"]) else "critical"


def item(k):
    s, ser = SPEC[k], LOGS[k]
    v, base = ser[-1], sum(ser[:10]) / 10
    dev = round((v - base) / base * 100, 1)
    lv = band(v, s)
    if lv == "normal" and abs(dev) >= 15:
        lv = "watch"  # personal baseline shift
    act = s["act"][0 if lv == "normal" else 1 if lv == "watch" else 2]
    if lv == "watch" and dev and abs(dev) >= 15 and band(v, s) == "normal":
        act = f"This is {abs(dev)}% away from your own baseline. " + s["act"][1]
    return dict(key=k, label=s["label"], unit=s["unit"], value=v, level=lv, series=ser[-14:], n=s["n"], src=SRC, why=s["why"],
                how=s["how"], action=act, escalate=lv in ("warning", "critical"), logged=k in TODAY, baseline=round(base, 1), dev=dev)


def log_value(k, v):
    if k not in SPEC:
        return False, f"{k}: unknown indicator"
    lo, hi = SPEC[k]["lim"]
    if not lo <= v <= hi:
        return False, f"{SPEC[k]['label']}: {v} looks like a typing error (expected {lo}-{hi} {SPEC[k]['unit']})."
    LOGS[k][-1] = v
    TODAY.add(k)
    if len(TODAY) == len(SPEC) and not STREAK[1]:
        STREAK[0] += 1
        STREAK[1] = True
    return True, ""


def checkin_state():
    items = [item(k) for k in SPEC]
    score = max(0, 100 - sum(PEN[i["level"]] for i in items))
    return dict(items=items, score=score, streak=STREAK[0], due=[i["label"] for i in items if not i["logged"]],
                escalate=any(i["escalate"] for i in items))


# --------------------------------------------------------------------------------------------------
# Mission time series (data/astronaut_data.csv)
# --------------------------------------------------------------------------------------------------
# column -> (demo formula of mission day d, decimal places). Used only to (re)generate the CSV.
DEMO_FORMULAS = {
    "brain_dose_msv": (lambda d: 5 + .9 * d, 1),
    "spine_bone_density_pct": (lambda d: 100 - .06 * d, 1),
    "marrow_dose_msv": (lambda d: 3 + 1.2 * d, 1),
    "muscle_mass_pct": (lambda d: 100 - .1 * d, 1),
    "resting_hr_bpm": (lambda d: 58 + .03 * d, 1),
    "microbiome_diversity": (lambda d: 4.2 - .008 * d, 2),
    "crp_mg_l": (lambda d: 1 + .02 * d, 1),
    "optic_disc_swelling_um": (lambda d: 1.1 * d, 1),
    "cumulative_dose_msv": (lambda d: 1.8 * d, 1),
    "dose_rate_transit_msv_day": (lambda d: 1.8 + .05 * math.sin(d / 3), 2),
    "dose_rate_surface_msv_day": (lambda d: .67 + .03 * math.sin(d / 5), 2),
    "lymphocytes_e9_l": (lambda d: 2.2 - .004 * d, 2),
    "infection_risk_pct": (lambda d: 4 + .05 * d, 1),
    "sleep_hours": (lambda d: 7.2 - .012 * d, 1),
    "stress_level": (lambda d: 30 + .15 * d, 1),
    "mood_score": (lambda d: 7.5 - .01 * d, 1),
    "days_since_earth_call": (lambda d: 3 + (d % 9), 0),
    "co2_ppm": (lambda d: 780 + 1.5 * d, 0),
    "oxygen_pct": (lambda d: 20.9 - .002 * d, 2),
    "habitat_temp_c": (lambda d: 22.4 + .3 * math.sin(d), 1),
    "humidity_pct": (lambda d: 45 + 2 * math.sin(d / 4), 0),
    "microbial_load_cfu_m3": (lambda d: 120 + .8 * d, 0),
}
GEN_DAYS = 180


def generate_csv(path=DATA_CSV, days=GEN_DAYS):
    """Write the demo mission dataset (one row per mission day)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = list(DEMO_FORMULAS)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["day"] + cols)
        for d in range(1, days + 1):
            row = []
            for c in cols:
                f, dp = DEMO_FORMULAS[c]
                row.append(round(f(d) + 0.02 * math.sin(d * 1.7) * abs(f(d)) * 0.1, dp))
            w.writerow([d] + row)


def load_series(path=DATA_CSV):
    """Return {column: [value for day 1, day 2, ...]} from the CSV (generated first if missing)."""
    if not Path(path).exists():
        generate_csv(Path(path))
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: int(r["day"]))
    missing = [c for c in DEMO_FORMULAS if c not in (rows[0] if rows else {})]
    if not rows or missing:
        raise ValueError(f"{path}: needs a 'day' column plus {missing or list(DEMO_FORMULAS)}")
    return {c: [float(r[c]) for r in rows] for c in DEMO_FORMULAS}


SERIES = load_series()
TOTAL_DAYS = len(SERIES["co2_ppm"])
DEFAULT_DAY = min(142, TOTAL_DAYS)


def lvl(v, w, o, c, hb=True):
    if not hb:
        v, w, o, c = -v, -w, -o, -c
    return "critical" if v >= c else "warning" if v >= o else "watch" if v >= w else "normal"


def mk(label, col, unit, w, o, c, hb=True, day=1):
    """One metric card: the last 14 days of a CSV column plus its status level."""
    s = SERIES[col][max(1, day - 13) - 1:day]
    return dict(label=label, value=s[-1], unit=unit, series=s, level=lvl(s[-1], w, o, c, hb))


def markers(day):
    # id, name, pos, hazards, label, csv column, unit, watch, warning, critical, higher_is_bad, explanation
    D = [
        ("brain", "Brain", (0, 1.74, .08), ["radiation", "mind"], "Brain dose", "brain_dose_msv", "mSv", 100, 200, 300, True,
         "Cosmic rays pass through the skull. Dose is tracked closely and sleep quality helps the brain recover."),
        ("spine", "Spine", (0, 1.22, -.06), ["radiation", "gravity"], "Lower-spine bone density", "spine_bone_density_pct", "% of baseline", 92, 88, 82, False,
         "Without gravity loading, bones slowly lose mineral. I'm seeing reduced bone density markers in your lower spine."),
        ("marrow", "Bone marrow", (.11, .93, .08), ["radiation"], "Marrow dose", "marrow_dose_msv", "mSv", 150, 250, 350, True,
         "Bone marrow makes blood cells and is sensitive to radiation, so we keep its dose well under the limit."),
        ("legs", "Legs", (.11, .62, .08), ["gravity"], "Leg muscle mass", "muscle_mass_pct", "% of baseline", 95, 88, 80, False,
         "Legs do less work in microgravity, so muscle shrinks without resistance exercise."),
        ("heart", "Heart", (.08, 1.4, .1), ["gravity"], "Resting heart rate", "resting_hr_bpm", "bpm", 65, 72, 85, True,
         "Fluids shift toward the head in space and the heart adapts. Your rate is within a healthy range."),
        ("gut", "Gut", (0, 1.06, .12), ["immune", "habitat"], "Microbiome diversity", "microbiome_diversity", "index", 3.4, 2.8, 2.2, False,
         "Gut bacteria shift in a closed habitat, which can affect immunity. Diversity is dipping slightly."),
        ("skin", "Skin", (.2, 1.3, .1), ["immune", "habitat"], "Inflammation marker (CRP)", "crp_mg_l", "mg/L", 4, 6, 10, True,
         "Skin is the front line of immunity. Dry air and dust can raise inflammation a little."),
        ("eyes", "Eyes", (0, 1.77, .13), ["radiation", "gravity"], "Optic disc swelling", "optic_disc_swelling_um", "um", 160, 200, 300, True,
         "Head-ward fluid shift can swell the back of the eye and blur near vision. Worth watching."),
    ]
    out = []
    for i, name, pos, hz, label, col, unit, w, o, c, hb, text in D:
        out.append(dict(id=i, name=name, pos=pos, hazards=hz, text=text, **mk(label, col, unit, w, o, c, hb, day)))
    return out


COUNTER = {
    "radiation": [("Storm shelter protocols", "Strong", "Operational practice; no known side effects."), ("Antioxidant-rich diet", "Emerging", "Food-based only; supplements are not proven.")],
    "gravity": [("Resistive exercise (ARED-type)", "Strong", "Use correct form; report joint pain."), ("Lower-body negative pressure", "Moderate", "Supervised use only; can cause light-headedness."), ("Vitamin D and calcium review", "Moderate", "Needs blood tests by the flight surgeon.")],
    "immune": [("Sleep and circadian lighting", "Moderate", "Safe; follow the lighting schedule."), ("Diverse fibre and fermented foods", "Emerging", "Check against onboard food allergies.")],
    "mind": [("Guided breathing", "Moderate", "Safe for everyone."), ("Scheduled Earth contact", "Moderate", "Plan around the comms delay."), ("Light therapy", "Emerging", "Avoid late in the day.")],
    "habitat": [("Filter and scrubber maintenance", "Strong", "Follow the lockout procedure."), ("Surface microbial sampling", "Moderate", "Use gloves and sealed swabs.")],
}


def worst(levels):
    return max(levels, key=ORDER.index) if levels else "normal"


def chip(level):
    return "stable" if level == "normal" else "watch" if level == "watch" else "alert"


def state(day=DEFAULT_DAY):
    day = max(1, min(TOTAL_DAYS, int(day)))
    mk_ = lambda *a, **k: mk(*a, day=day, **k)
    ms = markers(day)
    ck = checkin_state()
    byk = {i["key"]: i for i in ck["items"]}
    for m in ms:  # real check-in values raise the body-map status
        fl = [byk[k] for k in LINK.get(m["id"], []) if byk[k]["level"] != "normal"]
        if fl:
            m["level"] = worst([m["level"]] + [f["level"] for f in fl])
            m["text"] += " Today's check-in: " + ", ".join(f"{f['label']} {f['value']} {f['unit']} ({f['level']})" for f in fl) + "."
    anomalies = [a for d, a in [
        (100, "Greenhouse bay humidity drifting +8%"),
        (130, "Port scrubber efficiency down 6%"),
        (140, "CO2 spike in sleep pod 2: 1,150 ppm for 12 min")] if day >= d]
    spe = 138 <= day <= 148
    mods = {
        "radiation": dict(title="Radiation Guardian", hazard="radiation", ask="Explain my radiation level", askLabel="Ask ASTRA about radiation",
            metrics=[mk_("Cumulative dose", "cumulative_dose_msv", "mSv", 300, 450, 550),
                     mk_("Dose rate (transit)", "dose_rate_transit_msv_day", "mSv/day", 2.5, 4, 6),
                     mk_("Dose rate (surface)", "dose_rate_surface_msv_day", "mSv/day", 1, 2, 4)],
            insight="Radiation can damage DNA in cells. Your body repairs most of it, but we track the total so it stays under your mission limit."),
        "gravity": dict(title="Gravity Health", hazard="gravity", ask="Start a guided workout", askLabel="Start voice-guided workout",
            metrics=[mk_("Muscle mass", "muscle_mass_pct", "% of baseline", 95, 88, 80, False),
                     mk_("Bone density", "spine_bone_density_pct", "% of baseline", 92, 88, 82, False),
                     mk_("Resting heart rate", "resting_hr_bpm", "bpm", 65, 72, 85)],
            insight="Muscles and bones need load to stay strong. Resistance sessions are the best way to slow the loss, so consistency matters more than intensity."),
        "immune": dict(title="Immune Shield", hazard="immune", ask="How is my immune system?", askLabel="Ask ASTRA about immunity",
            metrics=[mk_("Inflammation (CRP)", "crp_mg_l", "mg/L", 4, 6, 10),
                     mk_("Lymphocyte count", "lymphocytes_e9_l", "x10^9/L", 1.5, 1.2, .9, False),
                     mk_("Microbiome diversity", "microbiome_diversity", "index", 3.4, 2.8, 2.2, False),
                     mk_("Infection risk", "infection_risk_pct", "%", 15, 25, 40)],
            insight="Space stress can make immune cells less alert. A varied diet, sleep and clean air help your defences stay balanced."),
        "mind": dict(title="MindSpace", hazard="mind", ask="I feel lonely", askLabel="Tell ASTRA how you feel",
            metrics=[mk_("Sleep", "sleep_hours", "h/night", 6.5, 5.5, 4.5, False),
                     mk_("Stress level", "stress_level", "/100", 55, 70, 85),
                     mk_("Mood", "mood_score", "/10", 5.5, 4.5, 3.5, False),
                     mk_("Days since live Earth call", "days_since_earth_call", "days", 8, 12, 18)],
            insight="Long missions can feel isolating. Short, regular check-ins and a steady sleep routine make a big difference."),
        "habitat": dict(title="Habitat Health", hazard="habitat", ask="How is the habitat air?", askLabel="Ask ASTRA about the habitat",
            metrics=[mk_("CO2", "co2_ppm", "ppm", 1000, 2000, 5000),
                     mk_("Oxygen", "oxygen_pct", "%", 20, 19.5, 18, False),
                     mk_("Temperature", "habitat_temp_c", "C", 25, 28, 32),
                     mk_("Humidity", "humidity_pct", "%", 60, 70, 80),
                     mk_("Microbial load", "microbial_load_cfu_m3", "CFU/m3", 300, 500, 800)],
            insight="The habitat is a closed loop: every breath and surface matters. Small drifts are caught early so they never become problems.",
            anomalies=anomalies),
    }
    for k, m in mods.items():
        lv = [x["level"] for x in m["metrics"]] + [x["level"] for x in ms if k in x["hazards"]]
        lv += [byk[x]["level"] for x in HAZ.get(k, [])]
        if k == "habitat" and len(anomalies) >= 2:
            lv.append("watch")
        m["level"] = worst(lv)
        m["chip"] = chip(m["level"])
    attention = sum(1 for m in mods.values() if m["chip"] == "alert")
    return dict(astronaut="Cdr. Amara Okafor", day=day, total=TOTAL_DAYS, markers=ms, modules=mods, attention=attention,
        rad=dict(limit=600, spe=spe, spe_text="Solar particle event: elevated protons for the next ~10 h. Move to the storm shelter if the rate exceeds 6 mSv/day."),
        adherence=[int((day - 6 + i) * 7 % 5 != 0) for i in range(7)],
        messages=["Mum: 'Proud of you. The garden is blooming.' (6 min delay)", "Mission Control: 'Great work on the EVA prep, Amara.'", "Sam: 'Football finals tonight, I saved you a seat.'"],
        counter=COUNTER, checkin=ck)


reset()
