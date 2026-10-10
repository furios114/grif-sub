#!/usr/bin/env python3
"""
GRIF VPN — автообновление подписки.
Источник: ТОЛЬКО https://raw.githubusercontent.com/VansFenix/vpnparser/refs/heads/main/vless.txt
Всё, что не vless:// — выкидывается.
"""

import re
import urllib.parse
import urllib.request
from pathlib import Path

# ============ НАСТРОЙКИ ============
SOURCE_URL = "https://raw.githubusercontent.com/VansFenix/vpnparser/refs/heads/main/vless.txt"
OUTPUT_FILE = "grif_branded.txt"
PREFIX = "🇬🇷 GRIF | "
PROFILE_TITLE = "GRIF VPN"
ANNOUNCE = "GRIF VPN - VPN с множеством серверов"
UPDATE_INTERVAL = 1

# Оставлять ли security=none (True — оставляем как в источнике)
KEEP_NONE = True

# Убирать ли "Белый айпи"
DROP_WHITE_LIST = True
# ===================================


COUNTRY_NAMES = {
    "AE": "ОАЭ",       "AM": "Армения",    "AT": "Австрия",
    "AU": "Австралия", "AZ": "Азербайджан","BG": "Болгария",
    "BR": "Бразилия",  "BY": "Беларусь",   "CA": "Канада",
    "CH": "Швейцария", "CN": "Китай",      "CZ": "Чехия",
    "DE": "Германия",  "DK": "Дания",      "EE": "Эстония",
    "ES": "Испания",   "FI": "Финляндия",  "FR": "Франция",
    "GB": "Великобритания", "GE": "Грузия","HK": "Гонконг",
    "HU": "Венгрия",   "ID": "Индонезия",  "IE": "Ирландия",
    "IL": "Израиль",   "IN": "Индия",      "IR": "Иран",
    "IT": "Италия",    "JP": "Япония",     "KR": "Южная Корея",
    "KZ": "Казахстан", "LT": "Литва",      "LV": "Латвия",
    "MD": "Молдова",   "MY": "Малайзия",   "NL": "Нидерланды",
    "NO": "Норвегия",  "PL": "Польша",     "PT": "Португалия",
    "RO": "Румыния",   "RS": "Сербия",     "RU": "Россия",
    "SA": "Саудовская Аравия", "SC": "Сейшелы", "SE": "Швеция",
    "SG": "Сингапур",  "TR": "Турция",     "UA": "Украина",
    "UK": "Великобритания", "US": "США",   "UZ": "Узбекистан",
    "ZA": "ЮАР",
}


def flag(code: str) -> str:
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())


def extract_country(name: str):
    m = re.search(r"\[([A-Za-z]{2})\]", name)
    if m and m.group(1).upper() in COUNTRY_NAMES:
        return m.group(1).upper()
    for token in re.findall(r"\b[A-Z]{2}\b", name):
        if token in COUNTRY_NAMES:
            return token
    m = re.search(r"([\U0001F1E6-\U0001F1FF]{2})", name)
    if m:
        c1, c2 = m.group(1)
        code = chr(ord(c1) - 0x1F1E6 + ord("A")) + chr(ord(c2) - 0x1F1E6 + ord("A"))
        if code in COUNTRY_NAMES:
            return code
    return None


def is_white_list(old_name: str) -> bool:
    n = urllib.parse.unquote(old_name).lower()
    return "белый айпи" in n


def build_name(old_name: str, fallback_index: int) -> str:
    old_name = urllib.parse.unquote(old_name or "")
    code = extract_country(old_name)
    if code:
        return f"{PREFIX}{flag(code)} {COUNTRY_NAMES[code]}"
    return f"{PREFIX}{fallback_index:02d}"


def get_old_name(line: str) -> str:
    return line.split("#", 1)[1] if "#" in line else ""


def is_none_security(line: str) -> bool:
    return "security=none" in line


def process_line(line: str, fallback_index: int) -> str:
    """
    Обрабатываем ТОЛЬКО vless:// — остальное отсеивается раньше.
    """
    line = line.strip()
    old_name = get_old_name(line)
    new_name = build_name(old_name, fallback_index)

    base = line.split("#", 1)[0] if "#" in line else line
    return base + "#" + urllib.parse.quote(new_name)


def fetch_source(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def main():
    print(f"→ Скачиваю источник: {SOURCE_URL}")
    raw = fetch_source(SOURCE_URL)
    lines = raw.splitlines()
    print(f"  Получено строк: {len(lines)}")

    kept = []
    skipped_white = 0
    skipped_none = 0
    skipped_not_vless = 0
    fallback = 0

    for l in lines:
        l = l.strip()
        if not l or l.startswith("#"):
            continue

        # ⛔ ЖЁСТКО: только vless://
        if not l.lower().startswith("vless://"):
            skipped_not_vless += 1
            continue

        old_name = get_old_name(l)

        # ⛔ Убираем "Белый айпи"
        if DROP_WHITE_LIST and is_white_list(old_name):
            skipped_white += 1
            continue

        # ⛔ По желанию: убираем security=none
        if not KEEP_NONE and is_none_security(l):
            skipped_none += 1
            continue

        fallback += 1
        kept.append(process_line(l, fallback))

    result = [
        f"#profile-title: {PROFILE_TITLE}",
        f"#profile-update-interval: {UPDATE_INTERVAL}",
        f"#announce: {ANNOUNCE}",
    ] + kept

    Path(OUTPUT_FILE).write_text("\n".join(result) + "\n", encoding="utf-8")
    print(f"✅ {OUTPUT_FILE}: {len(kept)} ключей")
    print(f"   Убрано белых списков:      {skipped_white}")
    print(f"   Убрано security=none:      {skipped_none}")
    print(f"   Убрано не-vless:           {skipped_not_vless}")


if __name__ == "__main__":
    main()