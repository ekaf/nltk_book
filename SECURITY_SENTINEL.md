# NLTK Security Sentinel — Developer & Maintainer Guide

## Background

Starting with NLTK 3.10, all file and network access in NLTK goes through a
central security sentinel (`nltk.pathsec`). This was introduced in
[nltk/nltk#3522](https://github.com/nltk/nltk/pull/3522) to prevent
path traversal, SSRF, and zip-slip attacks.

## What This Means for `nltk_book`

When `nltk.pathsec.ENFORCE = True` (the default in NLTK >= 3.10):

- **File access** via `open()` is restricted to:
  - The current working directory (CWD) and its subdirectories
  - Paths listed in `nltk.data.path`
- **Network access** via `urllib.request.urlopen` and similar is subject to
  host-allowlist enforcement.

Scripts or examples that open arbitrary absolute paths or access arbitrary URLs
will raise a `SecurityError` in strict mode.

## Configuring Your Environment for Local Builds

If you need to access files outside CWD during a local build or test run,
add the required path to `nltk.data.path` before running:

```python
import nltk
nltk.data.path.append('/path/to/your/data')
```

## Testing Compatibility

To verify that `nltk_book` examples are compatible with the sentinel, run:

```python
import nltk
nltk.pathsec.ENFORCE = True
# then run your examples / doctests
```

Any failures indicate code that needs to be updated to use authorized paths.

## References

- [NLTK PR #3522](https://github.com/nltk/nltk/pull/3522) — Security sentinel implementation
- [nltk_book Issue #269](https://github.com/nltk/nltk_book/issues/269) — Audit tracking issue
