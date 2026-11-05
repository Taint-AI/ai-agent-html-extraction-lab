# AI-agent HTML extraction boundary lab

A contained parser experiment using synthetic HTML. **No model or browser runs.** Retaining source changes audit evidence, not the text a model receives. The experiment does not execute page content, send requests, implement an injection defense or measure browser visibility.

## Hypothesis and result

Hypothesis: an HTML text extractor can turn different source placements into the same text, leaving a text-only audit unable to explain where that text came from.

BeautifulSoup4.14.3 with Python's `html.parser` produced the same literal `Product: notebook. NOTE-MARKER` from an ordinary `<div>` and a `<div hidden>`. Keeping the original HTML beside the extracted text preserved that difference. Both methods retain exactly the same extracted text; neither changes an agent's behavior.

Fourteen selected synthetic fixtures matched their predeclared expected strings. Eight included the inert marker in extracted text; five other marker-bearing fixtures (comment, meta attribute, script, style and template) did not. The fourteenth fixture contains no marker. These are fixture counts, not attack rates or claims about all pages.

## Setup and exact commands

Tested with Python3.11.6. Use a clean virtual environment with the pinned dependencies:

```sh
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -B -m unittest -v
.venv/bin/python -B experiment.py
```

Dependency installation requires normal package access. The experiment and tests then run offline without credentials. The run checks all three package versions before emitting results. Python parser versions may behave differently on other inputs; this repository does not claim invariance across Python versions. Run from this repository root. The script writes only `artifacts/run.json` and `evidence.md` beside itself.

## Threat model and containment

A webpage author can choose source HTML before a trusted extractor reads it. That is the security-relevant boundary being inspected. Our fixtures supply a harmless marker in selected locations; they do not instruct an agent to act. No attack persuasion, harmful action, private page, real endpoint, authentication session, browser rendering, CSS evaluation or JavaScript execution occurs.

The parser, fixture loader and capture writer are trusted. The source HTML remains untrusted even after capture. The SHA256 binds the stored bytes for comparison; it is not authenticated authorship, a signature or proof that a page is safe. Capturing source may retain material excluded by text extraction, so it is not a recommendation to send more source text to a model. Synthetic fixtures avoid the privacy issues of storing real page content.

## Technical walkthrough

The actual library call is:

```python
BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
```

Two capture formats receive its identical result:

- **Text-only capture:** store the extracted text alone.
- **Source-linked capture:** store that same text with the exact original HTML and its UTF-8 SHA256.

The source is retained before parsing, not reconstructed with `str(soup)` or `prettify`. Reserialization could change attributes, entities or formatting and would not preserve original bytes.

The principal pair differs only by the `hidden` attribute:

```html
<div>NOTE-MARKER</div>
<div hidden>NOTE-MARKER</div>
```

Both produce `NOTE-MARKER` after the ordinary product paragraph. The text-only payloads are equal. The source-linked records differ in both the actual source and its digest. The digest alone does not explain why; the HTML fragment supplies the inspectable difference.

[Full exact trace and scenario table](evidence.md). [Machine-readable captures](artifacts/run.json). [All synthetic inputs and predeclared text expectations](fixtures.json).

Source placement is not a single inclusion category. In these fixtures, element text under a hidden attribute, an ancestor's hidden attribute, inline display styling and a CSS class survives the chosen extraction call. A comment, meta attribute, script, style and template does not contribute the marker. The entity case is decoded in extracted text while its original spelling survives in the source capture. An `aria-hidden` attribute is not treated as a visual-hiding test. We observed source bytes and parser output, not pixels or accessibility-tree behavior.

## Validation

Twelve focused tests cover the exact twin collision, original-source identity and hashes, identical text across capture formats, placement families, entity preservation, benign text, duplicate/invalid fixture records, dependency mismatch, expectation mismatch, deterministic outputs and blocked network constructors. All passed on Python3.11.6 with the three pinned packages. A fresh copy reproduced the exact JSON and evidence bytes with those same installed dependency bytes.

Two deliberately broken implementations were checked separately: replacing retained source with extracted text, and removing hidden-marked elements before the baseline extraction. The suite rejected both. These are functional regression checks, not proof of universal correctness. The first checks the audit intervention; the second checks that the baseline remains the actual documented parser call instead of quietly becoming a filter.

## Source rationale

[Indirect Prompt Injection in the Wild, v2](https://arxiv.org/html/2604.27202v2), section8, compares webpage representations for a summarization task. It motivates inspecting preprocessing; this lab does not reproduce its corpus, extractor implementation, model responses or reported attack rates. The paper does not establish that retaining markup universally prevents injection. No novelty claim depends on what changed between its versions.

[BeautifulSoup documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#get-text) describes text extraction. This experiment pins and runs4.14.3; the live documentation can describe a newer release. The repository contains independently authored code and synthetic fixtures, not copied paper pages, third-party source, benchmark payloads or social content.

## Limits and engineering check

The principal witness proves an information-loss distinction in this specific parser call. It does not establish actual screen visibility, end-to-end agent compromise, model instruction following, safe extraction, protection from visible instructions, a prevalence estimate or a complete CSS/HTML security policy. An unchanged useful sentence does not prove general task utility. Fixed selected cases are not randomly sampled observations.

When auditing an AI agent's webpage preprocessing, compare the exact extracted input with a suitably protected source capture taken before extraction. Include ordinary-element, hidden-attribute, comment and metadata fixtures so the audit distinguishes what survives from what is omitted. Review any capture retention policy separately before using real content; keeping markup is evidence preservation, not a trust decision or a prompt-injection defense.
