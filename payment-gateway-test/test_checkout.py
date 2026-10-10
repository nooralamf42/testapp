#!/usr/bin/env python3
"""Standalone test for the gtw.online-epayment.com encrypted checkout GET API.

Builds the mandatory query parameters for the hosted checkout URL
(https://gtw.online-epayment.com/checkout) and sends the GET request,
reporting the response status, redirect chain, and a snippet of the body.

Credentials are read from environment variables (see .env.example) so
nothing secret is hardcoded or committed.
"""

import os
import sys
import uuid
from pathlib import Path

import requests

GATEWAY_URL = "https://gtw.online-epayment.com/checkout"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"Missing required env var: {name} (see .env.example)")
    return value


def main() -> None:
    load_dotenv(Path(__file__).parent / ".env")

    private_key = require("GTW_PRIVATE_KEY")
    public_key = require("GTW_PUBLIC_KEY")
    ter_no = require("GTW_TER_NO")

    reference = os.environ.get("GTW_REFERENCE", "").strip() or f"TEST-{uuid.uuid4().hex[:10]}"
    source_url = os.environ.get("GTW_SOURCE_URL", "https://example.com/checkout")
    return_url = os.environ.get("GTW_RETURN_URL", "https://example.com/payment/return")
    webhook_url = os.environ.get("GTW_WEBHOOK_URL", "https://example.com/payment/webhook")
    bill_amt = os.environ.get("GTW_BILL_AMT", "10.00")
    product_name = os.environ.get("GTW_PRODUCT_NAME", "Test Product")

    params = {
        "private_key": private_key,
        "public_key": public_key,
        "terNO": ter_no,
        "bill_ip": "127.0.0.1",
        "source_url": source_url,
        "bill_amt": bill_amt,
        "product_name": product_name,
        "fullname": "Test Customer",
        "bill_email": "test.customer@example.com",
        "bill_address": "123 Test Street",
        "bill_city": "Test City",
        "bill_country": "US",
        "bill_phone": "15555550123",
        "reference": reference,
        "webhook_url": webhook_url,
        "return_url": return_url,
    }

    print(f"GET {GATEWAY_URL}")
    print(f"reference = {reference}")

    try:
        response = requests.get(GATEWAY_URL, params=params, timeout=30, allow_redirects=True)
    except requests.RequestException as exc:
        sys.exit(f"Request failed: {exc}")

    print(f"\nFinal status: {response.status_code}")
    if response.history:
        print("Redirect chain:")
        for hop in response.history:
            print(f"  {hop.status_code} -> {hop.headers.get('Location')}")
    print(f"Final URL: {response.url}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print("\n--- Body (first 1000 chars) ---")
    print(response.text[:1000])


if __name__ == "__main__":
    main()
