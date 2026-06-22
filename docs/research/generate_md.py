#!/usr/bin/env python3

import json
from pathlib import Path
import html
import sys


PRODUCTS_DIR = Path("docs/research/products")
OUTPUT_FILE  = Path("docs/research/research-table.md")


def bullet_list(items):
    if not items:
        return ""

    lines = []

    for item in items:
        if isinstance(item, str):
            lines.append(f"- {item}")
        elif isinstance(item, dict):
            name   = item.get("name") or item.get("capability_name") or item.get("display_name") or ""
            desc   = item.get("description") or item.get("notes") or ""
            vendor = item.get("vendor", "")
            url    = item.get("url", "")

            label  = f"{name} ({vendor})" if vendor else name
            linked = f"[{label}]({url})" if url else label

            if desc:
                lines.append(f"- **{linked}**: {desc}")
            else:
                lines.append(f"- **{linked}**")
        else:
            lines.append(f"- {str(item)}")

    return "<br>".join(lines)


def escape_cell(value):
    if value is None:
        return ""
    return html.escape(str(value)).replace("\n", "<br>")


def main():
    if not PRODUCTS_DIR.exists():
        print(f"Products directory not found: {PRODUCTS_DIR}", file=sys.stderr)
        sys.exit(1)

    product_files = sorted(
        f for f in PRODUCTS_DIR.rglob("*.json") if f.name != "_meta.json"
    )

    if not product_files:
        print("No product files found.", file=sys.stderr)
        sys.exit(1)

    products = [json.loads(f.read_text(encoding="utf-8")) for f in product_files]

    lines = [
        "# AI Research Catalog",
        "",
        "| Product | Display Name | Domain | Description | Reference Implementations | Capabilities | Tags |",
        "|---|---|---|---|---|---|---|",
    ]

    for product in products:
        product_name = escape_cell(product.get("product_name", ""))
        display_name = escape_cell(product.get("display_name", ""))
        domain       = escape_cell(product.get("domain", ""))
        description  = escape_cell(product.get("description", ""))
        refs         = bullet_list(product.get("reference_implementations", []))
        capabilities = bullet_list(product.get("capabilities", []))
        tags         = ", ".join(product.get("tags", []))

        lines.append(
            f"| {product_name} | {display_name} | {domain} | {description} | {refs} | {capabilities} | {escape_cell(tags)} |"
        )

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE} ({len(products)} products)")


if __name__ == "__main__":
    main()
