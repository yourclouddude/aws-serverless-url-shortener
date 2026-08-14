from __future__ import annotations

import secrets
import string
import time
from typing import Any

from botocore.exceptions import ClientError

from common import (
    get_table,
    json_response,
    parse_expiry_days,
    parse_json_body,
    validate_destination_url,
)

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 8
MAX_COLLISION_RETRIES = 5


def generate_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


def handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    try:
        body = parse_json_body(event)
        destination_url = validate_destination_url(body.get("url"))
        expiry_days = parse_expiry_days(body.get("expires_in_days"))
    except ValueError as exc:
        return json_response(400, {"error": str(exc)})

    now = int(time.time())
    expires_at = now + expiry_days * 24 * 60 * 60
    table = get_table()

    for _ in range(MAX_COLLISION_RETRIES):
        code = generate_code()
        try:
            table.put_item(
                Item={
                    "short_code": code,
                    "destination_url": destination_url,
                    "created_at": now,
                    "expires_at": expires_at,
                },
                ConditionExpression="attribute_not_exists(short_code)",
            )
            return json_response(
                201,
                {
                    "code": code,
                    "path": f"/{code}",
                    "expires_at": expires_at,
                },
            )
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code == "ConditionalCheckFailedException":
                continue
            raise

    return json_response(503, {"error": "Could not allocate a unique short code"})
