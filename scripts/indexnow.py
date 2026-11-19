#!/usr/bin/env python3
"""Submit every URL in the sitemap to IndexNow (Bing, Yandex, Seznam, Naver, Yep)."""
import json, os, sys, time, urllib.error, urllib.request
import xml.etree.ElementTree as ET

HOST = os.environ.get("SITE_HOST", "pozijoist.com")
KEY = os.environ["INDEXNOW_KEY"]
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
UA = {"User-Agent": f"pozijoist-bot/1.0 (+https://{HOST})"}
MAX_BATCH = 100


def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=30).read()
        except Exception as e:
            if i == tries - 1:
                print(f"  skip {url}: {e}", file=sys.stderr)
                return b""
            time.sleep(2 ** i)


def collect(urls, depth=0):
    pages = set()
    for u in urls:
        if depth > 2:
            continue
        body = fetch(u)
        if not body:
            continue
        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            continue
        locs = [e.text.strip() for e in root.findall(".//s:loc", NS) if e.text]
        pages |= {l for l in locs if not l.endswith(".xml")}
        pages |= collect([l for l in locs if l.endswith(".xml")], depth + 1)
    return pages


def main():
    urls = sorted(collect([f"https://{HOST}/sitemap.xml"]))
    if not urls:
        sys.exit("sitemap fetch failed - nothing submitted")
    print(f"{len(urls)} urls found")

    for i in range(0, len(urls), MAX_BATCH):
        batch = urls[i:i + MAX_BATCH]
        payload = {"host": HOST, "key": KEY,
                   "keyLocation": f"https://{HOST}/{KEY}.txt", "urlList": batch}
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=json.dumps(payload).encode(),
            headers={**UA, "Content-Type": "application/json; charset=utf-8"},
            method="POST")
        try:
            r = urllib.request.urlopen(req, timeout=30)
            print(f"  submitted {len(batch)} -> HTTP {r.status}")
        except urllib.error.HTTPError as e:
            body = e.read()[:200].decode(errors="replace")
            print(f"  batch failed {e.code}: {body}", file=sys.stderr)
        time.sleep(1)


if __name__ == "__main__":
    main()
