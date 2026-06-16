# QUALITÄTSREGELN V4 — MEAN-REVERSION (Gegen-Trend)

Stand: 16.06.2026. **Umbau von V3 (Momentum-Swing) auf Mean-Reversion** auf Nutzerwunsch —
der Swing-Slot ist ab jetzt der **Gegen-Trend-Bot** der Flotte (bewusst unkorreliert zu den
Momentum-Bots SOLID/RISK/Speku). Forschungsgrundlage: `research/MEAN_REVERSION_RESEARCH_2026-06-16.md`.
Die alte Momentum-Spec liegt als `AGENT_V3_MOMENTUM_ARCHIV.md` / `REGELN_V3_MOMENTUM_ARCHIV.md`.

**Regeln 1–9 (Strategie) sind neu auf Mean-Reversion umgestellt. Regeln 10–15 (Risiko) bleiben
unverändert aus V3 — strategie-agnostische Disziplin.** Statistik-Reset-Gate (n≥30) beachten:
V4-Trades werden statistisch getrennt von V3 betrachtet.

**KERNIDEE:** NICHT Stärke kaufen, sondern messbare statistische **Extreme faden** — überverkaufte
Dips im Aufwärtstrend kaufen, überkaufte Spikes im Abwärtstrend shorten. Ziel = Rückkehr zum
Mittelwert. *„Buy weakness, sell strength."* Kapitalerhalt vor Aktivität (Regel 15).

---

## 1. SETUP-DEFINITION — statistisches Extrem (Pflicht, nicht subjektiv)
Ohne messbares Extrem gibt es kein Setup. Mindestens **zwei** Bedingungen müssen zeigen:
- **RSI(2) < 10** (besser < 5) → Long-Kandidat · **RSI(2) > 90** (besser > 95) → Short-Kandidat.
- **Z-Score ≤ −2** (Long) / **≥ +2** (Short) zum 20er-Mittel.
- Kurs **≥ 1,5–2 ATR** vom 20er-Mittel entfernt bzw. am **unteren/oberen Bollinger-Band (20, 2)**.
Je extremer, desto besser (tieferes RSI = höhere historische Folge-Rendite). Subjektive
„sieht überverkauft aus"-Calls sind verboten — es zählt die Zahl.

## 2. TREND-FILTER — Falling-Knife-Schutz (Pflicht)
Mean Reversion **nur mit dem übergeordneten Trend**:
- **Long nur über der 200-Tage-SMA** (Aufwärtstrend → überverkaufte Dips kaufen).
- **Short nur unter der 200-Tage-SMA** (Abwärtstrend → überkaufte Spikes shorten).
Gegen die 200-SMA wird **nie** gefadet. Ein Extrem ohne Trend-Filter-Deckung = **KEIN TRADE**.

## 3. REGIME-GATE — wann MR funktioniert
- RICHTUNG: **Range/Seitwärts = grün** · **starker Trend = Signal unterdrücken** (Kurs bleibt
  länger extrem als erwartet).
- ZUSTAND: Normal = grün · **News-getriebener Bruch = ROT**.
- **Fundamentaler Katalysator ist hier ein WARNSIGNAL, kein Pluspunkt:** Earnings-Miss,
  Guidance-Cut, Downgrade, SEC-/Fraud-Problem → das ist ein **Regimewechsel**, kein Dip. Solche
  Titel **nicht faden** (das wäre das fallende Messer). Der Dip muss eine technische/Sentiment-
  **Überreaktion** ohne fundamentalen Bruch sein.

## 4. ZIEL = RÜCKKEHR ZUM MITTELWERT (nicht starres CRV)
Take-Profit = Mittelwert (20er-SMA / mittleres Bollinger-Band) bzw. Rückschlag über die
**5-Tage-MA** (Connors). **Kurze Haltedauer: `maxHaltezeitTage` = 3** (MR ist schnell; reagiert
sie nicht, war die These falsch). Erreicht der Kurs den Mittelwert oder schlägt über die
5-Tage-MA zurück → Reversion erreicht, Exit.

## 5. STOP = INVALIDATION DES SETUPS
Stop dort, wo die Reversions-These **widerlegt** ist: jenseits des jüngsten Swing-Extrems bzw.
~1 ATR über das Extrem hinaus, **außerhalb des normalen Rauschens**. Reißt der Stop → es ist
ein Trend, kein Dip → raus, **kein Nachkaufen, kein Mitteln**. Reihenfolge fix (Regel 10):
Invalidation → Stop → Risiko → Positionsgröße. Niemals den Stop weiten, um „dem Trade Zeit zu geben".

