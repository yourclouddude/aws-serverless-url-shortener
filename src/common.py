from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any
from urllib.parse import urlparse

import boto3

MAX_URL_LENGTH = 2048
DEFAULT_EXPIRY_DAYS = 30
MAX_EXPIRY_DAYS = 365


@lru_cache(maxsize=1)
def get_table():
    table_name = os.environ.get("TABLE_NAME")
    if not table_name:
        raise RuntimeError("TABLE_NAME environment variable is required")
    return boto3.resource("dynamodb").Table(table_name)


def json_response(status_code: int, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload, separators=(",", ":")),
    }


def parse_json_body(event: dict[str, Any]) -> dict[str, Any]:
    raw = event.get("body")
    if not raw:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Request body must be valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Request body must be a JSON object")
    return value


def validate_destination_url(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("url must be a string")

    url = value.strip()
    if not url:
        raise ValueError("url is required")
    if len(url) > MAX_URL_LENGTH:
        raise ValueError(f"url must be at most {MAX_URL_LENGTH} characters")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("url must be an absolute http or https URL")

    return url


def parse_expiry_days(value: Any) -> int:
    if value is None:
        return DEFAULT_EXPIRY_DAYS
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("expires_in_days must be an integer")
    if not 1 <= value <= MAX_EXPIRY_DAYS:
        raise ValueError(f"expires_in_days must be between 1 and {MAX_EXPIRY_DAYS}")
    return value
