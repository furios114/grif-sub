#!/usr/bin/env python3
"""
GRIF VPN — автообновление подписки.
Источник: только VansFenix vless.txt
Названия: [🇬🇷 GRIF | <оригинальное имя из VansFenix>]
"""

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
    """Достаём оригинальное имя после #"""
    return line.split("#", 1)[1] if "#" in line else ""


def process_line(line: str) -> str:
    """
    Берём оригинальную строку vless:// как есть,
    меняем только фрагмент (#...) на [PREFIX + оригинальное имя].
    Всё остальное (UUID, адрес, порт, параметры) — не трогаем.
    """
    line = line.strip()
    old_name = get_old_name(line)

    # Если у ключа вообще нет имени — ставим просто GRIF
    if old_name:
        new_name = PREFIX + old_name
    else:
        new_name = PREFIX.rstrip(" |")

    base = line.split("#", 1)[0]
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

        # Комментарии/шапку источника сохраняем как есть
        if l.startswith("#"):
            kept.append(l)
            continue

        # Только vless:// — как в источнике
        if not l.lower().startswith("vless://"):
            skipped_not_vless += 1
            continue

        kept.append(process_line(l))

    # Заменяем шапку на свою (для брендинга)
    # Убираем старые #profile-title, #announce и т.п. из источника
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
    print(f"   Ключей сохранено: {sum(1 for x in result if x.startswith('vless://'))}")
    print(f"   Не-vless выкинуто: {skipped_not_vless}")


if __name__ == "__main__":
    main()