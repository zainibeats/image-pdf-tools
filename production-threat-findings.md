# Production Threat Findings

Ordered by most likely and largest blast radius first.

## 1. Hostile or unusually complex PDFs can exhaust CPU or memory before the page limit helps

`append-image-page.py` reads the input PDF with `PdfReader(str(source_pdf))` and then evaluates `len(source_reader.pages)` before enforcing `--max-pdf-pages` (`append-image-page.py:242-256`). The page-count limit does not cap input file size, PDF object count, compressed stream size, malformed cross-reference tables, embedded files, or parser work needed to discover the pages.

In production, a malicious or accidentally huge PDF can hang the script, consume large amounts of memory, or crash the Python process even if it has only a small number of pages. This is especially risky on non-technical users' desktops because the process may appear stuck and there is no timeout, file-size limit, or clear recovery path.

Progress: `append-image-page.py` now enforces a pre-parse `--max-pdf-mb` limit, defaulting to 25 MiB, before calling `PdfReader`. This reduces the largest accidental/hostile-file path, though a true parser timeout would still need a subprocess-based execution boundary.

## 2. Default image-grid settings can consume hundreds of megabytes and fail on normal desktops

`make-image-grid.py` allows a default output up to `200_000_000` pixels (`make-image-grid.py:19`, `make-image-grid.py:238-243`). The default 40-image case with 1200x1600 cells creates a canvas around 80 million RGB pixels before JPEG optimization (`make-image-grid.py:17`, `make-image-grid.py:55-70`, `make-image-grid.py:245`). That canvas alone is roughly 240 MB, and Pillow can need additional memory while resizing images and saving with `optimize=True` (`make-image-grid.py:251-265`).

In production, users on lower-memory Windows, macOS, or Linux machines may see the script terminate, freeze, or be killed by the OS during ordinary supported use. The same risk exists in `append-image-page.py` when large images are converted, resized, and pasted into a PDF page (`append-image-page.py:164-188`), especially if users raise `--dpi` or `--max-image-pixels`.

Progress: `make-image-grid.py` now defaults to 24 images and a 50,000,000-pixel output ceiling, validates the JPG output suffix before allocating the canvas, leaves JPEG `optimize` off unless `--optimize` is passed, and asks Pillow to draft-decode large JPEG inputs near their final cell size before resizing. `append-image-page.py` now checks the original image pixel count, draft-decodes large JPEG inputs near the target page size, and thumbnails before RGB conversion/compositing. Users can still opt into higher memory use with larger limits, higher DPI, or `--optimize`.

## 3. One corrupt, unsupported, or partially synced image aborts the entire grid job

`make-image-grid.py` collects files by extension, then fails the whole run when any selected file cannot be decoded (`make-image-grid.py:147-157`, `make-image-grid.py:247-255`). This includes corrupted files, cloud-storage placeholders, partially copied images, phone export artifacts with a supported extension but unsupported encoding, or images being written while the script is running.

In production, a single bad file in a user-selected folder prevents all other valid images from being processed. For non-technical users, the failure can be difficult to resolve because the script does not quarantine bad inputs, continue with valid images, or produce a preflight report of all failing files.

Progress: `make-image-grid.py` now preflights selected inputs before allocating the grid, skips unreadable or unsupported-by-decoder files with stderr warnings, continues with the readable images, and prints a skipped count in the final summary. The script still fails if no readable images remain, and configured safety-limit violations such as `--max-image-pixels` remain hard stops.

## 4. Atomic replacement is not durable across power loss or OS crash

Both scripts write to a temporary file and then replace the destination (`append-image-page.py:193-211`, `make-image-grid.py:175-198`). This protects against many partial-write failures, but neither script flushes and fsyncs the temporary file or its parent directory before or after replacement.

