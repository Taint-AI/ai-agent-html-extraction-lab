"""A contained HTML extraction assay. No model, browser, network or actions."""
import hashlib
import importlib.metadata
import json
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
MARKER = "NOTE-MARKER"
VERSIONS = {"beautifulsoup4": "4.14.3", "soupsieve": "2.2.1", "typing_extensions": "4.16.0"}


def verify_versions():
    actual = {name: importlib.metadata.version(name) for name in VERSIONS}
    if actual != VERSIONS:
        raise RuntimeError(f"Dependency versions differ: {actual}; expected {VERSIONS}")
    return actual


def load_fixtures(path=ROOT / "fixtures.json"):
    fixtures = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("Expected a nonempty list of fixtures")
    seen = set()
    for row in fixtures:
        if not isinstance(row, dict) or set(row) != {"id", "placement", "html", "expected_text"}:
            raise ValueError("Invalid fixture fields")
        if any(not isinstance(row[k], str) or not row[k] for k in row):
            raise ValueError("Fixture fields must be nonempty strings")
        if row["id"] in seen:
            raise ValueError("Duplicate fixture ID")
        seen.add(row["id"])
    return fixtures


def extract_text(html):
    return BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)


def capture(html):
    text = extract_text(html)
    return {
        "text_only": {"text": text},
        "source_linked": {
            "text": text,
            "source_html": html,
            "source_sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        },
    }


def run(fixtures=None):
    versions = verify_versions()
    fixtures = load_fixtures() if fixtures is None else fixtures
    rows = []
    for fixture in fixtures:
        captures = capture(fixture["html"])
        text = captures["text_only"]["text"]
        if text != fixture["expected_text"]:
            raise AssertionError(f"Unexpected extraction for {fixture['id']}: {text!r}")
        rows.append({
            "id": fixture["id"], "placement": fixture["placement"],
            "captures": captures, "marker_in_extracted_text": MARKER in text,
        })
    by_id = {row["id"]: row for row in rows}
    ordinary = by_id["ordinary"]["captures"]
    hidden = by_id["hidden_attribute"]["captures"]
    return {
        "schema_version": 1,
        "scope": "Synthetic HTML; no browser, model, network or attack. Source capture is audit evidence only.",
        "parser": "Python html.parser", "dependencies": versions,
        "method": "BeautifulSoup(html, 'html.parser').get_text(separator=' ', strip=True)",
        "fixture_count": len(rows), "rows": rows,
        "principal_pair": {
            "ids": ["ordinary", "hidden_attribute"],
            "text_only_equal": ordinary["text_only"] == hidden["text_only"],
            "source_html_equal": ordinary["source_linked"]["source_html"] == hidden["source_linked"]["source_html"],
            "source_hash_equal": ordinary["source_linked"]["source_sha256"] == hidden["source_linked"]["source_sha256"],
        },
    }


def evidence(result):
    lines = [
        "# Exact extraction evidence", "",
        "Synthetic fixtures only. No browser visibility or model behavior was measured.",
        "The source-linked capture retains the same extracted text plus exact original HTML and its SHA256.",
        "It changes audit evidence, not model input or permissions.", "",
        "|Fixture|Source placement|Marker in extracted text|", "|---|---|---|",
    ]
    for row in result["rows"]:
        lines.append(f"|{row['id']}|{row['placement']}|{'yes' if row['marker_in_extracted_text'] else 'no'}|")
    lines += ["", "Each row is one selected fixture, not a prevalence sample or an attack-success trial.",
              "", "## Exact paired trace", ""]
    for row in result["rows"][:2]:
        captures = row["captures"]
        lines += [f"### {row['id']}", "", "Original source:", "```html",
                  captures["source_linked"]["source_html"], "```", "Text-only capture:",
                  "```json", json.dumps(captures["text_only"], ensure_ascii=False), "```",
                  "Source SHA256: `" + captures["source_linked"]["source_sha256"] + "`", ""]
    lines += ["The text-only captures are identical. The source-linked captures preserve the differing hidden attribute.",
              "The digest alone does not explain that difference; inspect the actual source beside it.", "",
              "Comments, metadata attributes, scripts, styles and template text are excluded in these specific fixtures.",
              "Text under hidden attributes, inline styling and a CSS class is retained by this parser call.",
              "The entity case decodes a character; aria-hidden is recorded as source markup, not treated as visual hiding.",
              "The ordinary text remains present in every case. Source retention is not sanitization or a defense."]
    return "\n".join(lines) + "\n"


def main():
    result = run()
    (ROOT / "artifacts").mkdir(exist_ok=True)
    (ROOT / "artifacts/run.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "evidence.md").write_text(evidence(result), encoding="utf-8")
    print(json.dumps({"fixtures": result["fixture_count"], "principal_pair": result["principal_pair"]}))


if __name__ == "__main__":
    main()
