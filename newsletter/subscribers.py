# newsletter/subscribers.py
from __future__ import annotations

from pathlib import Path
from typing import Set, Iterable

NEWS_SUBSCRIBERS_FILE = Path("news_subscribers.txt")


def _ensure_file_dir() -> None:
    if NEWS_SUBSCRIBERS_FILE.parent != Path("."):
        NEWS_SUBSCRIBERS_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_subscribers() -> Set[int]:
    if not NEWS_SUBSCRIBERS_FILE.exists():
        return set()

    try:
        lines = NEWS_SUBSCRIBERS_FILE.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print(f"[subscribers] failed to read file {NEWS_SUBSCRIBERS_FILE}: {e}")
        return set()

    subs: Set[int] = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            subs.add(int(line))
        except ValueError:
            print(f"[subscribers] skip invalid line in file: {line!r}")
            continue
    return subs


def save_subscribers(subs: Iterable[int]) -> None:
   
    _ensure_file_dir()
    # تبدیل به set تا تکراری‌ها حذف شوند
    unique_subs = sorted({int(c) for c in subs})
    text = "\n".join(str(cid) for cid in unique_subs)
    try:
        NEWS_SUBSCRIBERS_FILE.write_text(text, encoding="utf-8")
    except OSError as e:
        print(f"[subscribers] failed to write file {NEWS_SUBSCRIBERS_FILE}: {e}")


def add_subscriber(chat_id: int) -> None:
    """
    یک chat_id را به لیست اضافه می‌کند (اگر قبلا نبوده).
    """
    subs = load_subscribers()
    if chat_id in subs:
        return
    subs.add(chat_id)
    save_subscribers(subs)


def remove_subscriber(chat_id: int) -> None:
    """
    یک chat_id را از لیست حذف می‌کند (اگر موجود باشد).
    """
    subs = load_subscribers()
    if chat_id not in subs:
        return
    subs.remove(chat_id)
    save_subscribers(subs)


def is_subscribed(chat_id: int) -> bool:
    """
    بررسی می‌کند که آیا این chat_id در لیست سابسکرایبرها هست یا نه.
    """
    subs = load_subscribers()
    return chat_id in subs


def get_all_subscribers() -> Set[int]:

    return load_subscribers()


if __name__ == "__main__":
    print("== Manual test for subscribers module ==")

    test_file = Path("news_subscribers_test.txt")
    NEWS_SUBSCRIBERS_FILE = test_file

    if test_file.exists():
        test_file.unlink()

    print("Initial subscribers:", load_subscribers())

    print("Adding 111 and 222 ...")
    add_subscriber(111)
    add_subscriber(222)
    print("Now subscribers:", load_subscribers())

    print("is_subscribed(111)?", is_subscribed(111))
    print("is_subscribed(333)?", is_subscribed(333))

    print("Removing 111 ...")
    remove_subscriber(111)
    print("Now subscribers:", load_subscribers())

    print("Manual test finished.")
