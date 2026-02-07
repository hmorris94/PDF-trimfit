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
python trimfit.py input.pdf [output.pdf] [--size WxH] [--margin M]
```

| Option     | Default  | Description                          |
|------------|----------|--------------------------------------|
| `--size`   | `8.5x11` | Output page size in inches (WxH)     |
| `--margin` | `0.5`    | Minimum internal margin in inches    |

## Examples

```bash
# Default: 8.5x11 with 0.5in margin
python trimfit.py input.pdf output.pdf

# Letter size with 0.5in margins
python trimfit.py input.pdf output.pdf --size 11x8.5 --margin 0.5
```
