# Image PDF Tools

Small Python tools for preparing image-based PDF attachments. Each script can be
used on its own, but they also work well together for weekly receipt workflows:
collect receipt images, turn them into one grid image, then attach that image to
the end of an expense report in PDF format.

Original images and PDFs are always preserved.

## Tools

- `make-image-grid.py`: combines HEIC, HEIF, JPG, JPEG, and PNG images into one
  balanced JPG grid. Default image limit is 40. 
- `append-image-page.py`: appends a JPG/JPEG image as a US Letter page at the
  end of an existing PDF. Default input PDF limit is 10 pages. 

## Dependencies

- Python 3.10+
- `Pillow`
- `pillow-heif`
- `pypdf[crypto]`

## Install

Install dependencies in a standard Python virtual environment.

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
python make-image-grid.py ~/Pictures/images
```

This writes `image-grid.jpg` inside the input folder by default.

Append that image to an existing PDF:

```bash
python append-image-page.py ~/Pictures/images/image-grid.jpg --pdf ~/Downloads/input.pdf
```

This writes a PDF next to the image by default:

```text
~/Pictures/images/image-grid.pdf
```

## Examples

**Image Grid:**

```bash
# Choosing the grid output name and path
python make-image-grid.py ~/Pictures/images -o ~/Desktop/image-grid.jpg

# Raise the batch limit for a larger image set:
python make-image-grid.py ~/Pictures/images --max-images 60
```

**Append Image to PDF:**

```bash
# Choosing the final PDF output name and path
python append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf -o ~/Desktop/final.pdf

# Raise PDF page limit
python append-image-page.py ~/Desktop/image-grid.jpg --pdf ~/Downloads/input.pdf --max-pdf-pages 20
```

_Existing output files are not replaced unless `--overwrite` is passed._

> **Note**: The append script can handle unencrypted PDFs and owner-restricted PDFs that
open with an empty password. PDFs that require a user password are not
supported.

## Behavior

- `make-image-grid.py` accepts `.heic`, `.heif`, `.jpg`, `.jpeg`, and `.png` images up to the default safety limit of 40 images.
- `make-image-grid.py` only scans files directly inside the input folder. Subfolders are ignored.
- Original input images are left untouched.
- The image grid is always written as JPG. The grid uses a white background and balanced rows/columns.
- With 2 images, the grid is 2 rows by 1 column, so the output is portrait-oriented.
- `append-image-page.py` keeps the image aspect ratio and centers it on a white
  US Letter page.
- The scripts fail when inputs exceed configured safety limits. Use
  `--max-images`, `--max-image-pixels`, `--max-output-pixels`, or
  `--max-pdf-pages` to raise a limit for larger inputs.
