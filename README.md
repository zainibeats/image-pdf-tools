# Image PDF Tools

> **Note**: This project contains AI-generated code

Small Python tools for preparing image-based PDF attachments. Each script can be
used on its own, but they also work well together for weekly receipt workflows:
collect receipt images, turn them into one grid image, then attach that image to
the end of an expense report in PDF format.

Original images and PDFs are always preserved.

## Tools

- `scripts/make-image-grid.py`: combines HEIC, HEIF, JPG, JPEG, and PNG images into one
  balanced JPG grid. Default image limit is 24.
- `scripts/append-image-page.py`: appends a JPG/JPEG image as a US Letter page at the
  end of an existing PDF. Default input PDF limits are 10 pages, 25 MiB, and a
  15-second PDF parsing/rewrite timeout.

## Repository Layout

- `scripts/`: command line tools.
- `tests/`: unit tests.
- `docs/`: supporting project notes and findings.
- `run-image-pdf-tools.sh` and `run-image-pdf-tools.bat`: guided launchers.

## Dependencies

- Python 3.10+
- `Pillow`
- `pillow-heif`
- `pypdf[crypto]`

## Install

Install dependencies in a standard Python virtual environment.

For a guided setup and menu, Windows users can run `run-image-pdf-tools.bat`.
macOS and Linux users can run:

```bash
chmod +x run-image-pdf-tools.sh
./run-image-pdf-tools.sh
```

**Windows PowerShell:**

```powershell
cd path\to\image-pdf-tools
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

_If Windows blocks the `Activate.ps1` step, enable running local PowerShell
scripts first. Open Windows Settings, search for `PowerShell`, and turn on the
developer setting that allows local PowerShell scripts to run without signing.
Then close and reopen PowerShell and run the commands above again._

**macOS / Linux:**

```bash
cd /path/to/image-pdf-tools
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Basic Workflow

Create a grid from a folder of images:

```bash
python scripts/make-image-grid.py ~/Pictures/images
```

This writes `image-grid.jpg` inside the input folder by default.

Append that image to an existing PDF:

```bash
python scripts/append-image-page.py ~/Pictures/images/image-grid.jpg --pdf ~/Downloads/input.pdf
```

This writes a PDF next to the image by default:

```text
~/Pictures/images/image-grid.pdf
```

## Examples

**Image Grid:**

```bash
# Choosing the grid output name and path
python scripts/make-image-grid.py ~/Pictures/images -o named-image-grid.jpg

# Raise the batch limit for a larger image set:
python scripts/make-image-grid.py ~/Pictures/images --max-images 60

# Raise the output pixel limit for larger cells or batches:
python scripts/make-image-grid.py ~/Pictures/images --max-output-pixels 100000000
```

**Append Image to PDF:**

```bash
# Choosing the final PDF output name and path
python scripts/append-image-page.py ~/Pictures/images/image-grid.jpg --pdf ~/Downloads/input.pdf -o ~/Pictures/images/final.pdf

# Raise PDF page limit
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --max-pdf-pages 20

# Raise PDF file-size limit
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --max-pdf-mb 50

# Raise PDF parsing/rewrite timeout for an unusually complex input
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --pdf-timeout 30

# Refuse owner-restricted PDFs instead of producing unrestricted output
python scripts/append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --refuse-unrestricted-output
```

_Existing output files are not replaced unless `--overwrite` is passed._

_By default, grid outputs must stay inside the input image folder, and appended
PDF outputs must stay inside either the image folder or the source PDF folder.
The scripts also refuse Windows reserved device names and paths that would
create multiple missing folders. Pass `--allow-risky-output-path` only when an
unusual destination is intentional._

> **Note**: The append script can handle unencrypted PDFs by default.
Owner-restricted PDFs that open with an empty password are accepted, but the
output PDF will not preserve the original encryption or permission restrictions.
The script prints a warning when this happens. Pass `--refuse-unrestricted-output`
to stop instead. PDFs that require a user password are not supported.

## Behavior

- `scripts/make-image-grid.py` accepts `.heic`, `.heif`, `.jpg`, `.jpeg`, and `.png` images up to the default safety limit of 24 images.
- `scripts/make-image-grid.py` only scans files directly inside the input folder. Subfolders are ignored.
- Unreadable image files are skipped and reported instead of stopping the entire
  grid job. If no readable images remain, the script fails.
- Original input images are left untouched.
- The image grid is always written as JPG. The grid uses a white background and balanced rows/columns.
- The default grid output limit is 50,000,000 pixels. Larger grids require an explicit `--max-output-pixels` value.
- JPEG output optimization is off by default to reduce peak memory use. Pass `--optimize` to request a smaller optimized file when extra memory use is acceptable.
- With 2 images, the grid is 2 rows by 1 column, so the output is portrait-oriented.
- `scripts/append-image-page.py` keeps the image aspect ratio and centers it on a white
  US Letter page.
- `scripts/append-image-page.py` preserves source pages and simple string metadata, but
  it does not preserve encryption, permission restrictions, signatures, forms,
  outlines, attachments, document-level JavaScript, or tagged-PDF structure.
- Output paths are checked before processing starts. Unusual destinations
  outside the expected folders require `--allow-risky-output-path`.
- The scripts fail when inputs exceed configured safety limits. Use
  `--max-images`, `--max-image-pixels`, `--max-output-pixels`, or
  `--max-pdf-pages` to raise a limit for larger inputs. Use `--max-pdf-mb` to
  allow a larger PDF file before parsing. Use `--pdf-timeout` to allow more
  time for PDF parsing and rewriting before the worker process is stopped.
