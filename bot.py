"""Ali101: send one manually verified V2Ray link per eligible GitHub Actions run.

Every successful send is checkpointed in state.json. The GitHub cron is
best-effort; an elapsed-time check prevents posting less than 11 minutes after
an earlier successful post even at hour boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from checker import ConfigInfo, select_configs

BASE_DIR = Path(__file__).resolve().parent
LOG = logging.getLogger("ali101")
DEFAULT_CHANNEL = "@Ali101_free_V2ray"
MAX_BODY_LENGTH = 3900


class TelegramError(RuntimeError):
    pass


class TelegramClient:
    def __init__(self, token: str, transport: Callable = urlopen):
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.transport = transport

    def send_message(self, payload: dict, retries: int = 2) -> dict:
        request = Request(
            self.base_url + "sendMessage",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(retries + 1):
            try:
                with self.transport(request, timeout=25) as response:
                    result = json.load(response)
                if not result.get("ok"):
                    raise TelegramError("Telegram rejected message; check bot admin rights and HTML formatting")
                return result
            except HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == retries:
                    raise TelegramError(f"Telegram HTTP error {exc.code}") from None
            except (URLError, TimeoutError, OSError) as exc:
                if attempt == retries:
                    raise TelegramError(f"Telegram connection error: {type(exc).__name__}") from None
            time.sleep(2 ** attempt)
        raise TelegramError("Message send failed")


def load_configs(path: Path, check_tcp: bool = False) -> tuple[list[ConfigInfo], dict[str, int]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path.name}; keep your existing configs.txt in the repo")
    return select_configs(path.read_text(encoding="utf-8-sig").splitlines(), check_tcp=check_tcp)


def read_state(path: Path) -> dict:
    """Read new or old state.json, preserving previously published identifiers."""
    blank = {"cursor": 0, "posted_ids": [], "last_sent_at": None}
    if not path.exists():
        return blank
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cursor = data.get("cursor", 0)
        ids = data.get("posted_ids", [])
        last = data.get("last_sent_at", None)
        if (type(cursor) is not int or cursor < 0 or not isinstance(ids, list)
                or any(not isinstance(value, str) for value in ids)
                or (last is not None and (type(last) not in (int, float) or last < 0))):
            raise ValueError("invalid state")
        return {"cursor": cursor, "posted_ids": ids, "last_sent_at": last}
    except (ValueError, OSError, TypeError, AttributeError):
        # Fail closed: a corrupted cursor could spam already published configs.
        raise ValueError("Invalid state.json. Restore a valid state file before publishing") from None


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def channel_footer(channel: str) -> str:
    """Clickable channel link when destination is a valid public @username."""
    if re.fullmatch(r"@[A-Za-z][A-Za-z0-9_]{4,31}", channel):
        username = channel[1:]
        return (f'📢 کانفیگ‌های بیشتر: <a href="https://t.me/{username}">'
                f'{html.escape(channel)}</a>')
    return "📢 کانفیگ‌های بیشتر: Ali101"


def prepare_messages(batch: list[ConfigInfo], numbers: list[int], channel: str) -> list[dict]:
    """Exactly one Telegram message per URI, without any inline copy buttons."""
    if len(batch) != len(numbers):
        raise ValueError("Every config must have its own number")
    result = []
    footer = channel_footer(channel)
    for info, number in zip(batch, numbers):
        # Telegram renders <pre> as a monospace code block that can be copied in
        # supported clients. Unlike the CopyTextButton, no 256-character cap.
        safe_uri = html.escape(info.uri, quote=False)
        content = (f"🌐 <b>Ali101 | کانفیگ رایگان · {info.protocol}</b>\n"
                   f"#V2Ray #FreeVPN #Config #کانفیگ_رایگان #{info.protocol}\n\n"
                   f"<pre>{safe_uri}</pre>\n\n"
                   f"{footer}")
        if len(content) > MAX_BODY_LENGTH:
            raise ValueError(f"Config {number} is too long for a Telegram message")
        result.append({
            "chat_id": channel,
            "text": content,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        })
    return result


def _choose_next(state: dict, ids: list[str]) -> tuple[int, set[str]]:
    posted = set(state["posted_ids"]) & set(ids)
    cursor = state["cursor"] % len(ids)
    for offset in range(len(ids)):
        index = (cursor + offset) % len(ids)
        if ids[index] not in posted:
            return index, posted
    return cursor, set()  # Only repeat when the full current list has been posted.


def publish_once(*, configs_path: Path, state_path: Path, channel: str,
                 token: str | None, interval_minutes: int = 11,
                 now: float | None = None, dry_run: bool = False,
                 force: bool = False, check_tcp: bool = False,
                 client: TelegramClient | None = None) -> dict:
    if interval_minutes < 1:
        raise ValueError("SEND_INTERVAL_MINUTES must be positive")
    current_time = time.time() if now is None else now
    state = read_state(state_path)
    last = state["last_sent_at"]
    if not force and last is not None:
        if current_time < last:
            return {"status": "skipped_clock_backward", "count": 0}
        if current_time - last < interval_minutes * 60:
            return {"status": "skipped_wait", "count": 0,
                    "seconds_remaining": int(interval_minutes * 60 - (current_time - last))}

    infos, stats = load_configs(configs_path, check_tcp=check_tcp)
    if not infos:
        raise ValueError("No structurally valid configs found in configs.txt")
    if not dry_run and not token:
        raise ValueError("BOT_TOKEN missing; set the GitHub Actions secret")
    ids = [hashlib.sha256(info.uri.encode("utf-8")).hexdigest()[:24] for info in infos]
    index, posted = _choose_next(state, ids)
    message = prepare_messages([infos[index]], [101 + index], channel)[0]
    if dry_run:
        return {"status": "preview", "count": 1, "stats": stats}

    sender = client if client is not None else TelegramClient(token)
    sender.send_message(message)
    posted.add(ids[index])
    state.update({"cursor": (index + 1) % len(infos), "posted_ids": sorted(posted),
                  "last_sent_at": current_time})
    save_state(state_path, state)
    return {"status": "sent", "count": 1, "stats": stats,
            "utc_time": datetime.fromtimestamp(current_time, tz=timezone.utc).isoformat()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Ali101: send one config after at least 11 minutes")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Manually override the elapsed-time guard")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        result = publish_once(
            configs_path=BASE_DIR / "configs.txt", state_path=BASE_DIR / "state.json",
            channel=os.getenv("CHANNEL_ID", DEFAULT_CHANNEL), token=os.getenv("BOT_TOKEN"),
            interval_minutes=int(os.getenv("SEND_INTERVAL_MINUTES", "11")),
            dry_run=args.dry_run, force=args.force or os.getenv("FORCE_SEND") == "true",
            check_tcp=os.getenv("ENABLE_TCP_CHECK") == "1",
        )
        LOG.info("Result: %s", json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, OSError, TelegramError) as exc:
        LOG.error("Run failed: %s", str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
