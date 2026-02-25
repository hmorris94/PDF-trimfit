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
python trimfit.py input.pdf [output.pdf] [--trim | --fit] [--size SIZE] [--landscape | --portrait] [--margin M]
```

| Option        | Default     | Description                                |
|---------------|-------------|--------------------------------------------|
| `--trim`      |             | Trim whitespace only, skip fit             |
| `--fit`       |             | Fit to page only, skip trim                |
| `--size`      | `letter`    | Page size: `WxH` in inches or paper name   |
| `--landscape` |             | Landscape orientation (paper names only)   |
| `--portrait`  |             | Portrait orientation (paper names only)    |
| `--margin`    | `0.5`       | Minimum internal margin in inches          |

## Examples

```bash
# Default: trim and fit to letter (8.5x11) with 0.5in margin
python trimfit.py input.pdf output.pdf

# Trim only (no page normalization)
python trimfit.py input.pdf output.pdf --trim

# Fit to A4 landscape without trimming
python trimfit.py input.pdf output.pdf --fit --size a4 --landscape

# Exact dimensions
python trimfit.py input.pdf output.pdf --size 17x11 --margin 0.25
```
