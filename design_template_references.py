from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


OUT_DIR = Path("data/reference_style_concepts")
PHOTO_PATH = Path("data/extracted_photo/page1_image1.jpg")
PAGE_W, PAGE_H = A4

CV = {
    "name": "Жасан Самат",
    "first": "Жасан",
    "last": "Самат",
    "role": "IT / Ақпараттық жүйелер",
    "program": "6B06103 - Ақпараттық жүйелердің архитектурасы",
    "phone": "+7 747 140 2598",
    "email": "maratkaripzanov05@gmail.com",
    "city": "Талдыкорған, Қазақстан",
    "portfolio": "github.com / portfolio",
    "about": (
        "Ақпараттық жүйелер саласында білім алып жүрген жас маман. "
        "Дерекқорлармен, веб-технологиялармен және бағдарламалау тілдерімен жұмыс істей алады. "
        "Жаңа технологияларды тез меңгереді және командалық жобаларға белсенді қатысады."
    ),
    "education": [
        ("2022 - 2026", "Жетісу университеті", "Ақпараттық жүйелердің архитектурасы, GPA 2.63"),
        ("2024 - 2025", "Online courses", "Python, SQL, Web development"),
    ],
    "experience": [
        ("2026", "Кураторлық қызмет", "Innoverse Taldykorgan жеке меншік мектеп"),
        ("2025", "Оқу жобалары", "Веб-сайттар, дерекқорлар және мобильді қосымша прототиптері"),
    ],
    "skills": ["Python", "Java", "SQL", "HTML / CSS", "JavaScript", "MySQL", "Microsoft Office", "3ds Max"],
    "qualities": ["Жауапкершілік", "Аналитикалық ойлау", "Командада жұмыс", "Жылдам үйрену"],
    "languages": ["Қазақша", "Русский", "English B1"],
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _register_fonts()
    circle = _circle_photo(PHOTO_PATH, OUT_DIR / "circle_photo.png")

    concepts = [
        ("01_gray_header_sidebar.pdf", draw_gray_header_sidebar),
        ("02_neon_dark_cards.pdf", draw_neon_dark_cards),
        ("03_brown_timeline.pdf", draw_brown_timeline),
        ("04_navy_corporate.pdf", draw_navy_corporate),
    ]
    for filename, drawer in concepts:
        path = OUT_DIR / filename
        c = canvas.Canvas(str(path), pagesize=A4)
        drawer(c, circle)
        c.save()
        print(path)


def draw_gray_header_sidebar(c: canvas.Canvas, photo: Path | None) -> None:
    dark = colors.HexColor("#303240")
    sidebar = colors.HexColor("#dddddf")
    text = colors.HexColor("#20222a")
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(sidebar)
    c.rect(0, 0, 78 * mm, PAGE_H, stroke=0, fill=1)
    c.setFillColor(dark)
    c.rect(0, PAGE_H - 68 * mm, PAGE_W, 48 * mm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#cfd0d5"))
    c.rect(0, PAGE_H - 20 * mm, 78 * mm, 20 * mm, stroke=0, fill=1)
    if photo:
        c.setFillColor(colors.white)
        c.circle(38 * mm, PAGE_H - 45 * mm, 28 * mm, stroke=0, fill=1)
        c.drawImage(str(photo), 12 * mm, PAGE_H - 71 * mm, 52 * mm, 52 * mm, mask="auto")
    _txt(c, 92 * mm, PAGE_H - 43 * mm, CV["first"], 25, "CVBold", colors.white)
    _txt(c, 92 * mm, PAGE_H - 57 * mm, CV["last"], 25, "CVRegular", colors.white)
    _txt(c, 92 * mm, PAGE_H - 70 * mm, CV["role"], 11, "CVRegular", colors.white)
    _soft_shadow(c, 0, PAGE_H - 75 * mm, PAGE_W, 5 * mm)

    y = PAGE_H - 101 * mm
    for icon, title, lines in [
        ("A", "About Me", [CV["about"]]),
        ("C", "Contact", [CV["phone"], CV["email"], CV["city"]]),
        ("S", "Skills", CV["skills"][:5]),
        ("L", "Language", CV["languages"]),
    ]:
        c.setFillColor(text)
        c.circle(20 * mm, y + 1.8 * mm, 3.3 * mm, stroke=0, fill=1)
        _txt(c, 18.3 * mm, y - 0.3 * mm, icon, 7, "CVBold", colors.white)
        _txt(c, 28 * mm, y, title, 13, "CVBold", text)
        y -= 10 * mm
        y = _paragraphs(c, 18 * mm, y, lines, 50 * mm, 8.2, text, bullet=title in {"Skills", "Language"}) - 13 * mm

    x = 92 * mm
    y = PAGE_H - 100 * mm
    y = _timeline_section(c, x, y, "Education", CV["education"], dark, text)
    y -= 8 * mm
    y = _timeline_section(c, x, y, "Experience", CV["experience"], dark, text)
    _section(c, x, y - 8 * mm, "Achievements", [
        "Университет іс-шараларына және хакатондарға қатысу.",
        "Coursera, Stepik және Huawei Talent Program арқылы даму.",
    ], 93 * mm, dark, text)


def draw_neon_dark_cards(c: canvas.Canvas, photo: Path | None) -> None:
    bg = colors.HexColor("#12131a")
    card = colors.HexColor("#1c1f2a")
    card2 = colors.HexColor("#202331")
    lime = colors.HexColor("#a8ff1f")
    white = colors.HexColor("#f5f7fb")
    muted = colors.HexColor("#c8ccd6")
    c.setFillColor(bg)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    _blob(c, 150 * mm, PAGE_H - 48 * mm, 45 * mm, colors.HexColor("#292d38"))
    c.setFillColor(card)
    c.roundRect(8 * mm, PAGE_H - 70 * mm, 194 * mm, 58 * mm, 5 * mm, stroke=0, fill=1)
    if photo:
        c.drawImage(str(photo), 18 * mm, PAGE_H - 58 * mm, 34 * mm, 34 * mm, mask="auto")
    _txt(c, 68 * mm, PAGE_H - 34 * mm, CV["first"].upper(), 22, "CVBold", lime)
    _txt(c, 68 * mm, PAGE_H - 50 * mm, CV["last"].upper(), 22, "CVBold", lime)
    _txt(c, 68 * mm, PAGE_H - 63 * mm, CV["role"].upper(), 11, "CVBold", white)

    left_x = 8 * mm
    right_x = 64 * mm
    y = PAGE_H - 86 * mm
    _neon_card(c, left_x, y, 52 * mm, 20 * mm, "PORTFOLIO", [CV["portfolio"]], lime, card2, white)
    y -= 28 * mm
    _neon_card(c, left_x, y, 52 * mm, 42 * mm, "CONTACT", [CV["phone"], CV["email"], CV["city"]], lime, card2, white)
    y -= 51 * mm
    _neon_skill_grid(c, left_x, y, lime, card2, white)
    y -= 58 * mm
    _neon_card(c, left_x, y, 52 * mm, 35 * mm, "ОСВІТА", [item[1] for item in CV["education"][:1]] + ["2022 - 2026"], lime, card2, white)
    y -= 43 * mm
    _neon_card(c, left_x, y, 52 * mm, 28 * mm, "МОВА", CV["languages"], lime, card2, white)

    _neon_card(c, right_x, PAGE_H - 105 * mm, 138 * mm, 47 * mm, "ПРО МЕНЕ", [CV["about"]], lime, card2, muted)
    _neon_card(c, right_x, PAGE_H - 165 * mm, 138 * mm, 49 * mm, "ДОДАТКОВА ІНФОРМАЦІЯ", [
        "Відкритий до вивчення нових інструментів.",
        "Дотримуюся дедлайнів.",
        "Швидко адаптуюся до вимог проєкту.",
    ], lime, card2, muted, toggles=True)
    _neon_card(c, right_x, PAGE_H - 223 * mm, 138 * mm, 49 * mm, "ДОСВІД", [
        "Кураторлық қызмет - Innoverse Taldykorgan",
        "Оқу жобалары: веб-сайттар, дерекқорлар, мобильді прототиптер.",
    ], lime, card2, muted)
    _neon_card(c, right_x, PAGE_H - 266 * mm, 138 * mm, 32 * mm, "НАВИЧКИ", CV["skills"][:6], lime, card2, muted, chips=True)


def draw_brown_timeline(c: canvas.Canvas, photo: Path | None) -> None:
    dark = colors.HexColor("#2f2f35")
    brown = colors.HexColor("#b57d52")
    paper = colors.HexColor("#f4f4f4")
    c.setFillColor(paper)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(dark)
    c.rect(0, 0, 78 * mm, PAGE_H, stroke=0, fill=1)
    c.setFillColor(brown)
    c.roundRect(38 * mm, PAGE_H - 62 * mm, 160 * mm, 42 * mm, 21 * mm, stroke=0, fill=1)
    if photo:
        c.setFillColor(colors.white)
        c.circle(47 * mm, PAGE_H - 44 * mm, 31 * mm, stroke=0, fill=1)
        c.drawImage(str(photo), 19 * mm, PAGE_H - 72 * mm, 56 * mm, 56 * mm, mask="auto")
    _txt(c, 88 * mm, PAGE_H - 46 * mm, CV["first"] + " " + CV["last"], 22, "CVBold", colors.white)
    _txt(c, 88 * mm, PAGE_H - 59 * mm, "Professional " + CV["role"], 11, "CVRegular", colors.white)
    _grid(c, 5 * mm, PAGE_H - 45 * mm, brown)

    sy = PAGE_H - 92 * mm
    for title, lines in [
        ("Reference", ["Жетісу университеті", "Физика-математика факультеті", CV["phone"]]),
        ("Language", CV["languages"]),
        ("Skills", CV["skills"][:5]),
    ]:
        c.setFillColor(brown)
        c.circle(13 * mm, sy + 1 * mm, 5 * mm, stroke=0, fill=1)
        _txt(c, 21 * mm, sy, title, 15, "CVBold", colors.white)
        sy -= 14 * mm
        sy = _paragraphs(c, 13 * mm, sy, lines, 50 * mm, 8.8, colors.white, bullet=False, stars=title == "Skills") - 15 * mm

    x = 92 * mm
    y = PAGE_H - 91 * mm
    y = _brown_section(c, x, y, "Education", CV["education"], brown)
    y -= 12 * mm
    y = _brown_section(c, x, y, "Work Experience", CV["experience"], brown)
    _brown_section(c, x, y - 12 * mm, "Achievements", [("2024", "Projects", "Web, SQL, Python portfolio projects")], brown)


def draw_navy_corporate(c: canvas.Canvas, photo: Path | None) -> None:
    navy = colors.HexColor("#333b50")
    light = colors.HexColor("#f7f7f7")
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(navy)
    c.roundRect(0, PAGE_H - 58 * mm, 72 * mm, 58 * mm, 0, stroke=0, fill=1)
    c.roundRect(0, PAGE_H - 58 * mm, 72 * mm, 58 * mm, 12 * mm, stroke=0, fill=1)
    if photo:
        c.drawImage(str(photo), 22 * mm, PAGE_H - 42 * mm, 30 * mm, 30 * mm, mask="auto")
    _txt(c, 84 * mm, PAGE_H - 27 * mm, CV["first"].upper(), 22, "CVBold", colors.black)
    _txt(c, 84 * mm, PAGE_H - 44 * mm, CV["last"].upper(), 22, "CVBold", colors.black)
    _txt(c, 84 * mm, PAGE_H - 57 * mm, CV["role"].upper(), 12, "CVRegular", colors.black)

    c.setFillColor(navy)
    c.roundRect(5 * mm, PAGE_H - 78 * mm, 200 * mm, 14 * mm, 7 * mm, stroke=0, fill=1)
    contacts = [CV["phone"], CV["email"], CV["portfolio"], CV["city"]]
    cx = 12 * mm
    for item in contacts:
        _txt(c, cx, PAGE_H - 72 * mm, "● " + item, 7.2, "CVRegular", colors.white)
        cx += 48 * mm

    c.setFillColor(navy)
    c.roundRect(0, 0, 70 * mm, PAGE_H - 83 * mm, 0, stroke=0, fill=1)
    lx = 14 * mm
    ly = PAGE_H - 103 * mm
    for title, lines in [
        ("Education", [f"{d}  {school}" for d, school, _ in CV["education"]]),
        ("Certifications", ["Python / SQL courses", "Web development basics"]),
        ("Skills", CV["skills"][:5]),
        ("Language", CV["languages"]),
    ]:
        _txt(c, lx, ly, title, 14, "CVBold", colors.white)
        c.setStrokeColor(colors.white)
        c.line(lx, ly - 3 * mm, 61 * mm, ly - 3 * mm)
        ly -= 11 * mm
        ly = _paragraphs(c, lx, ly, lines, 45 * mm, 8, colors.white, bullet=title in {"Certifications"}) - 12 * mm

    rx = 82 * mm
    ry = PAGE_H - 98 * mm
    for title, lines in [
        ("About me", [CV["about"]]),
        ("Experience", [f"{d}: {role} - {place}" for d, role, place in CV["experience"]]),
        ("Reference", ["Жетісу университеті | Физика-математика факультеті", CV["phone"]]),
        ("Achievements", CV["achievements"] if "achievements" in CV else ["Project work", "Fast learning"]),
    ]:
        _txt(c, rx, ry, title, 14, "CVBold", navy)
        c.setStrokeColor(navy)
        c.line(rx, ry - 3 * mm, 195 * mm, ry - 3 * mm)
        ry -= 10 * mm
        ry = _paragraphs(c, rx, ry, lines, 104 * mm, 8.7, colors.black, bullet=title != "About me") - 10 * mm


def _register_fonts() -> None:
    fonts = [
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "CVRegular"),
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "CVBold"),
    ]
    for path, name in fonts:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont(name, path))


