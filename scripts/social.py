#!/usr/bin/env python3
"""Post the next pending row from queue.csv to the platforms listed in that row."""
import csv, os, sys, urllib.parse, urllib.request
import tweepy

QUEUE = "queue.csv"
LIMIT = 275


def load():
    with open(QUEUE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(rows):
    with open(QUEUE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def compose(row, for_x):
    text = f"{row['title']}\n\n{row['blurb']}\n{row['url']}"
    if for_x and len(text) > LIMIT:
        text = f"{row['title'][:120]}\n{row['url']}"
    return text


def post_x(text):
    client = tweepy.Client(
        os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_SECRET"])
    client.create_tweet(text=text)


def post_telegram(text):
    data = urllib.parse.urlencode({
        "chat_id": os.environ["TELEGRAM_CHAT_ID"], "text": text}).encode()
    urllib.request.urlopen(
        f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage",
        data=data, timeout=30)


HANDLERS = {"x": (post_x, True), "telegram": (post_telegram, False)}


def main():
    rows = load()
    row = next((r for r in rows if r["status"].strip() == "pending"), None)
    if row is None:
        print("queue empty - nothing to post")
        return

    posted = False
    for p in [p.strip() for p in row["platforms"].split(";") if p.strip()]:
        handler, for_x = HANDLERS.get(p, (None, False))
        if handler is None:
            continue
        try:
            handler(compose(row, for_x))
            print(f"  posted to {p}")
            posted = True
        except Exception as e:
            print(f"  {p} failed: {e}", file=sys.stderr)

    if posted:
        row["status"] = "posted"
        save(rows)


if __name__ == "__main__":
    main()
