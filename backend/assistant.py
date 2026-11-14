"""ASTRA, the voice-first health assistant.

Replies come from built-in rules and work offline. An optional LLM can reword the reply:

    ASTRA_LLM=groq       Groq chat completions (needs GROQ_API_KEY or API_KEY)
    ASTRA_LLM=ollama     small local model via Ollama (no internet needed)
    ASTRA_LLM=anthropic  Claude API (needs ANTHROPIC_API_KEY)
    ASTRA_LLM=none       rules only; automatic selection tries Groq before the default provider

Safety rule: replies that carry measurements, status or escalation advice are never rewritten by a model.
ASTRA gives guidance only, never a diagnosis.
"""
import json
import os
import re
import urllib.request

from database import DEFAULT_DAY, item, log_value, state

# spoken phrase -> check-in indicator, e.g. "my heart rate is 72"
VOICE = {
    "hr": r"(?:heart rate|pulse)\D{0,12}(\d+(?:\.\d+)?)",
    "glucose": r"(?:glucose|blood sugar)\D{0,12}(\d+(?:\.\d+)?)",
    "temp": r"temperature\D{0,12}(\d+(?:\.\d+)?)",
    "sleep": r"(?:slept|sleep)\D{0,12}(\d+(?:\.\d+)?)",
    "mood": r"mood\D{0,12}(\d+(?:\.\d+)?)",
    "sys": r"(?:systolic(?: blood pressure)?|top number)\D{0,12}(\d+(?:\.\d+)?)",
    "dia": r"(?:diastolic(?: blood pressure)?|bottom number)\D{0,12}(\d+(?:\.\d+)?)",
}
BLOOD_PRESSURE = r"(?:blood pressure|bp)\D{0,8}(\d+(?:\.\d+)?)\s*(?:over|/)\s*(\d+(?:\.\d+)?)"

LLM_MODEL = os.getenv("ASTRA_MODEL", "claude-sonnet-4-6")          # Anthropic model
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")             # any small model you have pulled
LLM_TIMEOUT = float(os.getenv("ASTRA_LLM_TIMEOUT", "20"))           # seconds, then fall back to rules
SYSTEM = ("You are ASTRA, a calm, kind voice assistant for an astronaut on a long mission. "
          "Reply in 1-3 short spoken sentences, plain language. Never diagnose or prescribe. "
          "Use only the status data given. If something looks serious, tell them to contact the flight surgeon. Status data: ")


