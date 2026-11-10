"""
Calcule les KPI mensuels par hôtel à partir de hotel_bookings.csv
(simule la couche de traitement ; sortie exportée vers MySQL par Sqoop)
et affiche les statistiques descriptives utilisées dans la présentation.
  python prepare_kpi.py
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

rows = list(csv.DictReader(open(HERE / "hotel_bookings.csv", encoding="utf-8")))
kpi = defaultdict(lambda: {"n": 0, "c": 0, "adr": 0.0, "nights": 0, "rev": 0.0})
stats = {"total": len(rows), "by_hotel": defaultdict(lambda: [0, 0]), "by_deposit": defaultdict(lambda: [0, 0]),
         "by_month": defaultdict(int), "by_segment": defaultdict(lambda: [0, 0]), "countries": set(),
         "lead": defaultdict(lambda: [0, 0])}

for r in rows:
    canc = int(r["is_canceled"])
    nights = int(r["stays_in_weekend_nights"]) + int(r["stays_in_week_nights"])
    adr = float(r["adr"])
    key = (r["hotel"], f'{r["arrival_date_year"]}-{MONTHS.index(r["arrival_date_month"]) + 1:02d}')
    k = kpi[key]
    k["n"] += 1; k["c"] += canc; k["adr"] += adr
    if not canc:
        k["nights"] += nights; k["rev"] += adr * nights
    stats["by_hotel"][r["hotel"]][0] += 1; stats["by_hotel"][r["hotel"]][1] += canc
    stats["by_deposit"][r["deposit_type"]][0] += 1; stats["by_deposit"][r["deposit_type"]][1] += canc
    stats["by_segment"][r["market_segment"]][0] += 1; stats["by_segment"][r["market_segment"]][1] += canc
    stats["by_month"][r["arrival_date_month"]] += 1
    stats["countries"].add(r["country"])
    lt = int(r["lead_time"])
    b = "0-30 j" if lt <= 30 else "31-90 j" if lt <= 90 else "91-180 j" if lt <= 180 else "> 180 j"
    stats["lead"][b][0] += 1; stats["lead"][b][1] += canc

with open(HERE / "kpi_monthly.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["hotel", "year_month_key", "total_bookings", "canceled_bookings", "cancel_rate_pct",
                "avg_adr", "room_nights", "revenue_realized"])
    for (h, ym), k in sorted(kpi.items()):
        w.writerow([h, ym, k["n"], k["c"], round(100 * k["c"] / k["n"], 2), round(k["adr"] / k["n"], 2),
                    k["nights"], round(k["rev"], 2)])

out = {
    "total": stats["total"],
    "cancel_rate": round(100 * sum(int(r["is_canceled"]) for r in rows) / len(rows), 1),
    "countries": len(stats["countries"]),
    "by_hotel": {h: [n, round(100 * c / n, 1)] for h, (n, c) in stats["by_hotel"].items()},
    "by_deposit": {h: [n, round(100 * c / n, 1)] for h, (n, c) in stats["by_deposit"].items()},
    "by_segment": {h: [n, round(100 * c / n, 1)] for h, (n, c) in stats["by_segment"].items()},
    "by_month": {m: stats["by_month"][m] for m in MONTHS},
    "lead": {b: [n, round(100 * c / n, 1)] for b, (n, c) in stats["lead"].items()},
    "lost_revenue": round(sum(float(r["adr"]) * (int(r["stays_in_weekend_nights"]) + int(r["stays_in_week_nights"]))
                              for r in rows if r["is_canceled"] == "1")),
}
json.dump(out, open(HERE / "stats.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
