---
name: export-trip-plan-pdf
description: "Exports a confirmed Baku trip plan as a downloadable PDF with the holder, dates, hotel, activities with photos, line totals and grand total. Use when the traveler asks for the plan as a PDF, document or download."
---

# Export the trip plan as PDF

## When to use

Use this skill when the traveler asks for the plan as a PDF, a document, a file or a download.
Only a **confirmed** plan can be exported. If the plan is still a draft, say it must be confirmed
first and offer to confirm it (skill `confirm-trip-plan`).

## How to run the script

The script is `scripts/make_pdf.py` in this skill's folder. Run it from Python with an argument
list (no shell quoting). The skill folder is read-only, so pass a writable folder as `--out`
(your current working folder, for example `/app/workspace`):

```python
import json, os, subprocess, sys
SKILL_DIR = "<folder that contains this SKILL.md>"
out = subprocess.run([sys.executable, f"{SKILL_DIR}/scripts/make_pdf.py", "build",
                      "--state", json.dumps(state), "--out", os.getcwd()],
                     capture_output=True, text=True, check=True)
result = json.loads(out.stdout)   # {"ok", "state", "file", "markdown", "errors"}
```

Pass the latest `state` from the previous script call (the one returned by `confirm`), unchanged.

## Procedure

1. Call `build` with the latest state.
2. If `ok` is true, return the PDF at `result["file"]` to the traveler as a downloadable file and
   show `markdown` as normal Markdown (not in a code block).
3. If `errors` contains `photo_missing`, still return the file; mention that one photo was
   replaced by a placeholder.
4. If `ok` is false with `not_confirmed`, show `markdown` and offer to confirm the plan.
5. If the script can't run or no file is produced, say so plainly and show the confirmed plan again
   (from `confirm-trip-plan`'s last result). Never claim a PDF exists when it doesn't.

## Rules

- The PDF content comes only from the script. Don't create a PDF yourself with other code, and
  don't change names, prices or totals.
- The PDF contains only the holder's name, email and phone — never add other personal data.
- The traveler can ask for the PDF again; run `build` again with the same confirmed state.
