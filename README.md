# PDF Editing Tools

Simple Python tools for basic PDF page editing using [`pypdf`](https://pypdf.readthedocs.io/).

This project includes two versions:

- `pdf_editing_tools.ipynb`: Jupyter Notebook version
- `pdf_tools.py`: Command-line version for terminal use

## Features

1. Reorder pages in a PDF
2. Delete selected pages from a PDF
3. Merge multiple PDF files into one PDF

All page numbers are **1-based**, meaning the first page is page `1`, not page `0`.

## Installation

Install the required package:

```bash
python -m pip install pypdf
```

## Command-Line Usage

### 1. Reorder pages

```bash
python pdf_tools.py reorder input.pdf output.pdf --order "3,1-2,5"
```

This creates `output.pdf` with pages ordered as:

```text
3, 1, 2, 5
```

You can use both individual page numbers and page ranges.

Examples:

```bash
python pdf_tools.py reorder input.pdf reordered.pdf --order "1,3,2"
python pdf_tools.py reorder input.pdf reordered.pdf --order "5-1"
```

### 2. Delete pages

```bash
python pdf_tools.py delete input.pdf output.pdf --pages "2,4-6"
```

This removes pages 2, 4, 5, and 6 from `input.pdf` and saves the result as `output.pdf`.

Examples:

```bash
python pdf_tools.py delete input.pdf clean.pdf --pages "1"
python pdf_tools.py delete input.pdf clean.pdf --pages "2,5,8-10"
```

### 3. Merge PDF files

```bash
python pdf_tools.py merge merged.pdf file1.pdf file2.pdf file3.pdf
```

This combines `file1.pdf`, `file2.pdf`, and `file3.pdf` into `merged.pdf`.

## Jupyter Notebook Usage

Open `pdf_editing_tools.ipynb` in Jupyter Notebook or JupyterLab.

The notebook contains ready-to-use functions for:

- Reordering pages
- Deleting pages
- Merging PDFs

Example:

```python
reorder_pdf("input.pdf", "output.pdf", "3,1-2,5")
delete_pages("input.pdf", "clean.pdf", "2,4-6")
merge_pdfs(["file1.pdf", "file2.pdf"], "merged.pdf")
```

## Page Range Syntax

You can write page selections like this:

```text
1
1,3,5
1-4
4-1
1,3-5,8
```

Examples:

- `1,3,5` means pages 1, 3, and 5
- `1-4` means pages 1 through 4
- `4-1` means pages 4, 3, 2, and 1
- `1,3-5,8` means pages 1, 3, 4, 5, and 8

## Notes

These tools are designed for **page-level PDF editing**. They do not edit the text or images inside a PDF page.

For important documents, it is recommended to keep a backup of the original PDF before editing.
