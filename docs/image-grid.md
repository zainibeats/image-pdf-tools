# Image Grid

`scripts/make-image-grid.py` combines HEIC, HEIF, JPG, JPEG, and PNG images into
one balanced JPG grid. The default image limit is 24.

Original images are always preserved.

## Usage

Create a grid from a folder of images:

```bash
python scripts/make-image-grid.py ~/Pictures/receipts
```

This writes `image-grid.jpg` inside the input folder by default.

Common options:

```bash
python scripts/make-image-grid.py ~/Pictures/receipts -o named-image-grid.jpg
python scripts/make-image-grid.py ~/Pictures/receipts --max-images 60
python scripts/make-image-grid.py ~/Pictures/receipts --max-output-pixels 100000000
```

Existing output files are not replaced unless `--overwrite` is passed.

By default, grid outputs must stay inside the input image folder. Pass
`--allow-risky-output-path` only when an unusual destination is intentional.

## Notes

- Only files directly inside the input folder are scanned. Subfolders are
  ignored.
- Unreadable image files are skipped and reported.
- If no readable images remain, the grid job fails.
