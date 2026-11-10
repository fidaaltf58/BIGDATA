"""
Génère des logs Apache (format "combined") simulant le site de réservation de l'hôtel.
Usage :
  python generate_weblogs.py --out ../../02_Dataset/web_access.log --lines 5000   # fichier échantillon
  python generate_weblogs.py --live                                              # dépose un fichier toutes les 10 s dans ../spool (pour Flume)
"""
import argparse
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

PAGES = [
    ("GET", "/", 200, 0.18),
    ("GET", "/rooms", 200, 0.14),
    ("GET", "/rooms/deluxe-sea-view", 200, 0.06),
    ("GET", "/rooms/standard-double", 200, 0.06),
    ("GET", "/booking/search?checkin={ci}&nights={n}&adults={a}", 200, 0.20),
    ("GET", "/booking/quote?room={r}&checkin={ci}&nights={n}", 200, 0.10),
    ("POST", "/booking/confirm", 201, 0.06),
    ("POST", "/booking/cancel", 200, 0.03),
    ("GET", "/offers/early-booking", 200, 0.05),
    ("GET", "/contact", 200, 0.03),
    ("GET", "/booking/payment", 500, 0.01),
    ("GET", "/old-promo-2015", 404, 0.02),
    ("GET", "/static/css/main.css", 304, 0.06),
]
AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
]
REFERRERS = ["-", "https://www.google.com/", "https://www.booking.com/", "https://www.expedia.com/",
             "https://www.facebook.com/", "https://www.tripadvisor.com/"]
ROOMS = ["A", "C", "D", "E", "F", "G"]
WEIGHTS = [p[3] for p in PAGES]


def log_line(ts: datetime) -> str:
    method, path, status, _ = random.choices(PAGES, weights=WEIGHTS)[0]
    ci = (ts + timedelta(days=random.randint(1, 300))).strftime("%Y-%m-%d")
    path = path.format(ci=ci, n=random.randint(1, 10), a=random.randint(1, 4), r=random.choice(ROOMS))
    ip = f"{random.randint(2, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    size = 0 if status == 304 else random.randint(400, 48000)
    stamp = ts.strftime("%d/%b/%Y:%H:%M:%S +0000")
    return (f'{ip} - - [{stamp}] "{method} {path} HTTP/1.1" {status} {size} '
            f'"{random.choice(REFERRERS)}" "{random.choice(AGENTS)}"')


def write_file(path: Path, lines: int, start: datetime) -> None:
    ts = start
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for _ in range(lines):
            ts += timedelta(seconds=random.expovariate(1 / 3))
            f.write(log_line(ts) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web_access.log")
    ap.add_argument("--lines", type=int, default=5000)
    ap.add_argument("--live", action="store_true", help="dépose un nouveau fichier toutes les 10 s dans ../spool")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    if not args.live:
        write_file(Path(args.out), args.lines, datetime(2017, 8, 1, 6, 0, 0))
        print(f"{args.lines} lignes écrites dans {args.out}")
        return

    spool = Path(__file__).resolve().parent.parent / "spool"
    spool.mkdir(exist_ok=True)
    i = 0
    print(f"Mode live : un fichier de 200 lignes toutes les 10 s dans {spool} (Ctrl+C pour arrêter)")
    while True:
        i += 1
        tmp = spool / f".tmp_{i}"
        write_file(tmp, 200, datetime.utcnow())
        final = spool / f"access_{datetime.now():%Y%m%d_%H%M%S}.log"
        tmp.rename(final)  # renommage atomique : Flume ne lit jamais un fichier incomplet
        print("déposé :", final.name)
        time.sleep(10)


if __name__ == "__main__":
    main()
