#!/usr/bin/env python3
"""Build a static documentation site for GitHub Pages."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEFAULT_OUT = ROOT / "site"


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>heatmiser-neohub docs</title>
  <link rel="stylesheet" href="assets/site.css" />
</head>
<body>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="index.html">heatmiser-neohub</a>
      <nav>
        <a href="index.html">Home</a>
        <a href="api/neohub-api.html">API guide</a>
        <a href="swagger/">OpenAPI / Swagger</a>
        <a href="openapi/neohub-api.openapi.yaml">openapi.yaml</a>
      </nav>
    </div>
  </header>
  <main class="wrap prose">
    <h1>heatmiser-neohub</h1>
    <p>
      Python client library and CLI for the IMI Heatmiser NeoHub WebSocket API
      (port <code>4243</code>), plus documentation derived from the official
      NeoHub API Rev&nbsp;3.02 guide.
    </p>
    <ul>
      <li><a href="api/neohub-api.html">Full API guide</a> (markdown → HTML)</li>
      <li><a href="swagger/">Interactive OpenAPI (Swagger UI)</a></li>
      <li><a href="openapi/neohub-api.openapi.yaml">Raw OpenAPI 3.1 YAML</a></li>
      <li><a href="https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf">Official NeoHub API PDF</a></li>
    </ul>
    <h2>IMI Heatmiser links</h2>
    <ul>
      <li><a href="https://www.heatmiser.com/neohub-smart-control/">neoHub smart control</a></li>
      <li><a href="https://dev.heatmiser.com/">Developer Portal</a></li>
      <li><a href="https://dev.heatmiser.com/uploads/short-url/b2K3JopBdu4sjcRz8WC0VYdca3R.pdf">Official NeoHub API PDF</a></li>
    </ul>
    <h2>Quick start</h2>
    <pre><code>pip install -e .
export NEOHUB_HOST=192.168.0.19
export NEOHUB_TOKEN=your-token
neohub live-data</code></pre>
    <p>
      Source:
      <a href="https://github.com/hypercat-net/heatmiser-neohub">github.com/hypercat-net/heatmiser-neohub</a>
    </p>
  </main>
</body>
</html>
"""

SWAGGER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NeoHub OpenAPI — Swagger UI</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
  <link rel="stylesheet" href="../assets/site.css" />
  <style>
    body { margin: 0; background: #fafafa; }
    .top { margin-bottom: 0; }
    #swagger-ui { max-width: 1460px; margin: 0 auto; }
  </style>
</head>
<body>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="../index.html">heatmiser-neohub</a>
      <nav>
        <a href="../index.html">Home</a>
        <a href="../api/neohub-api.html">API guide</a>
        <a href="./">OpenAPI / Swagger</a>
        <a href="../openapi/neohub-api.openapi.yaml">openapi.yaml</a>
      </nav>
    </div>
  </header>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js" crossorigin></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: "../openapi/neohub-api.openapi.yaml",
        dom_id: "#swagger-ui",
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis],
        layout: "BaseLayout",
      });
    };
  </script>
</body>
</html>
"""

SITE_CSS = """
:root {
  --ink: #1a1f24;
  --muted: #5b6570;
  --bg: #f6f3ee;
  --card: #fffdf9;
  --accent: #0b6e4f;
  --line: #ddd4c6;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --sans: "IBM Plex Sans", "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--sans);
  color: var(--ink);
  background:
    radial-gradient(1200px 500px at 10% -10%, #e7f3ec 0%, transparent 55%),
    linear-gradient(180deg, #fbf8f2, var(--bg));
  line-height: 1.55;
}
.wrap { width: min(960px, calc(100% - 2rem)); margin: 0 auto; }
.top {
  border-bottom: 1px solid var(--line);
  background: rgba(255,253,249,0.92);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 10;
}
.top .wrap {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  min-height: 3.25rem;
}
.brand {
  font-weight: 700;
  color: var(--ink);
  text-decoration: none;
  letter-spacing: -0.02em;
}
nav { display: flex; flex-wrap: wrap; gap: 0.85rem; }
nav a {
  color: var(--muted);
  text-decoration: none;
  font-size: 0.95rem;
}
nav a:hover { color: var(--accent); }
.prose { padding: 2rem 0 4rem; }
.prose h1, .prose h2, .prose h3 { line-height: 1.2; letter-spacing: -0.02em; }
.prose a { color: var(--accent); }
.prose code, .prose pre {
  font-family: var(--mono);
  font-size: 0.9em;
}
.prose pre {
  background: #182028;
  color: #e8eef4;
  padding: 1rem 1.1rem;
  overflow: auto;
  border-radius: 10px;
}
.prose table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.92rem;
}
.prose th, .prose td {
  border: 1px solid var(--line);
  padding: 0.45rem 0.6rem;
  vertical-align: top;
}
.prose th { background: #efe8dc; text-align: left; }
.prose blockquote {
  border-left: 3px solid var(--accent);
  margin-left: 0;
  padding-left: 1rem;
  color: var(--muted);
}
"""

API_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NeoHub API Rev 3.02</title>
  <link rel="stylesheet" href="../assets/site.css" />
</head>
<body>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="../index.html">heatmiser-neohub</a>
      <nav>
        <a href="../index.html">Home</a>
        <a href="neohub-api.html">API guide</a>
        <a href="../swagger/">OpenAPI / Swagger</a>
        <a href="../openapi/neohub-api.openapi.yaml">openapi.yaml</a>
      </nav>
    </div>
  </header>
  <main class="wrap prose">
{body}
  </main>
</body>
</html>
"""


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    (out / "assets").mkdir()
    (out / "assets" / "site.css").write_text(SITE_CSS, encoding="utf-8")
    (out / "index.html").write_text(INDEX_HTML, encoding="utf-8")

    swagger_dir = out / "swagger"
    swagger_dir.mkdir()
    (swagger_dir / "index.html").write_text(SWAGGER_HTML, encoding="utf-8")

    openapi_src = DOCS / "openapi"
    if not (openapi_src / "neohub-api.openapi.yaml").exists():
        raise SystemExit(
            "Missing docs/openapi/neohub-api.openapi.yaml — run scripts/generate_openapi.py first"
        )
    shutil.copytree(openapi_src, out / "openapi")

    md_path = DOCS / "neohub-api-rev-3.02.md"
    html_body = markdown.markdown(
        md_path.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "toc"],
    )
    api_dir = out / "api"
    api_dir.mkdir()
    (api_dir / "neohub-api.html").write_text(
        API_PAGE.format(body=html_body), encoding="utf-8"
    )

    print(f"Built site → {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output directory (default: ./site)",
    )
    args = parser.parse_args()
    build(args.out.resolve())


if __name__ == "__main__":
    main()
