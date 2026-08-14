from __future__ import annotations

from typing import Any

from common import json_response


def handler(_event: dict[str, Any], _context: Any) -> dict[str, Any]:
    return json_response(200, {"status": "ok", "service": "aws-serverless-url-shortener"})
