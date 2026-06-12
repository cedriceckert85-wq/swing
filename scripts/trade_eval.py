# -*- coding: utf-8 -*-
"""Wertet die Paper-Trades des Elite-Swing-Agenten gegen echte Tageskerzen aus.

Laeuft per GitHub Actions (Mo-Fr abends) VOR dem Agenten-Lauf.
Logik (konservativ):
- Trade "wartet": Entry-Trigger in den ersten 2 Handelstagen nach Empfehlung,
  sonst Status "verfallen". entryTyp "stop" (Breakout) oder "limit" (Pullback).
- Trade "offen": Stop vor Ziel, wenn beide in derselben Kerze liegen.
  Zeit-Exit zum Schlusskurs nach maxHaltezeitTage Handelstagen.
- Ergebnis in R-Multiplen: 1R = 100 EUR (Risiko pro Trade). Gap-Fills realistisch
  (Eroeffnung jenseits des Levels -> Fill zur Eroeffnung).
- Plausibilitaets-Guard: Kerse mit >50 % Sprung zum Vortag wird verworfen.
"""
import json
import urllib.request
import urllib.parse
import datetime

J = "data/journal.json"


def kerzen_taeglich(symbol):
    url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
           + urllib.parse.quote(symbol) + "?interval=1d&range=3mo")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    res = d["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    out = []
    vorher = None
    for i, t in enumerate(res["timestamp"]):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        if vorher and abs(c / vorher - 1) > 0.5:
            continue  # Datenfehler-Guard
        vorher = c
        datum = datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
        out.append({"datum": datum, "o": o, "h": h, "l": l, "c": c})
    return out


def r_multiple(t, exit_kurs):
    if t["richtung"] == "long":
        risiko = t["entryFill"] - t["stop"]
        gewinn = exit_kurs - t["entryFill"]
    else:
        risiko = t["stop"] - t["entryFill"]
        gewinn = t["entryFill"] - exit_kurs
    return round(gewinn / risiko, 2) if risiko > 0 else 0.0


def trade_auswerten(t):
    """Mutiert t. True wenn sich etwas geaendert hat."""
    try:
        kerzen = kerzen_taeglich(t["yahooSymbol"])
    except Exception as e:
        t.setdefault("log", []).append(f"Kursabruf fehlgeschlagen: {e}")
        return False
    geaendert = False

    if t["status"] == "wartet":
        fenster = [k for k in kerzen if k["datum"] > t["datumEmpfehlung"]][:2]
        for k in fenster:
            lng = t["richtung"] == "long"
            styp = t.get("entryTyp", "stop") == "stop"
            getriggert = ((lng and styp and k["h"] >= t["entry"]) or
                          (lng and not styp and k["l"] <= t["entry"]) or
                          (not lng and styp and k["l"] <= t["entry"]) or
                          (not lng and not styp and k["h"] >= t["entry"]))
            if getriggert:
                if lng:
                    fill = max(k["o"], t["entry"]) if styp else min(k["o"], t["entry"])
                else:
                    fill = min(k["o"], t["entry"]) if styp else max(k["o"], t["entry"])
                t["status"] = "offen"
                t["entryFill"] = round(fill, 2)
                t["entryDatum"] = k["datum"]
                t.setdefault("log", []).append(f"{k['datum']} Entry-Fill {fill:.2f}")
                geaendert = True
                break
        else:
            if len(fenster) >= 2:
                t["status"] = "verfallen"
                t.setdefault("log", []).append("Entry 2 Handelstage nicht getriggert -> verfallen")
                geaendert = True

    if t["status"] == "offen":
        nach_entry = [k for k in kerzen if k["datum"] >= t["entryDatum"]]
        for i, k in enumerate(nach_entry):
            lng = t["richtung"] == "long"
            stop_hit = (k["l"] <= t["stop"]) if lng else (k["h"] >= t["stop"])
            ziel_hit = (k["h"] >= t["tp"]) if lng else (k["l"] <= t["tp"])
            if stop_hit:  # konservativ: Stop schlaegt Ziel
                fill = min(k["o"], t["stop"]) if lng else max(k["o"], t["stop"])
                t["status"] = "verloren"
                t["exitDatum"], t["exitKurs"] = k["datum"], round(fill, 2)
                t.setdefault("log", []).append(f"{k['datum']} Stop {t['stop']} -> Exit {fill:.2f}")
                geaendert = True
                break
            if ziel_hit:
                fill = max(k["o"], t["tp"]) if lng else min(k["o"], t["tp"])
                t["status"] = "gewonnen"
                t["exitDatum"], t["exitKurs"] = k["datum"], round(fill, 2)
                t.setdefault("log", []).append(f"{k['datum']} Ziel {t['tp']} -> Exit {fill:.2f}")
                geaendert = True
                break
            if i + 1 >= t.get("maxHaltezeitTage", 5):
                t["status"] = "zeit_exit"
                t["exitDatum"], t["exitKurs"] = k["datum"], round(k["c"], 2)
                t.setdefault("log", []).append(f"{k['datum']} Zeit-Exit zu {k['c']:.2f}")
                geaendert = True
                break
        if t["status"] in ("verloren", "gewonnen", "zeit_exit"):
            t["ergebnisR"] = r_multiple(t, t["exitKurs"])
            t["pnlEur"] = round(t["ergebnisR"] * 1000, 2)  # 1R = 1.000 $ (1 % von 100.000)

    return geaendert


def statistik_neu(trades):
    fertig = [t for t in trades if t["status"] in ("gewonnen", "verloren", "zeit_exit")]
    gewonnen = [t for t in fertig if t.get("ergebnisR", 0) > 0]
    verloren = [t for t in fertig if t.get("ergebnisR", 0) <= 0]
    serie = 0
    schlechteste = 0
    for t in fertig:
        serie = serie + 1 if t.get("ergebnisR", 0) <= 0 else 0
        schlechteste = max(schlechteste, serie)
    summe_gewinn = sum(t["ergebnisR"] for t in gewonnen)
    summe_verlust = abs(sum(t["ergebnisR"] for t in verloren))
    n = len(fertig)
    return {
        "trades": n,
        "gewonnen": len(gewonnen),
        "verloren": len(verloren),
        "verfallen": len([t for t in trades if t["status"] == "verfallen"]),
        "offen": len([t for t in trades if t["status"] in ("wartet", "offen")]),
        "trefferquote": round(len(gewonnen) / n * 100, 1) if n else None,
        "summeR": round(sum(t.get("ergebnisR", 0) for t in fertig), 2),
        "erwartungswertR": round(sum(t.get("ergebnisR", 0) for t in fertig) / n, 3) if n else None,
        "profitFactor": round(summe_gewinn / summe_verlust, 2) if summe_verlust > 0 else None,
        "aktuelleVerlustserie": serie,
        "groessteVerlustserie": schlechteste,
        "bremseAktiv": serie >= 3,
    }


def main():
    with open(J, encoding="utf-8") as f:
        d = json.load(f)
    geaendert = False
    for t in d["trades"]:
        if "alpaca" in t:
            continue  # Alpaca-verwaltete Trades synct alpaca_sync.py — echte Fills schlagen Simulation
        if t["status"] in ("wartet", "offen"):
            if trade_auswerten(t):
                geaendert = True
    neu = statistik_neu(d["trades"])
    neu_vergleich = {k: v for k, v in neu.items()}
    if neu_vergleich != d["statistik"]:
        geaendert = True
    d["statistik"] = neu
    if geaendert:
        with open(J, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("Journal aktualisiert.", json.dumps(neu, ensure_ascii=False))
    else:
        print("Keine Aenderungen.")


if __name__ == "__main__":
    main()