def _circle_photo(src: Path, dst: Path) -> Path | None:
    if not src.exists():
        return None
    img = Image.open(src).convert("RGB")
    side = min(img.size)
    img = img.crop(((img.width - side) // 2, (img.height - side) // 2, (img.width + side) // 2, (img.height + side) // 2))
    img = img.resize((720, 720))
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.width - 1, img.height - 1), fill=255)
    out = Image.new("RGBA", img.size, (255, 255, 255, 0))
    out.paste(img, (0, 0), mask)
    out.save(dst)
    return dst


def _txt(c: canvas.Canvas, x: float, y: float, text: str, size: float, font: str, color) -> None:
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


def _wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) <= max_chars:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def _paragraphs(
    c: canvas.Canvas,
    x: float,
    y: float,
    lines: list[str],
    width: float,
    size: float,
    color,
    bullet: bool = False,
    stars: bool = False,
) -> float:
    max_chars = max(16, int(width / (size * 0.42)))
    c.setFont("CVRegular", size)
    c.setFillColor(color)
    for line in lines:
        wrapped = _wrap(line, max_chars)
        for i, part in enumerate(wrapped):
            prefix = ""
            if i == 0 and bullet:
                prefix = "• "
            c.drawString(x, y, prefix + part)
            y -= size + 2.2
        if stars:
            c.setFillColor(colors.HexColor("#b57d52"))
            c.drawString(x + 37 * mm, y + size + 2.2, "★★★★☆")
            c.setFillColor(color)
        y -= 1.2
    return y


