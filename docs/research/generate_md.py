#!/usr/bin/env python3

import json
from pathlib import Path
import html
import sys


INPUT_FILE = Path("docs/research/research.json")
OUTPUT_FILE = Path("docs/research/research-table.md")


def bullet_list(items):
    if not items:
        return ""

    lines = []

    for item in items:
        if isinstance(item, str):
            lines.append(f"- {item}")
        elif isinstance(item, dict):
            name = item.get("name") or item.get("capability_name") or item.get("display_name") or ""
            desc = item.get("description") or item.get("notes") or ""
            vendor = item.get("vendor", "")

            label = name
            if vendor:
                label = f"{name} ({vendor})"

            if desc:
                lines.append(f"- **{label}**: {desc}")
            else:
                lines.append(f"- **{label}**")
        else:
            lines.append(f"- {str(item)}")

    return "<br>".join(lines)


def escape_cell(value):
    if value is None:
        return ""
    return html.escape(str(value)).replace("\n", "<br>")


def main():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    products = data.get("products", [])

    lines = [
        "# AI Research Catalog",
        "",
        "| Product | Display Name | Domain | Description | Reference Implementations | Capabilities | Tags |",
        "|---|---|---|---|---|---|---|"
    ]

    for product in products:
        product_name = escape_cell(product.get("product_name", ""))
        display_name = escape_cell(product.get("display_name", ""))
        domain = escape_cell(product.get("domain", ""))
        description = escape_cell(product.get("description", ""))
        refs = bullet_list(product.get("reference_implementations", []))
        capabilities = bullet_list(product.get("capabilities", []))
        tags = ", ".join(product.get("tags", []))

        lines.append(
            f"| {product_name} | {display_name} | {domain} | {description} | {refs} | {capabilities} | {escape_cell(tags)} |"
        )

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()