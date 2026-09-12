import re
from datetime import datetime
from bs4 import BeautifulSoup
from ics import Calendar, Event
import requests

BASE_URL = "https://www.sdetmi.com/bratislava/podujatia/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def main():
    cal = Calendar()

    # Prejde prvých 5 stránok aktuálnych akcií
    for page in range(1, 6):
        url = f"{BASE_URL}?p={page}"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                break
        except Exception:
            break

        soup = BeautifulSoup(res.text, "html.parser")
        articles = soup.find_all(["article", "div"], class_=re.compile(r"item|event|podujatie", re.I))

        for item in articles:
            title_tag = item.find(["h2", "h3", "a"])
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            if not title:
                continue

            link = title_tag.get("href", "")
            if link and not link.startswith("http"):
                link = "https://www.sdetmi.com" + link

            event = Event()
            event.name = title
            event.description = f"Zdroj a detail: {link}" if link else "Podujatie zo sdetmi.com"
            event.begin = datetime.now().strftime("%Y-%m-%d")
            event.make_all_day()

            cal.events.add(event)

    # Uloženie do súboru
    with open("sdetmi.ics", "w", encoding="utf-8") as f:
        f.writelines(cal.serialize_iter())


if __name__ == "__main__":
    main()
