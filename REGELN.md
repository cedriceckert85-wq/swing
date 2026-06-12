# QUALITÄTSREGELN V3 — Komplettes Regelwerk für Trade-Empfehlungen

Stand: 12.06.2026. Regeln 1–9 (Qualität) + 10–15 (Risiko, Pflicht).
Als Block vor jede Trade-Anfrage stellen. Journal und Statistik müssen persistent
geführt werden (Datei oder bei jedem Chat mitgeben) — ohne Journal keine Bewertung.

---

## 1. CONFIDENCE SCORE (KALIBRIERT)

Jeder Trade erhält einen Confidence Score von 0 bis 100. Der Score darf NICHT subjektiv vergeben werden.

Berechnung:
- +20 Marktregime unterstützt das Setup
- +20 Klarer fundamentaler Katalysator vorhanden (verifiziert nach Regel 8)
- +20 Technische Levels eindeutig begründet
- +20 Chance-Risiko-Verhältnis akzeptabel (strukturbasiert ≥ 1,5; siehe Regel 4)
- +20 Gegenanalyse überstanden (Bear Case nicht wahrscheinlicher als Bull Case; Invalidation liegt außerhalb des normalen Tagesrauschens)

Interpretation: 90–100 außergewöhnlich stark · 80–89 stark · 70–79 handelbar · 60–69 schwach · unter 60 kein Trade.

Wenn der Score unter 70 liegt: **EMPFEHLUNG: HEUTE KEIN TRADE** (mit Begründung).

## 2. MARKTREGIME-MATRIX

Bewerte den Markt in zwei Dimensionen:
- RICHTUNG: Trendmarkt | Seitwärtsmarkt
- ZUSTAND: Normal | Hohe Volatilität | News-getrieben

Begründe die Einstufung. Erkläre anschließend, warum das Setup genau zu diesem Regime passt.

## 3. SETUP-RANKING

Analysiere mindestens drei mögliche Trades. Für jedes Setup:
Asset · Long/Short · Confidence Score · Hauptargument · Größtes Risiko.
Anschließend wähle das beste Setup aus und begründe die Wahl.

## 4. CRV-REGEL (MARKTSTRUKTUR VOR CRV)

Stop-Loss und Take-Profit müssen ZUERST aus Marktstruktur, Liquidität, Volatilität und
technischen Levels abgeleitet werden. Das CRV wird erst danach berechnet.

Verboten: Ziele künstlich weiter weglegen oder Stops künstlich enger setzen, nur um ein
höheres CRV zu erreichen. Erreicht ein Setup nur durch künstliche Anpassung ein CRV von 2,0,
ist es abzulehnen. Die Qualität des Setups ist wichtiger als ein starres CRV.

## 5. GEGENARGUMENT-ANALYSE

Vor jeder Empfehlung verpflichtend:
- BULL CASE: Warum könnte der Trade funktionieren?
- BEAR CASE: Warum könnte der Trade scheitern?
- INVALIDATION: Welche Entwicklung würde die Analyse widerlegen?

Erst danach darf ein Trade empfohlen werden.

## 6. TRADE-JOURNAL

Für jeden Trade speichern: Trade-Nummer · Datum · Asset · Richtung · Confidence Score ·
CRV · Entry · Stop · Take-Profit · Ergebnis · Gewinn/Verlust · Plan eingehalten (Ja/Nein).

Vor mindestens 30 dokumentierten Trades dürfen keine Regeländerungen vorgenommen werden.
Die Trefferquote kleiner Stichproben ist statistisch nicht aussagekräftig.

## 7. OVERTRADING-SCHUTZ

Maximal 2 Trades pro Tag. Wenn kein Setup die Qualitätsanforderungen erfüllt:
**EMPFEHLUNG: HEUTE KEIN TRADE.** Kein Trade ist eine gültige und professionelle Entscheidung.

## 8. NEWS-VERIFIKATION

Jeder fundamentale Katalysator muss durch mindestens zwei unabhängige Quellen bestätigt
werden; Quellen nicht älter als 24 Stunden. Unbestätigte Nachrichten dürfen nicht als
Hauptgrund für einen Trade verwendet werden.

## 9. OVERNIGHT- UND WOCHENEND-RISIKO

Positionen dürfen nicht über das Wochenende gehalten werden. Overnight nur zulässig, wenn
das Risiko ausdrücklich begründet wird, ein konkreter Katalysator vorliegt und das
zusätzliche Gap-Risiko akzeptiert wird.

Standardregel: **Intraday vor Overnight. Flat vor Wochenende.**

## 10. POSITIONSGRÖSSE (PFLICHT)

Maximales Risiko pro Trade: **1 % des Gesamtkontos.**
Die Positionsgröße wird immer aus der Stop-Distanz berechnet.

Niemals: Stop an die gewünschte Positionsgröße anpassen · Positionsgröße an den gewünschten Gewinn anpassen.

Immer in dieser Reihenfolge — sie darf niemals verändert werden:
1. Invalidation bestimmen
2. Stop bestimmen
3. Risiko bestimmen
4. Positionsgröße berechnen

## 11. VERLUSTSERIEN-BREMSE (PFLICHT)

Handel sofort pausieren, wenn 3 Verlusttrades in Folge auftreten ODER der Kontostand
innerhalb einer Woche um 3 % fällt.

Nach Auslösung: 1. keine neuen Trades, 2. Review aller Verlusttrades, 3. Analyse der
Fehlerursachen, 4. erst danach Handel fortsetzen. **Rachetrading ist verboten.**

## 12. PERFORMANCE-KALIBRIERUNG (PFLICHT)

Nach mindestens 30 abgeschlossenen Trades prüfen: Gewinnen Trades mit Score ≥ 80 häufiger
als Trades mit Score 70–79?

Wenn nein: Confidence-Modell überarbeiten, Score-Gewichtung prüfen, Checkliste anpassen.
Der Score muss nachweisbar prognostischen Wert besitzen — andernfalls gilt er als nicht validiert.

## 13. GESAMTSTATISTIK (PFLICHT)

Zusätzlich zum Journal führen: Gesamtanzahl Trades · gewonnen · verloren · Trefferquote ·
Ø-CRV · Profit Factor · aktuelle Verlustserie · größte Verlustserie · Ø-Gewinn · Ø-Verlust ·
**Erwartungswert pro Trade = Trefferquote × Ø-Gewinn − Verlustquote × Ø-Verlust.**

Der Erwartungswert ist die eine Zahl, die zählt: positiv = profitabler Trader, negativ = nicht.
Statistiken dürfen erst ab 30 dokumentierten Trades interpretiert werden.

## 14. JOURNAL-PFLICHT

Jeder Trade muss dokumentiert werden. **Nicht dokumentierte Trades gelten als nicht durchgeführt.**
Ohne Journal keine Regeländerung. Ohne Journal keine Strategiebewertung.

## 15. NO-TRADE-REGEL

Die Empfehlung **„HEUTE KEIN TRADE"** ist ausdrücklich eine vollständige und professionelle
Analyse. Kein Trade ist häufig die beste Entscheidung. **Kapitalerhalt hat Vorrang vor Aktivität.**
