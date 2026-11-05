# Exact extraction evidence

Synthetic fixtures only. No browser visibility or model behavior was measured.
The source-linked capture retains the same extracted text plus exact original HTML and its SHA256.
It changes audit evidence, not model input or permissions.

|Fixture|Source placement|Marker in extracted text|
|---|---|---|
|ordinary|Ordinary div|yes|
|hidden_attribute|hidden attribute|yes|
|nested_hidden|hidden ancestor|yes|
|inline_display_none|inline display:none|yes|
|css_class|class with display:none rule|yes|
|comment|HTML comment|no|
|meta|meta content attribute|no|
|script|script data|no|
|style|style text|no|
|template|template text|no|
|entity|numeric character reference|yes|
|aria_hidden|aria-hidden attribute, not visual hiding|yes|
|hidden_false|literal hidden="false" attribute|yes|
|benign_no_marker|ordinary document without marker|no|

Each row is one selected fixture, not a prevalence sample or an attack-success trial.

## Exact paired trace

### ordinary

Original source:
```html
<!doctype html><html><head></head><body><p>Product: notebook.</p><div>NOTE-MARKER</div></body></html>
```
Text-only capture:
```json
{"text": "Product: notebook. NOTE-MARKER"}
```
Source SHA256: `effa770bae9248a9a56f76d85626715f5950f873c8f43301e07130ed7372095b`

### hidden_attribute

Original source:
```html
<!doctype html><html><head></head><body><p>Product: notebook.</p><div hidden>NOTE-MARKER</div></body></html>
```
Text-only capture:
```json
{"text": "Product: notebook. NOTE-MARKER"}
```
Source SHA256: `9940fdf8700ddbd88ff55e3526243ad4f468deb7e1e40d1db82dd5544a32abe6`

The text-only captures are identical. The source-linked captures preserve the differing hidden attribute.
The digest alone does not explain that difference; inspect the actual source beside it.

Comments, metadata attributes, scripts, styles and template text are excluded in these specific fixtures.
Text under hidden attributes, inline styling and a CSS class is retained by this parser call.
The entity case decodes a character; aria-hidden is recorded as source markup, not treated as visual hiding.
The ordinary text remains present in every case. Source retention is not sanitization or a defense.