## 6. CONFIDENCE SCORE (für MR kalibriert, je +20)
- +20 **Regime passt** (Range/Normal, kein starker Trend, kein News-Bruch)
- +20 **Statistisches Extrem klar** (RSI(2) < 10 / > 90 UND durch Z-Score/Bollinger/ATR bestätigt)
- +20 **Trend-Filter gedeckt** (Long > 200-SMA / Short < 200-SMA)
- +20 **Kein fundamentaler Bruch** (Dip ist Überreaktion, nicht Regimewechsel — 2 Quellen < 24 h, Regel 8)
- +20 **Reversions-Ziel strukturell definiert UND Stop außerhalb des Rauschens** (Gegenanalyse überstanden)
Interpretation wie V3: 80–89 stark, ≥ 90 außergewöhnlich. **Unter 70 niemals handeln.** Der
Haupttrade braucht Score ≥ 80 UND ein Fonds-JA.

## 7. GEGENARGUMENT-ANALYSE
Vor jeder Empfehlung Pflicht — BULL CASE · BEAR CASE · INVALIDATION. **Speziell die eine Frage:**
„Ist das ein **Dip** (Überreaktion, kehrt zurück) oder ein **Trendbruch** (fallendes Messer)?"
Kein klares „Dip" → KEIN TRADE.

## 8. NEWS-VERIFIKATION (hier: Ausschluss-Check)
Mindestens zwei unabhängige Quellen, nicht älter als 24 h. **Zweck im MR-Mandat:** ausschließen,
dass das Extrem von einem echten fundamentalen Bruch kommt. Findet sich ein harter Katalysator
(Miss / Cut / Downgrade / Fraud / Klage) → **Faden verboten**. Unbestätigte Gerüchte ignorieren.

## 9. ENTRY-AUSFÜHRUNG
Default `entryTyp` = **"limit"** (kauf Schwäche / verkauf Stärke direkt am Extrem). Connors
„close method": Bedingung auf Schlusskursbasis prüfen, Entry als Limit am/unter dem Extrem
(Long) bzw. am/über dem Extrem (Short). **Breakout-„stop"-Entries gibt es im MR-Mandat nicht.**

---

## 10. POSITIONSGRÖSSE (PFLICHT — unverändert)
Maximales Risiko pro Trade: **1 % des Gesamtkontos** (1R = 1.000 $). Positionsgröße immer aus
der Stop-Distanz (`scripts/alpaca_sync.py` rechnet sie automatisch). Niemals Stop an die
gewünschte Größe oder Größe an den gewünschten Gewinn anpassen. Reihenfolge fix:
1. Invalidation 2. Stop 3. Risiko 4. Positionsgröße.

## 11. VERLUSTSERIEN-BREMSE (PFLICHT — unverändert)
Sofort pausieren bei **3 Verlusttrades in Folge** ODER **−3 % Kontostand binnen einer Woche**.
Danach: keine neuen Trades, Review aller Verlusttrades, Fehlerursachen-Analyse, erst dann weiter.
**Rachetrading verboten.** (`statistik.bremseAktiv` = true → HEUTE KEIN TRADE.)

## 12. PERFORMANCE-KALIBRIERUNG (PFLICHT — unverändert)
Nach ≥ 30 abgeschlossenen Trades prüfen: Gewinnen Score-≥-80-Trades häufiger als 70–79? Wenn
nein → Confidence-Modell überarbeiten. Der Score muss nachweisbar prognostischen Wert besitzen.

## 13. GESAMTSTATISTIK (PFLICHT — unverändert)
Trades · gewonnen · verloren · Trefferquote · Ø-CRV · Profit Factor · aktuelle/größte
Verlustserie · Ø-Gewinn · Ø-Verlust · **Erwartungswert pro Trade = Trefferquote × Ø-Gewinn −
Verlustquote × Ø-Verlust.** Der Erwartungswert ist die eine Zahl, die zählt. Interpretation erst ab n ≥ 30.

## 14. JOURNAL-PFLICHT (unverändert)
Jeder Trade dokumentiert. **Nicht dokumentierte Trades gelten als nicht durchgeführt.** Ohne
Journal keine Regeländerung, keine Strategiebewertung.

## 15. NO-TRADE-REGEL (unverändert)
**„HEUTE KEIN TRADE"** ist eine vollständige, professionelle Analyse. Bei Mean Reversion gilt
besonders: an Tagen mit starkem Trend oder News-Bruch ist Nichthandeln die richtige Entscheidung.
**Kapitalerhalt hat Vorrang vor Aktivität.**