def default_provider():
    """Return the configured default model, or Ollama when none is specified."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "ollama"


def provider():
    p = os.getenv("ASTRA_LLM", "").lower()
    if p in ("groq", "ollama", "anthropic", "none"):
        return p
    from grok_chat import is_configured

    if is_configured():
        return "groq"
    return default_provider()


def voice_parse(text):
    """Pull measurements out of free text, including paired blood pressure."""
    t = text.lower()
    found = []
    pressure = re.search(BLOOD_PRESSURE, t)
    if pressure:
        found.extend((("sys", float(pressure.group(1))), ("dia", float(pressure.group(2)))))
    found.extend(
        (k, float(m.group(1)))
        for k, p in VOICE.items()
        if k not in ("sys", "dia") or not pressure
        if (m := re.search(p, t))
    )
    return found


def lonely_reply():
    bad = ("warning", "critical")
    s = "I'm here with you. Being far from home is hard. Would you like to talk to a crew member or Earth, or try a breathing exercise?"
    if item("mood")["level"] in bad or item("sleep")["level"] in bad:
        s += " Your recent mood and sleep check-ins are low, so please also speak with a crew member and your flight surgeon soon."
    return s


def rule_reply(text, day=DEFAULT_DAY):
    """Deterministic reply. Returns {reply, nav?, select?}; nav/select tell the frontend where to go."""
    found = voice_parse(text)
    if found:  # e.g. "my heart rate is 72"
        out = []
        for k, v in found:
            ok, msg = log_value(k, v)
            i = item(k)
            out.append(f"{i['label']} {v} {i['unit']} logged, status {i['level']}. {i['action']}" if ok else msg)
        return dict(reply=" ".join(out), nav="checkin", fixed=True)
    st, t = state(day), text.lower()
    for m in st["markers"]:
        if m["name"].lower() in t or (m["id"] == "spine" and "bone" in t):
            return dict(reply=f"{m['text']} Your {m['label'].lower()} is {m['value']} {m['unit']}. Status: {m['level']}.", nav="body", select=m["id"])
    mo = st["modules"]
    R = [
        (("check-in", "check in", "checkin", "log my"), lambda: "Opening your daily check-in. You can also tell me, for example: my heart rate is 70.", "checkin"),
        (("radiation", "dose", "solar"), lambda: f"Your total dose is {mo['radiation']['metrics'][0]['value']} milli-sieverts of a {st['rad']['limit']} limit. " + ("A solar particle event is active, so stay alert for shelter instructions." if st["rad"]["spe"] else "Space weather is calm."), "radiation"),
        (("workout", "exercise", "muscle", "gravity"), lambda: f"Let's train. Your muscle mass is {mo['gravity']['metrics'][0]['value']} percent of baseline. Start with ten squats, then rest for thirty seconds. Ready?", "gravity"),
        (("immune", "infection"), lambda: f"Your infection risk is {mo['immune']['metrics'][3]['value']} percent. That is low to moderate.", "immune"),
        (("habitat", "air", "co2", "oxygen"), lambda: f"CO2 is {mo['habitat']['metrics'][0]['value']:.0f} parts per million and oxygen is {mo['habitat']['metrics'][1]['value']} percent. {len(mo['habitat']['anomalies'])} anomalies are logged.", "habitat"),
        (("lonely", "sad", "alone", "mood", "sleep"), lonely_reply, "companion"),  # fixed below
        (("music", "song"), lambda: "Playing a calm ambient playlist: Earth sounds, rain on leaves.", None),
        (("breath",), lambda: "Let's breathe together. In for four, hold for four, out for six. Again, slowly.", None),
        (("story",), lambda: "Once, a small rover named Dusty found a blue pebble on Mars. It turned out to be a message from a very patient friend...", None),
        (("message", "home"), lambda: "You have three messages: " + " | ".join(st["messages"]), None),
        (("game",), lambda: "Let's play twenty questions. I'm thinking of something found on both Earth and Mars.", None),
        (("body map", "body"), lambda: "Here is your body map. Tap a glowing marker to learn more.", "body"),
        (("research", "countermeasure"), lambda: "Here are research-based countermeasures. Research information only, not a prescription.", "research"),
        (("how am i", "status", "overall", "explain my"), lambda: f"Your overall status is stable. {st['attention']} thing{'s' if st['attention'] != 1 else ''} need attention: " + ", ".join(k for k, m in mo.items() if m["chip"] == "alert") + ".", "home"),
    ]
    for keys, fn, nav in R:
        if any(k in t for k in keys):
            out = dict(reply=fn(), nav=nav)
            if fn is lonely_reply and "flight surgeon" in out["reply"]:
                out["fixed"] = True  # escalation advice stays exactly as written
            return out
    return dict(reply="I can explain your radiation, gravity, immune, mind or habitat status, open your body map, or just talk. What would you like?")


def _context(day):
    """Compact status summary: small models do better with short, flat context."""
    st = state(day)
    lines = [f"{m['title']}: {m['level']}; " + ", ".join(f"{x['label']} {x['value']} {x['unit']}" for x in m["metrics"][:3])
             for m in st["modules"].values()]
    return " | ".join(lines)


def _ask_ollama(text, ctx):
    body = json.dumps(dict(model=OLLAMA_MODEL, stream=False, options=dict(temperature=0.3, num_predict=120),
                           messages=[dict(role="system", content=SYSTEM + ctx), dict(role="user", content=text)])).encode()
    req = urllib.request.Request(OLLAMA_URL.rstrip("/") + "/api/chat", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as r:
        return json.load(r)["message"]["content"]


def _ask_anthropic(text, ctx):
    import anthropic
    r = anthropic.Anthropic().messages.create(model=LLM_MODEL, max_tokens=250, system=SYSTEM + ctx,
                                              messages=[{"role": "user", "content": text}])
    return r.content[0].text


def _ask_groq(text, ctx):
    from grok_chat import ask_groq

    return ask_groq(text, system_prompt=SYSTEM + ctx)


def llm_reply(text, day=DEFAULT_DAY):
    """Reword a reply, trying the default provider if Groq is unavailable."""
    selected = provider()
    if selected == "none":
        return None
    candidates = [selected]
    if selected == "groq":
        fallback = default_provider()
        if fallback not in candidates:
            candidates.append(fallback)
    askers = {"groq": _ask_groq, "ollama": _ask_ollama, "anthropic": _ask_anthropic}
    for name in candidates:
        try:
            out = askers[name](text, _context(day)).strip()
            if out:
                return out[:600]
        except Exception as e:  # Continue to the default provider, then rules.
            print(f"LLM fallback ({name}):", e)
    return None


def respond(text, day=DEFAULT_DAY):
    """Rules decide what to do (and log voice measurements); the LLM may only reword non-critical replies."""
    out = rule_reply(text, day)
    if not out.pop("fixed", False):
        llm = llm_reply(text, day)
        if llm:
            out["reply"] = llm
    return out
