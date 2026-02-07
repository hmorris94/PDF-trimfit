# PDF-trimfit

Auto-trim whitespace from each page of a PDF, then normalize to a uniform page size with minimum margins.

## Requirements

Python packages:
```bash
pip install pymupdf
```

Ubuntu / Debian / WSL:
```bash
sudo apt install texlive-extra-utils
```

macOS:
```bash
# Install MacTeX from https://tug.org/mactex/
```

## Usage

```bash
python trimfit.py input.pdf [output.pdf] [--size SIZE] [--landscape | --portrait] [--margin M]
```

| Option        | Default  | Description                                |
|---------------|----------|--------------------------------------------|
| `--size`      | `letter` | Page size: `WxH` in inches or paper name   |
| `--landscape` |          | Landscape orientation (paper names only)    |
| `--portrait`  |          | Portrait orientation (paper names only)     |
| `--margin`    | `0.5`   | Minimum internal margin in inches           |

## Examples

```bash
# Default: letter (8.5x11) with 0.5in margin
python trimfit.py input.pdf output.pdf

# A4 landscape
python trimfit.py input.pdf output.pdf --size a4 --landscape

# Exact dimensions
python trimfit.py input.pdf output.pdf --size 17x11 --margin 0.25
```