In production, a power outage, forced reboot, removable-drive disconnect, or cloud-sync interruption can still leave no durable final output, an older output, or an orphaned hidden temporary file. This matters most when `--overwrite` is used, because the user may believe an existing production PDF or JPG has been safely replaced when the filesystem has not actually committed the new file.

Progress: Both scripts now fsync the completed temporary output before replacement and fsync the output directory before and after the final rename where the operating system supports directory fsync (`append-image-page.py:176-260`, `make-image-grid.py:219-264`). This materially improves crash durability on normal POSIX filesystems, though some platforms, network mounts, removable media, and cloud-sync layers can still ignore or weaken those guarantees.

## 5. The overwrite protection has a race window

Both scripts check whether the output exists before doing the expensive work, then later replace the output path (`append-image-page.py:144-145`, `append-image-page.py:193-211`, `make-image-grid.py:295-296`, `make-image-grid.py:175-198`). If another process creates or changes that path after the check but before `Path.replace`, the scripts can replace it even when `--overwrite` was not originally allowed.

In production, this can destroy a file created by another process, a cloud-sync client, or a second copy of the script launched by mistake. The risk is higher in shared folders, synced folders, network drives, and desktop workflows where users may double-click or rerun commands without realizing a previous run is still active.

Progress: Both atomic write helpers now make the final publish step honor `--overwrite`. When overwrite is not allowed, the completed temp file is linked into place with exclusive destination creation and the command fails if the output path appeared after the early validation check (`append-image-page.py:192-281`, `make-image-grid.py:235-286`). When `--overwrite` is passed, the scripts keep the intentional replacement behavior. Regression tests cover both refusing and allowing replacement for the PDF and image write paths.

## 6. PDF output can silently drop security restrictions and document structure

`append-image-page.py` decrypts owner-restricted PDFs with an empty password when possible (`append-image-page.py:214-229`), then writes a new PDF with pages and simple string metadata only (`append-image-page.py:261-275`). It does not preserve encryption, permission restrictions, signatures, forms, outlines, attachments, document-level JavaScript, tagged-PDF structure, or other catalog-level features.

In production, the resulting PDF may no longer meet the same compliance, accessibility, workflow, or security expectations as the input PDF. The largest risk is that an owner-restricted PDF can become an unrestricted output PDF without an explicit user warning.

## 7. Output paths can target sensitive or unintended locations too easily

Both scripts accept arbitrary output paths and create missing parent directories (`append-image-page.py:115-120`, `append-image-page.py:196`, `make-image-grid.py:291-296`, `make-image-grid.py:183`, `make-image-grid.py:261`). They do not check for protected locations, network drives, removable drives, reserved Windows device names, or whether the destination is inside an expected workspace.

In production, a typo or pasted path can write files into an unintended folder, create unexpected directories, or fail late with platform-specific errors. For non-technical users, this is a realistic data-handling risk because the scripts provide no confirmation step or path safety warning before writing.

## 8. HEIC/HEIF support may fail on some supported desktops despite the documented workflow

`make-image-grid.py` only registers HEIC/HEIF support if a selected source has a HEIC/HEIF extension (`make-image-grid.py:307-308`), and installation depends on `pillow-heif` from `requirements.txt`. On some Windows, macOS, Linux, Python-version, or CPU-architecture combinations, the dependency installation or native image decoding can fail even when Pillow itself installs.

In production, users may follow the documented setup and still be unable to process common phone images. Because HEIC/HEIF is one of the advertised input formats, this is a deployment reliability risk rather than a cosmetic compatibility issue.

## 9. Output validation happens after large grid allocation

`make-image-grid.py` creates the full RGB canvas before checking whether the output suffix is `.jpg` or `.jpeg` (`make-image-grid.py:245`, `make-image-grid.py:261-264`). If a user accidentally passes `-o output.png` or another unsupported suffix, the script can spend significant memory and time processing the full job before failing.

In production, this turns a simple user typo into an avoidable resource spike. On constrained desktops, it can cause an apparent hang or process termination even though the command was invalid from the start.
