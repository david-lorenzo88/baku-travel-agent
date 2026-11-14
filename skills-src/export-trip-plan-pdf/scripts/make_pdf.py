"""Build the PDF of a confirmed Baku trip plan for the export-trip-plan-pdf skill.

Usage (one JSON object is printed to stdout; exit code 0 even for validation errors):

  python make_pdf.py build --state JSON [--out DIR] [--photos-dir DIR]

Output: {"ok": bool, "state": {...}, "file": "<path to PDF>", "markdown": "...", "errors": [...]}
The PDF is written to --out, else the first writable of: current folder, /app/workspace, the system
temp folder (the skill folder itself is read-only at runtime). Lines and totals are recomputed from
the bundled catalog. Photos come from ../assets/photos (bundled; the sandbox has no network).
Contract: specs/001-baku-trip-planner/contracts/pdf-document.md
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pricing  # noqa: E402  (synced copy in this folder)

HERE = Path(__file__).resolve().parent
DEFAULT_PHOTOS = HERE.parent / "assets" / "photos"

pricing.MESSAGES.update({
    "not_confirmed": "The plan needs to be confirmed before I can export it as a PDF. Shall we confirm it now?",
    "photo_missing": "A photo could not be found, so a placeholder was used in the PDF.",
    "pdf_failed": "I couldn't create the PDF this time. Here is your confirmed plan instead.",
})


# --- output folder ----------------------------------------------------------------------------

def _writable(folder: Path) -> bool:
    try:
        folder.mkdir(parents=True, exist_ok=True)
        probe = folder / f".write-test-{os.getpid()}"
        probe.write_bytes(b"")
        probe.unlink()
        return True
    except OSError:
        return False


def pick_out_dir(out: str | None, candidates: list[Path] | None = None) -> Path:
    if out:
        folder = Path(out)
        if _writable(folder):
            return folder
    for folder in candidates or [Path.cwd(), Path("/app/workspace"), Path(tempfile.gettempdir())]:
        if _writable(Path(folder)):
            return Path(folder)
    raise pricing.PlanError("pdf_failed")


# --- fonts ------------------------------------------------------------------------------------

def register_fonts() -> tuple[str, str]:
    """DejaVu Sans (covers Azerbaijani letters such as ə) from matplotlib, else Helvetica."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    try:
        import matplotlib

        ttf = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        pdfmetrics.registerFont(TTFont("DejaVuSans", str(ttf / "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(ttf / "DejaVuSans-Bold.ttf")))
        return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:  # matplotlib or the font missing: fall back (some letters may not render)
        return "Helvetica", "Helvetica-Bold"


# --- document ---------------------------------------------------------------------------------

def fmt_confirmed(iso: str) -> str:
    d = datetime.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y, %H:%M')} (Baku time)"


def build_pdf(state: dict, catalog: dict, out_path: Path, photos_dir: Path) -> list[pricing.PlanError]:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader
    from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from xml.sax.saxutils import escape

    regular, bold = register_fonts()
    body = ParagraphStyle("body", fontName=regular, fontSize=10, leading=14)
    small = ParagraphStyle("small", parent=body, fontSize=8, leading=11, textColor=colors.HexColor("#555555"))
    h1 = ParagraphStyle("h1", fontName=bold, fontSize=20, leading=24, spaceAfter=4)
    h2 = ParagraphStyle("h2", fontName=bold, fontSize=13, leading=17, spaceBefore=10, spaceAfter=4)
    item = ParagraphStyle("item", fontName=bold, fontSize=11, leading=15)
    right = ParagraphStyle("right", parent=body, alignment=TA_RIGHT)

    warnings: list[pricing.PlanError] = []
    credits: list[tuple[str, str]] = []
    trip, holder, conf = state["trip"], state["holder"], state["confirmation"]
    lines = {l["item_id"]: l for l in state["lines"]}
    p = lambda text, style=body: Paragraph(escape(text), style)  # noqa: E731

    def photo(cat_item: dict):
        ph = cat_item["photos"][0]
        credits.append((cat_item["name"], ph["credit"]))
        path = photos_dir / ph["file"]
        width = 7.5 * cm
        if path.is_file():
            iw, ih = ImageReader(str(path)).getSize()
            scale = min(width / iw, (6 * cm) / ih)  # cap tall portrait photos at 6 cm
            return Image(str(path), width=iw * scale, height=ih * scale)
        warnings.append(pricing.PlanError("photo_missing", f"Photo missing for {cat_item['name']}; placeholder used."))
        box = Table([[p(f"Photo: {cat_item['name']}", small)]], colWidths=[width], rowHeights=[width * 0.6])
        box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#DDDDDD")),
                                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        return box

    def block(img, *paras):
        t = Table([[img, list(paras)]], colWidths=[8 * cm, 9 * cm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
        return KeepTogether([t, Spacer(1, 6)])

    story = [
        p("Baku Trip Plan", h1),
        p(f"Confirmation reference: {conf['reference']} · Confirmed: {fmt_confirmed(conf['confirmed_at'])}"),
        p("Plan holder", h2),
        p(f"Name: {holder['full_name']}"),
        p(f"Email: {holder['email']}"),
        p(f"Phone: {holder['phone']}"),
        p("Trip", h2),
        p(f"Check-in: {pricing.fmt_date(trip['check_in'])} · Check-out: {pricing.fmt_date(trip['check_out'])} · "
          f"{pricing.plural(trip['nights'], 'night')} · {pricing.plural(trip['travelers'], 'traveler')}"),
        p("Hotel", h2),
    ]
    h = catalog["_hotels"][state["hotel_id"]]
    hl = lines[state["hotel_id"]]
    story.append(block(
        photo(h),
        p(h["name"], item),
        p(h["neighborhood"]),
        p(f"{pricing.fmt_azn(pricing.dec(hl['unit_price']))} per person per night"),
        p(f"{hl['quantity_label']} · Stay total {pricing.fmt_azn(pricing.dec(hl['line_total']))}"),
    ))

    story.append(p("Activities", h2))
    if not state["activity_ids"]:
        story.append(p("No activities selected."))
    for aid in state["activity_ids"]:
        a, al = catalog["_activities"][aid], lines[aid]
        story.append(block(
            photo(a),
            p(a["name"], item),
            p(f"{pricing.fmt_azn(pricing.dec(al['unit_price']))} per person · {a['duration']}"),
            p(f"{al['quantity_label']} · {pricing.fmt_azn(pricing.dec(al['line_total']))}"),
        ))

    story.append(p("Totals", h2))
    rows = [[p("Item", item), p("Price", item), p("Qty", item), p("Total", item)]]
    for l in state["lines"]:
        rows.append([p(l["name"]), p(pricing.fmt_azn(pricing.dec(l["unit_price"])), right),
                     p(l["quantity_label"]), p(pricing.fmt_azn(pricing.dec(l["line_total"])), right)])
    rows.append([p("Grand total", item), "", "", p(pricing.fmt_azn(pricing.dec(state["grand_total"])), ParagraphStyle("gt", parent=right, fontName=bold))])
    table = Table(rows, colWidths=[6.5 * cm, 3 * cm, 4.5 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story += [table, Spacer(1, 10)]
    story.append(p(
        f"Sample prices from the agent's catalog (version {state.get('catalog_version') or catalog.get('catalog_version')}) "
        "at the time of confirmation. This is a trip plan, not a booking; no reservation or payment has been made.",
        small,
    ))
    story.append(p("Photo credits", h2))
    for name, credit in credits:
        story.append(p(f"{name}: {credit}", small))

    doc = SimpleDocTemplate(str(out_path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm, title="Baku Trip Plan",
                            author="Baku Travel Planner")
    doc.build(story)
    return warnings


def cmd_build(args, catalog):
    state = pricing.recompute(pricing.parse_state(args.state), catalog)
    conf = state.get("confirmation") or {}
    if state.get("status") != "confirmed" or not conf.get("reference") or not state.get("holder") or not state.get("hotel_id"):
        raise pricing.PlanError("not_confirmed")
    folder = pick_out_dir(args.out)
    out_path = folder / f"Baku-Trip-{conf['reference']}.pdf"
    warnings = build_pdf(state, catalog, out_path, Path(args.photos_dir) if args.photos_dir else DEFAULT_PHOTOS)
    md = f"Here is your trip plan as a PDF: **{out_path.name}**"
    return {
        "ok": True,
        "state": state,
        "file": str(out_path),
        "markdown": md,
        "errors": [{"code": w.code, "message": w.message} for w in warnings],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="make_pdf.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("build")
    s.add_argument("--state", required=True)
    s.add_argument("--out")
    s.add_argument("--photos-dir")
    args = parser.parse_args(argv)

    catalog = pricing.load_catalog(pricing.default_catalog_path(__file__))
    try:
        incoming = pricing.parse_state(args.state)
    except pricing.PlanError:
        incoming = None
    try:
        envelope = cmd_build(args, catalog)
    except pricing.PlanError as err:
        envelope = pricing.error_envelope(incoming, err, file=None)
    pricing.emit(envelope)
    return 0


if __name__ == "__main__":
    sys.exit(main())
