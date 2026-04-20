# What `95-export-bundle.sh` Does

This script is the **final output builder** for the package.

## Simple explanation
While you work, you keep editing these source files:
- `reports/report.md`
- `reports/executive-summary.md`
- `reports/findings.md`
- `reports/remediation.md`
- `slides/slides.md`

When you are done, `bash scripts/95-export-bundle.sh` will:
1. rebuild the working slide file from the findings file
2. create dated copies of the report files
3. create a dated copy of the slide file
4. try to export HTML/PDF/PPTX if `pandoc` exists
5. write bundle notes saying what worked and what did not

## Why this is useful
It gives you a **clean final bundle** without overwriting your working notes.

Think of it like this:
- working files = your editable draft
- export bundle = your packaged handoff output

## When to use it
Use it near the end of the assessment, after you have updated the report and findings.

## What it is NOT
- it does not do pentesting for you
- it does not collect evidence
- it does not validate findings
- it does not install dependencies

It only helps package your deliverables.
