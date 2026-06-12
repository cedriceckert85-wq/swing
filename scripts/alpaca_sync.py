# -*- coding: utf-8 -*-
"""Alpaca-Paper-Trading-Anbindung des Elite-Swing-Agenten.

Aufgaben (laeuft per GitHub Actions mit Secrets ALPACA_KEY/ALPACA_SECRET):
1. Neue Journal-Trades (status "wartet", US-Symbol, noch ohne Alpaca-Order)
   als Bracket-Order platzieren (Entry + Stop-Loss + Take-Profit, GTC).
   Stueckzahl aus der 1R=100$-Regel: qty = floor(100 / Stop-Distanz).
2. Bestehende Alpaca-Trades synchronisieren: Entry-Fill, Stop/Ziel-Fill,
   Verfall (Entry >2 Handelstage nicht getriggert -> Order canceln),
   Zeit-Exit (Haltedauer ueberschritten -> Legs canceln + Market-on-Open).
Alpaca ist fuer diese Trades die Wahrheit; trade_eval.py (Yahoo) ueberspringt
sie und bleibt Fallback fuer Nicht-US-Symbole. Ohne Keys: stiller No-Op.
"""
import json
import os
import sys
import datetime
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trade_eval import r_multiple, statistik_neu  # noqa: E402

BASE = "https://paper-api.alpaca.markets/v2"
KEY = os.environ.get("ALPACA_KEY", "")
SEC = os.environ.get("ALPACA_SECRET", "")
J = "data/journal.json"


def api(pfad, methode="GET", body=None):
    req = urllib.request.Request(
        BASE + pfad, method=methode,
        headers={"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC,
                 "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            inhalt = r.read().decode()
            return json.loads(inhalt) if inhalt else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{methode} {pfad}: HTTP {e.code} {e.read().decode()[:300]}")


def handelstage(von, bis):
    d = datetime.date.fromisoformat(von)
    ende = datetime.date.fromisoformat(bis)
    n = 0
    while d < ende:
        d += datetime.timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def ist_us(t):
    return "." not in t.get("yahooSymbol", t["ticker"])


RISIKO_USD = 1000  # 1 % des 100.000-$-Kontos = 1R


def order_anlegen(t):
    risiko = abs(t["entry"] - t["stop"])
    qty = int(RISIKO_USD // risiko) if risiko > 0 else 0
    if qty < 1:
        t.setdefault("log", []).append(f"Alpaca: Stop-Distanz zu gross fuer {RISIKO_USD}$-Risiko, qty<1 -> Yahoo-Simulation")
        return False
    seite = "buy" if t["richtung"] == "long" else "sell"
    typ = "limit" if t.get("entryTyp", "stop") == "limit" else "stop"
    body = {"symbol": t["ticker"], "qty": str(qty), "side": seite, "type": typ,
            "time_in_force": "gtc", "order_class": "bracket",
            "take_profit": {"limit_price": f"{t['tp']:.2f}"},
            "stop_loss": {"stop_price": f"{t['stop']:.2f}"}}
    if typ == "limit":
        body["limit_price"] = f"{t['entry']:.2f}"
    else:
        body["stop_price"] = f"{t['entry']:.2f}"
    o = api("/orders", "POST", body)
    t["alpaca"] = {"orderId": o["id"], "qty": qty}
    t.setdefault("log", []).append(f"Alpaca: Bracket-Order platziert ({qty} Stk., Order {o['id'][:8]}...)")
    print(f"{t['id']} {t['ticker']}: Bracket-Order platziert, {qty} Stk.")
    return True


def order_sync(t):
    heute = datetime.date.today().isoformat()
    o = api(f"/orders/{t['alpaca']['orderId']}?nested=true")
    if t["status"] == "wartet":
        if o["status"] == "filled":
            t["status"] = "offen"
            t["entryFill"] = round(float(o["filled_avg_price"]), 2)
            t["entryDatum"] = o["filled_at"][:10]
            t.setdefault("log", []).append(f"{t['entryDatum']} Alpaca-Fill {t['entryFill']}")
        elif o["status"] in ("canceled", "expired", "rejected", "done_for_day"):
            t["status"] = "verfallen"
            t.setdefault("log", []).append(f"Alpaca-Order {o['status']} -> verfallen")
        elif handelstage(t["datumEmpfehlung"], heute) > 2:
            api(f"/orders/{t['alpaca']['orderId']}", "DELETE")
            t["status"] = "verfallen"
            t.setdefault("log", []).append("Entry 2 Handelstage nicht getriggert -> Order storniert, verfallen")
    if t["status"] == "offen":
        if t.get("exitOrderId"):
            eo = api(f"/orders/{t['exitOrderId']}")
            if eo["status"] == "filled":
                t["status"] = "zeit_exit"
                t["exitKurs"] = round(float(eo["filled_avg_price"]), 2)
                t["exitDatum"] = eo["filled_at"][:10]
        else:
            for leg in (o.get("legs") or []):
                if leg["status"] == "filled":
                    t["exitKurs"] = round(float(leg["filled_avg_price"]), 2)
                    t["exitDatum"] = leg["filled_at"][:10]
                    t["status"] = "gewonnen" if leg["type"] == "limit" else "verloren"
                    t.setdefault("log", []).append(f"{t['exitDatum']} Alpaca {leg['type']}-Leg gefuellt @ {t['exitKurs']}")
                    break
            if (t["status"] == "offen"
                    and handelstage(t["entryDatum"], heute) >= t.get("maxHaltezeitTage", 5)):
                for leg in (o.get("legs") or []):
                    if leg["status"] not in ("filled", "canceled", "expired"):
                        try:
                            api(f"/orders/{leg['id']}", "DELETE")
                        except RuntimeError:
                            pass
                seite = "sell" if t["richtung"] == "long" else "buy"
                eo = api("/orders", "POST", {
                    "symbol": t["ticker"], "qty": str(t["alpaca"]["qty"]),
                    "side": seite, "type": "market", "time_in_force": "opg"})
                t["exitOrderId"] = eo["id"]
                t.setdefault("log", []).append("Haltedauer erreicht -> Market-on-Open-Exit platziert")
    if t["status"] in ("gewonnen", "verloren", "zeit_exit") and "ergebnisR" not in t:
        t["ergebnisR"] = r_multiple(t, t["exitKurs"])
        t["pnlEur"] = round(t["ergebnisR"] * RISIKO_USD, 2)


def main():
    if not KEY or not SEC:
        print("Keine Alpaca-Keys gesetzt — uebersprungen (Yahoo-Simulation bleibt aktiv).")
        return
    with open(J, encoding="utf-8") as f:
        d = json.load(f)
    vorher = json.dumps(d, sort_keys=True)
    for t in d["trades"]:
        if not ist_us(t):
            continue
        try:
            if t["status"] == "wartet" and "alpaca" not in t:
                order_anlegen(t)
            if "alpaca" in t and t["status"] in ("wartet", "offen"):
                order_sync(t)
        except RuntimeError as e:
            print(f"{t['id']}: {e}")
    d["statistik"] = statistik_neu(d["trades"])
    if json.dumps(d, sort_keys=True) != vorher:
        with open(J, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("Journal aktualisiert (Alpaca).")
    else:
        print("Keine Aenderungen (Alpaca).")


if __name__ == "__main__":
    main()