def _section(c: canvas.Canvas, x: float, y: float, title: str, lines: list[str], width: float, accent, text) -> float:
    _txt(c, x, y, title, 11, "CVBold", accent)
    return _paragraphs(c, x, y - 7 * mm, lines, width, 7.5, text, bullet=True)


def _timeline_section(c: canvas.Canvas, x: float, y: float, title: str, items: list[tuple[str, str, str]], accent, text) -> float:
    c.setFillColor(accent)
    c.circle(x + 1 * mm, y + 1 * mm, 3 * mm, stroke=0, fill=1)
    _txt(c, x + 10 * mm, y, title, 13, "CVBold", text)
    y -= 11 * mm
    c.setStrokeColor(colors.HexColor("#d2d2d2"))
    c.line(x + 1 * mm, y + 4 * mm, x + 1 * mm, y - 43 * mm)
    for date, school, detail in items:
        c.setFillColor(accent)
        c.circle(x + 1 * mm, y + 1 * mm, 2.4 * mm, stroke=0, fill=1)
        _txt(c, x + 10 * mm, y, f"({date})", 10, "CVBold", text)
        _txt(c, x + 10 * mm, y - 6 * mm, school.upper(), 8.5, "CVBold", text)
        _txt(c, x + 10 * mm, y - 12 * mm, detail, 7.8, "CVRegular", text)
        y -= 26 * mm
    return y


