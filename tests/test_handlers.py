from __future__ import annotations

import json

from botocore.exceptions import ClientError

import create_link
import health
import redirect


class FakePutTable:
    def __init__(self, fail_first: bool = False):
        self.items = []
        self.fail_first = fail_first
        self.calls = 0

    def put_item(self, **kwargs):
        self.calls += 1
        if self.fail_first and self.calls == 1:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException", "Message": "collision"}},
                "PutItem",
            )
        self.items.append(kwargs)
        return {}


class FakeGetTable:
    def __init__(self, item=None):
        self.item = item

    def get_item(self, **_kwargs):
        return {"Item": self.item} if self.item is not None else {}


def body(response):
    return json.loads(response["body"])


def test_health():
    response = health.handler({}, None)
    assert response["statusCode"] == 200
    assert body(response)["status"] == "ok"


def test_create_rejects_invalid_url(monkeypatch):
    monkeypatch.setattr(create_link, "get_table", lambda: (_ for _ in ()).throw(AssertionError()))
    response = create_link.handler({"body": json.dumps({"url": "ftp://example.com"})}, None)
    assert response["statusCode"] == 400
    assert "http or https" in body(response)["error"]


def test_create_link_success(monkeypatch):
    table = FakePutTable()
    monkeypatch.setattr(create_link, "get_table", lambda: table)
    monkeypatch.setattr(create_link, "generate_code", lambda: "aB3xQ7zK")

    response = create_link.handler(
        {"body": json.dumps({"url": "https://example.com/aws", "expires_in_days": 7})},
        None,
    )

    assert response["statusCode"] == 201
    assert body(response)["code"] == "aB3xQ7zK"
    assert table.items[0]["ConditionExpression"] == "attribute_not_exists(short_code)"
    assert table.items[0]["Item"]["destination_url"] == "https://example.com/aws"


def test_create_retries_on_code_collision(monkeypatch):
    table = FakePutTable(fail_first=True)
    codes = iter(["AAAAAAAA", "BBBBBBBB"])
    monkeypatch.setattr(create_link, "get_table", lambda: table)
    monkeypatch.setattr(create_link, "generate_code", lambda: next(codes))

    response = create_link.handler({"body": json.dumps({"url": "https://example.com"})}, None)

    assert response["statusCode"] == 201
    assert body(response)["code"] == "BBBBBBBB"
    assert table.calls == 2


def test_redirect_success(monkeypatch):
    monkeypatch.setattr(
        redirect,
        "get_table",
        lambda: FakeGetTable(
            {
                "short_code": "aB3xQ7zK",
                "destination_url": "https://example.com/aws",
                "expires_at": 9_999_999_999,
            }
        ),
    )

    response = redirect.handler({"pathParameters": {"code": "aB3xQ7zK"}}, None)

    assert response["statusCode"] == 302
    assert response["headers"]["location"] == "https://example.com/aws"


def test_redirect_missing_link(monkeypatch):
    monkeypatch.setattr(redirect, "get_table", lambda: FakeGetTable())
    response = redirect.handler({"pathParameters": {"code": "aB3xQ7zK"}}, None)
    assert response["statusCode"] == 404


def test_redirect_expired_link(monkeypatch):
    monkeypatch.setattr(redirect.time, "time", lambda: 200)
    monkeypatch.setattr(
        redirect,
        "get_table",
        lambda: FakeGetTable(
            {
                "short_code": "aB3xQ7zK",
                "destination_url": "https://example.com",
                "expires_at": 100,
            }
        ),
    )

    response = redirect.handler({"pathParameters": {"code": "aB3xQ7zK"}}, None)
    assert response["statusCode"] == 410


def test_redirect_rejects_malformed_code(monkeypatch):
    monkeypatch.setattr(redirect, "get_table", lambda: (_ for _ in ()).throw(AssertionError()))
    response = redirect.handler({"pathParameters": {"code": "bad!"}}, None)
    assert response["statusCode"] == 400
