<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- SPDX-FileCopyrightText: Netresearch DTT GmbH -->

# rga (ripgrep-all) Guide

Extends ripgrep to search inside PDFs, Word/Excel/PowerPoint, SQLite databases,
compressed archives, and more.

---

## When to Use rga Instead of rg

- Searching PDF documents for text
- Searching Word (.docx), Excel (.xlsx), PowerPoint (.pptx) files
- Searching inside .zip, .tar.gz, .tar.bz2 archives
- Searching SQLite database contents
- Searching EPUB ebooks

---

## Supported Formats

| Format | Extension |
|--------|-----------|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| PowerPoint | `.pptx`, `.ppt` |
| OpenDocument | `.odt`, `.ods`, `.odp` |
| Archive | `.zip`, `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz` |
| SQLite | `.db`, `.sqlite`, `.sqlite3` |
| EPUB | `.epub` |

---

## Usage

```bash
# Search PDFs for a term
rga 'quarterly revenue' docs/

# Search all document types
rga 'confidential' --rga-adapters=+pdfpages,poppler /path/to/docs/

# Search inside archives
rga 'config' backups/*.tar.gz

# Search with ripgrep flags (most rg flags work)
rga -i -c 'error' logs/

# List matching files only
rga -l 'password' /shared/docs/
```

---

## Dependencies

rga requires adapters to process different file types:

- **PDF**: `poppler` (pdftotext) — usually pre-installed on Linux
- **Office (.docx, .xlsx, .pptx)**: built-in via `zip` + XML parsing
- **Legacy Office (.doc, .xls)**: requires `libreoffice` or `catdoc`
- **Archives**: requires standard tools (`tar`, `unzip`, etc.)

Install adapters: `sudo apt install poppler-utils` (Debian/Ubuntu) or
`brew install poppler` (macOS).

Without poppler and without root, read a single PDF through `pypdf` in a
throwaway environment:

```bash
uv run -q --with pypdf python3 -c "import sys, pypdf; print('\n'.join(p.extract_text() for p in pypdf.PdfReader(sys.argv[1]).pages))" file.pdf
```

---

## Cache Behavior

rga caches extracted text for faster subsequent searches. The cache is stored
in the system cache directory. Use `--rga-no-cache` to disable.
