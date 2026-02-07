#!/usr/bin/env python3

"""
trimfit.py

Auto-trim whitespace per page and normalize output to a specified size with a minimum internal margin.

Pipeline (per page):
  1) pymupdf: crop to visible content (ignoring white fills)
  2) pdfjam --papersize inner -> scaled-to-inner
  3) pdfjam --papersize outer --noautoscale true -> padded-to-outer
  4) pymupdf: merge all pages

Defaults:
  --size 8.5x11 (letter portrait)
  --margin 0.5
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

import fitz  # pymupdf


DEFAULT_WIDTH = 8.5
DEFAULT_HEIGHT = 11.0
DEFAULT_MARGIN = 0.5


def _parse_size(value: str) -> Tuple[float, float]:
    """Parse 'WIDTHxHEIGHT' string into (width, height) tuple."""
    try:
        w, h = value.lower().split("x")
        return float(w), float(h)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid size '{value}'. Expected format: WIDTHxHEIGHT (e.g., '8.5x11')")


def _visible_rect(page: fitz.Page) -> fitz.Rect:
    """Bounding rect of visible (non-white) drawings and all text on a page."""
    rects: list[fitz.Rect] = []

    for d in page.get_drawings():
        color = d.get("color")
        fill = d.get("fill")
        has_visible_stroke = color is not None and not all(c > 0.95 for c in color)
        has_visible_fill = fill is not None and not all(c > 0.95 for c in fill)
        if has_visible_stroke or has_visible_fill:
            rects.append(d["rect"])

    for block in page.get_text("dict")["blocks"]:
        rects.append(fitz.Rect(block["bbox"]))

    if not rects:
        return page.mediabox

    result = rects[0]
    for r in rects[1:]:
        result |= r

    # Pad by 1pt to avoid clipping thin border strokes
    result.x0 -= 1
    result.y0 -= 1
    result.x1 += 1
    result.y1 += 1

    return result & page.mediabox


def _crop_to_content(input_pdf: Path, output_pdf: Path) -> None:
    """Crop each page to visible content, ignoring white backgrounds."""
    doc = fitz.open(str(input_pdf))
    for page in doc:
        page.set_cropbox(_visible_rect(page))
    doc.save(str(output_pdf))
    doc.close()


def _which_or_die(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        raise FileNotFoundError(
            f"Required tool not found on PATH: {cmd}\n\n"
            f"On Ubuntu/WSL you can install dependencies with:\n"
            f"  sudo apt update && sudo apt install -y texlive-extra-utils\n"
        )
    return path


def _run(args: List[str]) -> None:
    try:
        subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or b"").decode("utf-8", errors="replace")
        stdout = (e.stdout or b"").decode("utf-8", errors="replace")
        msg = "Command failed:\n  " + " ".join(args) + "\n\n"
        if stdout.strip():
            msg += "STDOUT:\n" + stdout + "\n"
        if stderr.strip():
            msg += "STDERR:\n" + stderr + "\n"
        raise RuntimeError(msg) from e


def normalize_pdf(
    input_pdf: Path,
    output_pdf: Path,
    width: float = DEFAULT_WIDTH,
    height: float = DEFAULT_HEIGHT,
    margin: float = DEFAULT_MARGIN,
) -> None:
    _which_or_die("pdfjam")

    input_pdf = input_pdf.resolve()
    output_pdf = output_pdf.resolve()

    if not input_pdf.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")
    if input_pdf.suffix.lower() != ".pdf":
        raise ValueError(f"Input must be a .pdf file: {input_pdf}")

    inner_w = width - 2 * margin
    inner_h = height - 2 * margin

    if inner_w <= 0 or inner_h <= 0:
        raise ValueError(f"Margin {margin} is too large for size {width}x{height}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    inner = f"{{{inner_w}in,{inner_h}in}}"
    outer = f"{{{width}in,{height}in}}"

    with tempfile.TemporaryDirectory(prefix="pdf-trimfit-") as td:
        td_path = Path(td)

        # 1) Crop to visible content per page (ignores white fills)
        cropped = td_path / "cropped.pdf"
        _crop_to_content(input_pdf, cropped)

        # 2-3) Scale and pad each page individually, then merge
        src = fitz.open(str(cropped))
        result = fitz.open()

        for i in range(len(src)):
            page_in = td_path / f"p{i}.pdf"
            page_fit = td_path / f"p{i}_fit.pdf"
            page_pad = td_path / f"p{i}_pad.pdf"

            # Extract single page
            single = fitz.open()
            single.insert_pdf(src, from_page=i, to_page=i)
            single.save(str(page_in))
            single.close()

            # Scale to fit inner canvas (per-page)
            _run([
                "pdfjam", "--quiet",
                "--papersize", inner,
                str(page_in), "--outfile", str(page_fit),
            ])

            # Pad to outer page size (enforces minimum margin)
            _run([
                "pdfjam", "--quiet",
                "--papersize", outer,
                "--noautoscale", "true",
                str(page_fit), "--outfile", str(page_pad),
            ])

            # Append to result
            page_doc = fitz.open(str(page_pad))
            result.insert_pdf(page_doc)
            page_doc.close()

        src.close()
        result.save(str(output_pdf))
        result.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Auto-trim whitespace and normalize PDF to specified size with minimum margins."
    )
    parser.add_argument("input_pdf", help="Input PDF file")
    parser.add_argument("output_pdf", nargs="?", default="output.pdf", help='Output PDF file (default: "output.pdf")')
    parser.add_argument(
        "--size",
        type=_parse_size,
        default=(DEFAULT_WIDTH, DEFAULT_HEIGHT),
        metavar="WxH",
        help=f"Output page size as WIDTHxHEIGHT in inches (default: {DEFAULT_WIDTH:.0f}x{DEFAULT_HEIGHT:.0f})"
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=DEFAULT_MARGIN,
        help=f"Minimum internal margin in inches (default: {DEFAULT_MARGIN})"
    )
    args = parser.parse_args()
    width, height = args.size

    try:
        normalize_pdf(Path(args.input_pdf), Path(args.output_pdf), width, height, args.margin)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
