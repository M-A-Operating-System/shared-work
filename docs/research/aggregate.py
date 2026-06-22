#!/usr/bin/env python3
"""
Aggregates docs/research/products/*.json into docs/research/research.json.
Run after editing any product file to rebuild the catalog.
"""

import json
import sys
from pathlib import Path

PRODUCTS_DIR = Path("docs/research/products")
META_FILE    = PRODUCTS_DIR / "_meta.json"
OUTPUT_FILE  = Path("docs/research/research.json")
SCHEMA_FILE  = Path("docs/research/research.schema.json")


def main() -> None:
    if not PRODUCTS_DIR.exists():
        print(f"Products directory not found: {PRODUCTS_DIR}", file=sys.stderr)
        sys.exit(1)

    meta = json.loads(META_FILE.read_text(encoding="utf-8")) if META_FILE.exists() else {
        "research_version": "1.0",
        "research_name": "regulated_agentic_ai_research_catalog",
        "description": (
            "Function-first research catalog of enterprise AI products/functions, capabilities, "
            "and reference implementations for MCP-enabled conversational and agentic AI "
            "ecosystems in regulated data industries."
        ),
    }

    # Walk domain subfolders: products/<domain>/<product_name>.json
    product_files = sorted(
        f for f in PRODUCTS_DIR.rglob("*.json") if f.name != "_meta.json"
    )

    products = []
    for f in product_files:
        products.append(json.loads(f.read_text(encoding="utf-8")))

    catalog = {**meta, "products": products}

    # Optional schema validation
    if SCHEMA_FILE.exists():
        try:
            import jsonschema
            schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
            jsonschema.validate(catalog, schema)
        except ImportError:
            pass
        except jsonschema.ValidationError as e:
            print(f"Schema validation failed: {e.message}", file=sys.stderr)
            sys.exit(1)

    OUTPUT_FILE.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"Aggregated {len(products)} products → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