def _neon_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, lines: list[str], accent, fill, text, toggles: bool = False, chips: bool = False) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 4 * mm, stroke=0, fill=1)
    _txt(c, x + 7 * mm, y + h - 11 * mm, title, 11, "CVBold", accent)
    if chips:
        cx, cy = x + 7 * mm, y + h - 20 * mm
        for item in lines:
            tw = min(40 * mm, max(18 * mm, len(item) * 1.65 * mm))
            c.setFillColor(colors.HexColor("#4b4f5b"))
            c.roundRect(cx, cy, tw, 5 * mm, 2.5 * mm, stroke=0, fill=1)
            _txt(c, cx + 2 * mm, cy + 1.4 * mm, item, 5.6, "CVRegular", colors.white)
            cx += tw + 2 * mm
            if cx > x + w - 35 * mm:
                cx, cy = x + 7 * mm, cy - 7 * mm
        return
    yy = y + h - 20 * mm
    for line in lines:
        if toggles:
            c.setFillColor(accent)
            c.roundRect(x + 7 * mm, yy - 0.5 * mm, 6 * mm, 3 * mm, 1.5 * mm, stroke=0, fill=1)
            tx = x + 17 * mm
        else:
            tx = x + 7 * mm
        yy = _paragraphs(c, tx, yy, [line], w - 18 * mm, 6.4, text, bullet=not toggles)


