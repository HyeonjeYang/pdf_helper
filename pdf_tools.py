#!/usr/bin/env python3
"""
pdf_tools.py - Small pypdf-based PDF editing utility.

Features:
  1. Reorder pages
  2. Delete selected pages
  3. Merge multiple PDFs

Install:
  python -m pip install pypdf

Examples:
  python pdf_tools.py reorder input.pdf output.pdf --order "3,1-2,5"
  python pdf_tools.py delete input.pdf output.pdf --pages "2,4-6"
  python pdf_tools.py merge output.pdf file1.pdf file2.pdf file3.pdf

Page numbers are 1-based. Ranges are inclusive.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from pypdf import PdfReader, PdfWriter


def parse_page_spec(spec: str, total_pages: int | None = None) -> List[int]:
    """
    Parse a 1-based page specification into 0-based page indices.

    Supports:
      "1,3,5"
      "1-4"
      "4-1"  # descending range
      "1,3-5,8"

    Args:
        spec: Page spec string.
        total_pages: If provided, validate page bounds.

    Returns:
        List of 0-based page indices, preserving the requested order.
    """
    if not spec or not spec.strip():
        raise ValueError("Page specification is empty.")

    result: List[int] = []
    parts = [part.strip() for part in spec.split(",") if part.strip()]

    for part in parts:
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str.strip())
            end = int(end_str.strip())
            step = 1 if end >= start else -1
            pages = range(start, end + step, step)
            result.extend(page - 1 for page in pages)
        else:
            result.append(int(part) - 1)

    if total_pages is not None:
        invalid = [idx + 1 for idx in result if idx < 0 or idx >= total_pages]
        if invalid:
            raise ValueError(
                f"Invalid page number(s): {invalid}. This PDF has {total_pages} page(s)."
            )

    return result


def ensure_parent_dir(path: str | Path) -> None:
    """Create output parent directory if needed."""
    output = Path(path)
    if output.parent and not output.parent.exists():
        output.parent.mkdir(parents=True, exist_ok=True)


def read_pdf(path: str | Path, password: str | None = None) -> PdfReader:
    """Read a PDF and optionally decrypt it."""
    reader = PdfReader(str(path))
    if reader.is_encrypted:
        if password is None:
            raise ValueError(f"'{path}' is encrypted. Provide --password.")
        status = reader.decrypt(password)
        if status == 0:
            raise ValueError(f"Could not decrypt '{path}'. Check the password.")
    return reader


def write_pdf(writer: PdfWriter, output_path: str | Path) -> None:
    """Write a PdfWriter to disk."""
    ensure_parent_dir(output_path)
    with open(output_path, "wb") as f:
        writer.write(f)


def copy_metadata(reader: PdfReader, writer: PdfWriter) -> None:
    """Best-effort metadata copy."""
    if reader.metadata:
        metadata = {key: str(value) for key, value in reader.metadata.items() if value is not None}
        if metadata:
            writer.add_metadata(metadata)


def reorder_pdf(
    input_path: str | Path,
    output_path: str | Path,
    order: str,
    password: str | None = None,
) -> None:
    """
    Create a new PDF whose pages follow the requested order.

    Example order: "3,1-2,5".
    """
    reader = read_pdf(input_path, password=password)
    writer = PdfWriter()
    page_indices = parse_page_spec(order, total_pages=len(reader.pages))

    for idx in page_indices:
        writer.add_page(reader.pages[idx])

    copy_metadata(reader, writer)
    write_pdf(writer, output_path)


def delete_pages_pdf(
    input_path: str | Path,
    output_path: str | Path,
    pages_to_delete: str,
    password: str | None = None,
) -> None:
    """
    Create a new PDF with selected pages removed.

    Example pages_to_delete: "2,4-6".
    """
    reader = read_pdf(input_path, password=password)
    writer = PdfWriter()
    delete_set = set(parse_page_spec(pages_to_delete, total_pages=len(reader.pages)))

    for idx, page in enumerate(reader.pages):
        if idx not in delete_set:
            writer.add_page(page)

    copy_metadata(reader, writer)
    write_pdf(writer, output_path)


def merge_pdfs(
    input_paths: Iterable[str | Path],
    output_path: str | Path,
    password: str | None = None,
) -> None:
    """Merge multiple PDFs in the given order."""
    writer = PdfWriter()

    for input_path in input_paths:
        reader = read_pdf(input_path, password=password)
        for page in reader.pages:
            writer.add_page(page)

    write_pdf(writer, output_path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reorder, delete pages from, or merge PDFs using pypdf."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    reorder = subparsers.add_parser("reorder", help="Reorder pages in one PDF.")
    reorder.add_argument("input", help="Input PDF path.")
    reorder.add_argument("output", help="Output PDF path.")
    reorder.add_argument(
        "--order",
        required=True,
        help='1-based page order, e.g. "3,1-2,5" or "5-1".',
    )
    reorder.add_argument("--password", help="Password for encrypted PDFs.")

    delete = subparsers.add_parser("delete", help="Delete selected pages from one PDF.")
    delete.add_argument("input", help="Input PDF path.")
    delete.add_argument("output", help="Output PDF path.")
    delete.add_argument(
        "--pages",
        required=True,
        help='1-based pages to delete, e.g. "2,4-6".',
    )
    delete.add_argument("--password", help="Password for encrypted PDFs.")

    merge = subparsers.add_parser("merge", help="Merge multiple PDFs.")
    merge.add_argument("output", help="Output PDF path.")
    merge.add_argument("inputs", nargs="+", help="Input PDFs in merge order.")
    merge.add_argument("--password", help="Password if all encrypted PDFs share one password.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "reorder":
            reorder_pdf(args.input, args.output, args.order, password=args.password)
        elif args.command == "delete":
            delete_pages_pdf(args.input, args.output, args.pages, password=args.password)
        elif args.command == "merge":
            merge_pdfs(args.inputs, args.output, password=args.password)
        else:
            parser.error(f"Unknown command: {args.command}")

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
