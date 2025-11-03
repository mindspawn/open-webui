from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

from open_webui.env import DATA_DIR

_PROMPT_LOG_FILENAME = "prompt_usage.log"
_PROMPT_LOG_PATH = Path(DATA_DIR) / _PROMPT_LOG_FILENAME
_PROMPT_LOG_LOCK = Lock()


def _derive_user_id(email: Optional[str]) -> str:
    if not email:
        return "unknown"
    if "@" not in email:
        return email
    return email.split("@", 1)[0]


def log_prompt_usage(command: str, user_email: Optional[str]) -> None:
    """
    Append a prompt usage entry to the prompt usage log file.
    Each entry is formatted as: "<ISO8601 timestamp> | command=<command> | user=<user id>"
    """
    if not command:
        return

    timestamp = datetime.now(timezone.utc).isoformat()
    user_id = _derive_user_id(user_email)
    entry = f"{timestamp} | command={command} | user={user_id}\n"

    try:
        _PROMPT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _PROMPT_LOG_LOCK:
            with _PROMPT_LOG_PATH.open("a", encoding="utf-8") as log_file:
                log_file.write(entry)
    except Exception:
        # Logging must never break the request flow, so swallow all errors.
        pass
