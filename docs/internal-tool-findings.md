# Internal Tool Branch Findings

## Context

This repository supports a weekly expense workflow for roughly 30 to 100
employees:

1. Employees collect receipt or expense images during the week.
2. They create one image grid from those images.
3. They enter expenses on the company website.
4. They download the generated expense PDF.
5. They append the image grid to that PDF.

The process cannot be automated end to end because the company website sits in
the middle of the workflow.

## Branch Comparison

### main

The `main` branch is simpler from a repository perspective. The two user-facing
scripts live at the repository root:

- `make-image-grid.py`
- `append-image-page.py`

This makes command examples shorter, but it removes the guided launchers and the
organized `scripts/`, `tests/`, and `docs/` layout.

`main` also makes owner-restricted PDF output less strict. Owner-restricted PDFs
that open with an empty password are accepted by default, and the output is
written without preserving the original encryption or permission restrictions.
The script prints a warning. Users can opt into stricter behavior with
`--refuse-unrestricted-output`.

The main drawback is that `main` is less friendly for non-technical weekly use.
Employees need to know how to set up Python, install dependencies, and run the
right commands.

### dev

The `dev` branch is better packaged for an internal tool. It keeps command line
tools under `scripts/`, tests under `tests/`, and supporting notes under `docs/`.
More importantly, it includes guided launchers:

- `run-image-pdf-tools.bat`
- `run-image-pdf-tools.sh`

The launchers create a local virtual environment, install dependencies, and show
a menu for common workflows. This reduces support burden for occasional users
who only need the tool once per week.

`dev` also has a PDF parsing/rewrite timeout, which is useful for malformed or
unusually complex PDFs. Instead of hanging indefinitely, the append command can
fail with a clear timeout error.

The main drawback is stricter behavior around owner-restricted PDFs. Users must
explicitly pass `--allow-unrestricted-output` before the script will rewrite an
owner-restricted PDF as unrestricted output.

## Recommendation

Use `dev` as the base for the internal employee tool.

The guided launchers and menu are more important than the flatter file layout in
`main`. For a 30 to 100 person group, the ideal user experience is not "run this
Python command"; it is "open the launcher, choose the action, drag in the folder
or file path, and read the result."

Recommended product shape:

- Keep the `dev` repository layout.
- Keep the Windows and macOS/Linux launchers.
- Keep separate menu actions for making a grid and appending a grid to a PDF.
- Keep the PDF timeout behavior from `dev`.
- Keep original files preserved by default.
- Keep output overwrite protection by default.

The combined "make grid, then append to PDF" menu option is useful for testing
or edge cases, but the normal employee workflow should emphasize the two
separate steps because the PDF is only available after website submission.

## PDF Restriction Decision

The only behavior worth considering from `main` is owner-restricted PDF handling.

If company-downloaded PDFs are usually unrestricted, keep `dev` as-is. Explicit
consent is safer and clearer.

If company-downloaded PDFs commonly fail because they are owner-restricted but
open normally in a PDF viewer, adopt `main`'s default behavior: allow empty
password owner-restricted PDFs by default, warn clearly, and provide a strict
mode flag.

Before making that change, test several real downloaded expense PDFs from the
company website.

## Operational Notes

For internal deployment, the next useful improvements would be:

- Add a short employee-facing quickstart that starts with the launcher, not the
  raw Python commands.
- Rename the output PDF more clearly, for example `expense-with-receipts.pdf`,
  so users do not confuse it with the downloaded original.
- Consider hiding advanced flags from the launcher while keeping them available
  in the scripts.
- Test on the actual managed Windows environment employees use, especially
  Python availability, script execution policy, and package installation.

## Verification

Both branches passed their existing unit tests during review:

- `main`: `python -m unittest test_atomic_writes.py`
- `dev`: `python -m unittest tests/test_atomic_writes.py`

Each reported 18 passing tests.
