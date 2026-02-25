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

## Cache Behavior

rga caches extracted text for faster subsequent searches. The cache is stored
in the system cache directory. Use `--rga-no-cache` to disable.
