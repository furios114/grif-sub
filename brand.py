#!/usr/bin/env python3
"""
GRIF VPN — автообновление подписки.
Источник: только VansFenix vless.txt
Названия: [🇬🇷 GRIF | <оригинальное имя без VFPARSER>]
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
# ===================================


def fetch_source(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def get_old_name(line: str) -> str:
    return line.split("#", 1)[1] if "#" in line else ""


def clean_old_name(name: str) -> str:
    """Убираем мусорные маркеры из имени."""
    # URL-decode на случай %20 и прочего
    name = urllib.parse.unquote(name)

    # Убираем "VFPARSER" в любом регистре и с любыми пробелами вокруг
    name = re.sub(r"\s*VFPARSER\s*", " ", name, flags=re.IGNORECASE)

    # Схлопываем двойные пробелы
    name = re.sub(r"\s+", " ", name).strip()

    # Убираем висячие разделители в конце/начале
    name = name.strip(" |")

    return name


def process_line(line: str) -> str:
    line = line.strip()
    old_name = get_old_name(line)
    clean = clean_old_name(old_name)

    if clean:
        new_name = PREFIX + clean
    else:
        new_name = PREFIX.rstrip(" |")

    base = line.split("#", 1)[0]
    # Кодируем только то, что нужно (пробелы, пайпы, эмодзи — оставляем как есть)
    return base + "#" + new_name


def main():
    print(f"→ Скачиваю источник: {SOURCE_URL}")
    raw = fetch_source(SOURCE_URL)
    lines = raw.splitlines()
    print(f"  Получено строк: {len(lines)}")

    kept = []
    skipped_not_vless = 0

    for l in lines:
        l = l.strip()
        if not l:
            continue

        if l.startswith("#"):
            kept.append(l)
            continue

        if not l.lower().startswith("vless://"):
            skipped_not_vless += 1
            continue

        kept.append(process_line(l))

    # Чистим шапку источника и ставим свою
    filtered = []
    for l in kept:
        if l.startswith("#profile-title:") or \
           l.startswith("#announce:") or \
           l.startswith("#profile-update-interval:") or \
           l.startswith("#support-url:") or \
           l.startswith("#profile-web-page-url:") or \
           l.startswith("#routing-enable:"):
            continue
        filtered.append(l)

    result = [
        f"#profile-title: {PROFILE_TITLE}",
        f"#profile-update-interval: {UPDATE_INTERVAL}",
        f"#announce: {ANNOUNCE}",
    ] + [x for x in filtered if x.strip()]

    Path(OUTPUT_FILE).write_text("\n".join(result) + "\n", encoding="utf-8")
    print(f"✅ {OUTPUT_FILE}")
    print(f"   Ключей: {sum(1 for x in result if x.startswith('vless://'))}")
    print(f"   Не-vless выкинуто: {skipped_not_vless}")


if __name__ == "__main__":
    main()