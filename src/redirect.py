from __future__ import annotations

import re
import time
from typing import Any

from common import get_table, json_response

CODE_PATTERN = re.compile(r"^[A-Za-z0-9]{8}$")


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    code = (event.get("pathParameters") or {}).get("code", "")
    if not CODE_PATTERN.fullmatch(code):
        return json_response(400, {"error": "Invalid short code"})

    result = get_table().get_item(Key={"short_code": code}, ConsistentRead=False)
    item = result.get("Item")
    if not item:
        return json_response(404, {"error": "Short link not found"})

    expires_at = int(item.get("expires_at", 0))
    if expires_at <= int(time.time()):
        return json_response(410, {"error": "Short link has expired"})

    destination_url = item.get("destination_url")
    if not isinstance(destination_url, str) or not destination_url:
        return json_response(500, {"error": "Stored link is invalid"})

    return {
        "statusCode": 302,
        "headers": {
            "location": destination_url,
            "cache-control": "no-store",
        },
        "body": "",
    }
