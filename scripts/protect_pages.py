#!/usr/bin/env python3
"""
Post-build encryption script for Quartz protected pages.

Usage:
  1. Run `npx quartz build` first
  2. Set env vars:  PROTECT_KEY=<64-hex-char AES key>
  3. Run: py scripts/protect_pages.py

Mark pages as protected by adding `protected: true` to their frontmatter.
"""

import os
import re
import sys
import secrets
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing dependency: pip install beautifulsoup4")

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    sys.exit("Missing dependency: pip install cryptography")

# ─── Config ──────────────────────────────────────────────────────────────────
QUARTZ_ROOT = Path(__file__).parent.parent
CONTENT_DIR = QUARTZ_ROOT / "content"
PUBLIC_DIR  = QUARTZ_ROOT / "public"

AES_KEY_HEX = "081e8df7c3a23aae098a8e6c791ffba07c20d09ac95391b7feb75d3388fde483"
# ─────────────────────────────────────────────────────────────────────────────


def load_frontmatter(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    try:
        end = text.index("---", 3)
        return yaml.safe_load(text[3:end]) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def find_protected_files() -> list[Path]:
    return [
        f for f in CONTENT_DIR.rglob("*.md")
        if load_frontmatter(f).get("protected")
    ]


def md_to_html_path(md_path: Path) -> Path:
    slug = md_path.relative_to(CONTENT_DIR).with_suffix("")
    if slug.name == "index":
        return PUBLIC_DIR / slug.parent / "index.html"
    return PUBLIC_DIR / slug / "index.html"


def encrypt(key_hex: str, plaintext: str) -> str:
    key   = bytes.fromhex(key_hex)
    aesgcm = AESGCM(key)
    nonce  = secrets.token_bytes(12)
    ct     = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return (nonce + ct).hex()


def protect_html(html_path: Path, key_hex: str) -> bool:
    if not html_path.exists():
        print(f"  SKIP (HTML not found): {html_path.relative_to(QUARTZ_ROOT)}")
        return False

    html = html_path.read_text(encoding="utf-8")

    if 'data-enc="' in html:
        print(f"  SKIP (already encrypted): {html_path.relative_to(QUARTZ_ROOT)}")
        return False

    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article", class_=re.compile(r"\bpopover-hint\b"))

    if not article:
        print(f"  SKIP (no article found): {html_path.relative_to(QUARTZ_ROOT)}")
        return False

    inner_html = article.decode_contents()
    if not inner_html.strip():
        print(f"  SKIP (empty article): {html_path.relative_to(QUARTZ_ROOT)}")
        return False

    enc_hex = encrypt(key_hex, inner_html)

    article.clear()
    article["data-enc"] = enc_hex
    article["class"] = list(article.get("class", [])) + ["protected-gate"]

    html_path.write_text(str(soup), encoding="utf-8")
    print(f"  OK: {html_path.relative_to(QUARTZ_ROOT)}")
    return True


def main():
    if not AES_KEY_HEX:
        sys.exit(
            "ERROR: Set the PROTECT_KEY environment variable.\n"
            "Generate one with:  py -c \"import secrets; print(secrets.token_hex(32))\""
        )
    if len(AES_KEY_HEX) != 64:
        sys.exit("ERROR: PROTECT_KEY must be 64 hex characters (32 bytes / AES-256).")

    print("Scanning for protected pages...")
    protected = find_protected_files()

    if not protected:
        print("No protected pages found. Add `protected: true` to a page's frontmatter.")
        return

    print(f"Found {len(protected)} protected page(s):\n")
    ok = 0
    for md_path in protected:
        html_path = md_to_html_path(md_path)
        if protect_html(html_path, AES_KEY_HEX):
            ok += 1

    print(f"\nDone: {ok}/{len(protected)} pages encrypted.")


if __name__ == "__main__":
    main()