def _neon_skill_grid(c: canvas.Canvas, x: float, y: float, accent, fill, text) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, 52 * mm, 50 * mm, 4 * mm, stroke=0, fill=1)
    labels = [("Ai", "Python"), ("Ps", "SQL"), ("Ae", "Web"), ("3d", "3ds Max")]
    for idx, (abbr, label) in enumerate(labels):
        cx = x + (14 if idx % 2 == 0 else 38) * mm
        cy = y + (35 if idx < 2 else 16) * mm
        c.setStrokeColor(accent)
        c.setLineWidth(2)
        c.circle(cx, cy, 7 * mm, stroke=1, fill=0)
        _txt(c, cx - 3.8 * mm, cy - 2 * mm, abbr, 10, "CVBold", colors.white)
        _txt(c, cx - 8 * mm, cy - 11 * mm, label, 5.5, "CVRegular", text)


def _brown_section(c: canvas.Canvas, x: float, y: float, title: str, items: list[tuple[str, str, str]], accent) -> float:
    c.setFillColor(accent)
    c.circle(x, y + 1 * mm, 5 * mm, stroke=0, fill=1)
    _txt(c, x + 9 * mm, y, title, 17, "CVBold", colors.black)
    y -= 13 * mm
    c.setStrokeColor(colors.HexColor("#d0d0d0"))
    c.line(x + 2 * mm, y + 6 * mm, x + 2 * mm, y - 48 * mm)
    for date, role, place in items:
        c.setFillColor(accent)
        c.circle(x + 2 * mm, y + 1 * mm, 2.2 * mm, stroke=0, fill=1)
        _txt(c, x + 12 * mm, y, date, 8.5, "CVBold", colors.black)
        _txt(c, x + 34 * mm, y, role, 9, "CVBold", colors.black)
        _txt(c, x + 34 * mm, y - 6 * mm, place, 7.3, "CVRegular", colors.black)
        y -= 22 * mm
    return y


def _grid(c: canvas.Canvas, x: float, y: float, color) -> None:
    c.setStrokeColor(color)
    c.setLineWidth(0.5)
    for i in range(7):
        c.line(x + i * 6 * mm, y, x + i * 6 * mm, y + 32 * mm)
    for j in range(5):
        c.line(x, y + j * 6 * mm, x + 36 * mm, y + j * 6 * mm)


def _soft_shadow(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    for i in range(8):
        c.setFillColor(colors.Color(0, 0, 0, alpha=max(0.02, 0.12 - i * 0.014)))
        c.rect(x, y - i * 1.5, w, h, stroke=0, fill=1)


def _blob(c: canvas.Canvas, x: float, y: float, r: float, color) -> None:
    c.setFillColor(color)
    for i in range(7):
        c.circle(x + i * 3 * mm, y + ((i % 2) * 4 - 2) * mm, r - i * 4 * mm, stroke=0, fill=1)


if __name__ == "__main__":
    main()
