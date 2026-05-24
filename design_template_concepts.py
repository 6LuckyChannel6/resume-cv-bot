from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


OUT_DIR = Path("data/design_concepts")
PHOTO_PATH = Path("data/extracted_photo/page1_image1.jpg")
PAGE_W, PAGE_H = A4


CV = {
    "name": "Жасан Самат",
    "role": "Архитектура информационных систем",
    "program": "6B06103 - Архитектура информационных систем",
    "city": "Талдыкорған, 6 мкр, 3 үй, 23",
    "birth": "23.11.2007",
    "phone": "+7 747 140 2598",
    "email": "maratkaripzanov05@gmail.com",
    "education": [
        "Жетісу университеті, физика-математика факультеті",
        "Ақпараттық жүйелердің архитектурасы, 2 курс",
        "GPA: 2.63",
    ],
    "experience": [
        ("2026 қаңтар - 2026 сәуір", "Кураторлық қызмет", "Innoverse Taldykorgan жеке меншік мектеп"),
    ],
    "skills": [
        "Python, Java, SQL, C++, C#",
        "HTML, CSS, JavaScript",
        "MySQL және дерекқорлар",
        "Microsoft Office, Excel, PowerPoint",
        "3ds Max 3D модельдеу",
    ],
    "qualities": [
        "Жауапкершілік",
        "Аналитикалық ойлау",
        "Командада жұмыс",
        "Жаңа технологияларды тез үйрену",
    ],
    "achievements": [
        "Мамандығы бойынша жоғары орташа балды тұрақты ұстап тұру.",
        "Университет іс-шараларын, конференциялар мен хакатондарды ұйымдастыруға қатысу.",
        "Coursera, Stepik және Huawei Talent Program арқылы біліктілікті арттыру.",
    ],
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    _register_fonts()
    circle_photo = _circle_photo(PHOTO_PATH, OUT_DIR / "circle_photo.png")

    templates = [
        ("01_turquoise_timeline.pdf", draw_turquoise_timeline),
        ("02_dark_split.pdf", draw_dark_split),
        ("03_black_yellow.pdf", draw_black_yellow),
        ("04_yellow_focus.pdf", draw_yellow_focus),
        ("05_blue_editorial.pdf", draw_blue_editorial),
    ]
    for filename, drawer in templates:
        path = OUT_DIR / filename
        c = canvas.Canvas(str(path), pagesize=A4)
        drawer(c, circle_photo)
        c.save()
        print(path)


def _register_fonts() -> None:
    fonts = [
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "CVRegular"),
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "CVBold"),
        ("/System/Library/Fonts/Supplemental/Arial Italic.ttf", "CVItalic"),
    ]
    for path, name in fonts:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont(name, path))
    if "CVRegular" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CVRegular", "/System/Library/Fonts/Supplemental/Arial.ttf"))


def _circle_photo(src: Path, dst: Path) -> Path | None:
    if not src.exists():
        return None
    img = Image.open(src).convert("RGB")
    side = min(img.size)
    left = (img.width - side) // 2
    top = (img.height - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((520, 520))
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.width - 1, img.height - 1), fill=255)
    out = Image.new("RGBA", img.size, (255, 255, 255, 0))
    out.paste(img, (0, 0), mask)
    out.save(dst)
    return dst


def draw_turquoise_timeline(c: canvas.Canvas, photo: Path | None) -> None:
    teal = colors.HexColor("#42c8c7")
    dark = colors.HexColor("#38434a")
    c.setFillColor(colors.HexColor("#38c2c0"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(colors.white)
    card_x, card_y, card_w, card_h = 24 * mm, 18 * mm, 162 * mm, 255 * mm
    c.roundRect(card_x, card_y, card_w, card_h, 6 * mm, stroke=0, fill=1)
    c.setStrokeColor(teal)
    c.setLineWidth(3)
    c.roundRect(card_x, card_y, card_w, card_h, 6 * mm, stroke=1, fill=0)

    if photo:
        c.drawImage(str(photo), card_x + 8 * mm, card_y + card_h - 34 * mm, 27 * mm, 27 * mm, mask="auto")
    _txt(c, card_x + 40 * mm, card_y + card_h - 16 * mm, CV["name"].upper(), 15, "CVBold", teal)
    _txt(c, card_x + 40 * mm, card_y + card_h - 23 * mm, CV["role"].upper(), 9, "CVBold", dark)
    _txt(c, card_x + 40 * mm, card_y + card_h - 29 * mm, f"Алматы | {CV['birth']}", 7.5, "CVRegular", dark)

    left_x = card_x + 14 * mm
    main_x = card_x + 33 * mm
    top = card_y + card_h - 60 * mm
    c.setStrokeColor(teal)
    c.setLineWidth(1.2)
    c.line(left_x, top + 3 * mm, left_x, card_y + 16 * mm)

    y = top
    for icon, title, lines in [
        ("E", "Опыт работы", _exp_lines()),
        ("O", "Образование", CV["education"]),
        ("K", "Курсы", ["Huawei Talent Program", "Stepik: Python және SQL"]),
        ("Ж", "Жетістіктер", CV["achievements"]),
        ("Ө", "О себе", CV["qualities"]),
    ]:
        c.setFillColor(teal)
        c.circle(left_x, y + 2 * mm, 4.2 * mm, stroke=0, fill=1)
        _txt(c, left_x - 2 * mm, y + 0.2 * mm, icon, 7, "CVBold", colors.white)
        _txt(c, main_x, y, title, 10.5, "CVBold", teal)
        y -= 7 * mm
        y = _bullets(c, main_x, y, lines, 72 * mm, 7.2, dark, bullet=False) - 6 * mm

    side_x = card_x + 112 * mm
    _side_block(c, side_x, top, "Контакты", [CV["phone"], CV["email"], CV["city"]], teal)
    _side_block(c, side_x, top - 47 * mm, "Навыки", CV["skills"], teal)
    _side_block(c, side_x, top - 124 * mm, "Қасиеттер", CV["qualities"], teal)


def draw_dark_split(c: canvas.Canvas, photo: Path | None) -> None:
    c.setFillColor(colors.HexColor("#d8d8d8"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    x, y, w, h = 52 * mm, 17 * mm, 106 * mm, 260 * mm
    c.setFillColor(colors.white)
    c.rect(x, y, w, h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#232323"))
    c.rect(x, y, 42 * mm, h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#464646"))
    c.rect(x, y + h - 65 * mm, 42 * mm, 15 * mm, stroke=0, fill=1)
    if photo:
        c.drawImage(str(photo), x + 10 * mm, y + h - 43 * mm, 22 * mm, 22 * mm, mask="auto")
    _txt(c, x + 5 * mm, y + h - 58 * mm, CV["name"].upper(), 12, "CVBold", colors.white)
    _txt(c, x + 9 * mm, y + h - 78 * mm, "CONTACT", 7.5, "CVBold", colors.white)
    _bullets(c, x + 7 * mm, y + h - 86 * mm, [CV["phone"], CV["email"], CV["birth"]], 28 * mm, 6.3, colors.white, bullet=False)
    _bar_group(c, x + 7 * mm, y + h - 122 * mm, "SOFTWARE SKILLS", ["Word", "PowerPoint", "Python", "SQL"])
    _bar_group(c, x + 7 * mm, y + h - 172 * mm, "PERSONALITY", CV["qualities"][:4])

    rx = x + 48 * mm
    ry = y + h - 20 * mm
    for title, lines in [
        ("PROFILE", [CV["program"], "Detail-oriented student with practical IT and communication skills."]),
        ("EDUCATION", CV["education"]),
        ("EXPERIENCE", _exp_lines()),
        ("SKILLS", CV["skills"]),
        ("ACHIEVEMENTS", CV["achievements"]),
    ]:
        _txt(c, rx, ry, title, 9.5, "CVBold", colors.black)
        ry -= 6 * mm
        ry = _bullets(c, rx, ry, lines, 52 * mm, 6.8, colors.black, bullet=title in {"SKILLS", "ACHIEVEMENTS"}) - 5 * mm


def draw_black_yellow(c: canvas.Canvas, photo: Path | None) -> None:
    c.setFillColor(colors.HexColor("#efefeb"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    x, y, w, h = 49 * mm, 18 * mm, 112 * mm, 258 * mm
    c.setFillColor(colors.white)
    c.rect(x, y, w, h, stroke=1, fill=1)
    c.setFillColor(colors.HexColor("#202020"))
    c.rect(x, y, 37 * mm, h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#ffd45c"))
    c.rect(x + 37 * mm, y + h - 54 * mm, w - 37 * mm, 13 * mm, stroke=0, fill=1)
    if photo:
        c.drawImage(str(photo), x + 7 * mm, y + h - 35 * mm, 22 * mm, 22 * mm, mask="auto")
    _txt(c, x + 43 * mm, y + h - 48 * mm, CV["name"], 13, "CVBold", colors.black)
    _txt(c, x + 43 * mm, y + h - 56 * mm, CV["role"], 7.2, "CVRegular", colors.black)
    _txt(c, x + 6 * mm, y + h - 55 * mm, "CONTACT", 7.5, "CVBold", colors.white)
    _bullets(c, x + 6 * mm, y + h - 64 * mm, [CV["phone"], CV["email"], CV["city"]], 27 * mm, 5.8, colors.white, bullet=False)
    _bar_group(c, x + 6 * mm, y + h - 105 * mm, "EXPERTISE", ["Python", "SQL", "Office", "3ds Max"], yellow=True)
    _dark_sidebar_text(c, x + 6 * mm, y + h - 158 * mm, "EDUCATION", CV["education"])

    rx = x + 42 * mm
    ry = y + h - 72 * mm
    for title, lines in [
        ("WORK EXPERIENCE", _exp_lines()),
        ("EDUCATION", CV["education"]),
        ("PROFESSIONAL SKILLS", CV["skills"]),
        ("ACHIEVEMENTS", CV["achievements"]),
    ]:
        _txt(c, rx, ry, title, 8.8, "CVBold", colors.black)
        c.setStrokeColor(colors.HexColor("#ffd45c"))
        c.setLineWidth(1.2)
        c.line(rx, ry - 2 * mm, rx + 20 * mm, ry - 2 * mm)
        ry -= 7 * mm
        ry = _bullets(c, rx, ry, lines, 62 * mm, 6.4, colors.black, bullet=True) - 5 * mm


def draw_yellow_focus(c: canvas.Canvas, photo: Path | None) -> None:
    yellow = colors.HexColor("#f6cf2d")
    c.setFillColor(colors.HexColor("#d3b000"))
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    x, y, w, h = 46 * mm, 18 * mm, 118 * mm, 258 * mm
    c.setFillColor(colors.white)
    c.rect(x, y, w, h, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#f3f3f3"))
    c.rect(x + 7 * mm, y, 39 * mm, h, stroke=0, fill=1)
    c.setFillColor(yellow)
    c.rect(x + 7 * mm, y + h - 62 * mm, 27 * mm, 62 * mm, stroke=0, fill=1)
    if photo:
        c.drawImage(str(photo), x + 14 * mm, y + h - 43 * mm, 30 * mm, 30 * mm, mask="auto")
    _txt(c, x + 58 * mm, y + h - 28 * mm, "ЖАСАН", 17, "CVRegular", colors.black)
    _txt(c, x + 58 * mm, y + h - 39 * mm, "САМАТ", 17, "CVBold", colors.black)
    _txt(c, x + 58 * mm, y + h - 48 * mm, CV["role"].upper(), 7.5, "CVRegular", colors.HexColor("#555555"))
    c.setStrokeColor(yellow)
    c.line(x + 58 * mm, y + h - 59 * mm, x + 100 * mm, y + h - 59 * mm)

    lx = x + 14 * mm
    _txt(c, lx, y + h - 92 * mm, "CONTACT_", 8.5, "CVBold", colors.black)
    _bullets(c, lx, y + h - 103 * mm, [CV["phone"], CV["email"], CV["city"]], 27 * mm, 6, colors.black, bullet=False)
    _dark_sidebar_text(c, lx, y + h - 142 * mm, "EDUCATION_", CV["education"], black=False)
    _dark_sidebar_text(c, lx, y + h - 198 * mm, "REFERENCE_", ["Жетісу университеті", "Физика-математика факультеті"], black=False)

    rx = x + 58 * mm
    ry = y + h - 82 * mm
    for title, lines in [
        ("JOB EXPERIENCE_", _exp_lines()),
        ("SKILLS_", CV["skills"]),
        ("INTERESTS_", ["Футбол", "Теннис", "Бағдарламалау", "Саяхат"]),
        ("QUALITIES_", CV["qualities"]),
    ]:
        _txt(c, rx, ry, title, 9, "CVBold", colors.black)
        ry -= 7 * mm
        ry = _bullets(c, rx, ry, lines, 52 * mm, 6.2, colors.black, bullet=True, accent=yellow) - 7 * mm


def draw_blue_editorial(c: canvas.Canvas, photo: Path | None) -> None:
    blue = colors.HexColor("#b8d6df")
    pale = colors.HexColor("#dcecf1")
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(blue)
    c.rect(0, PAGE_H - 78 * mm, 74 * mm, 78 * mm, stroke=0, fill=1)
    c.setFillColor(pale)
    c.rect(0, 0, 74 * mm, PAGE_H - 78 * mm, stroke=0, fill=1)
    if photo:
        c.drawImage(str(photo), 27 * mm, PAGE_H - 33 * mm, 24 * mm, 24 * mm, mask="auto")
    _txt(c, 20 * mm, PAGE_H - 51 * mm, "Жасан", 22, "CVBold", colors.black)
    _txt(c, 12 * mm, PAGE_H - 68 * mm, "Самат", 22, "CVBold", colors.black)
    _txt(c, 17 * mm, PAGE_H - 78 * mm, "IT маманы", 10, "CVBold", colors.HexColor("#333333"))

    sx = 6 * mm
    sy = PAGE_H - 95 * mm
    for title, lines in [
        ("Контакты", [CV["email"], CV["phone"], CV["city"]]),
        ("Навыки", CV["skills"]),
        ("Образование", CV["education"]),
        ("Қосымша білім", ["Huawei Talent Program", "Stepik Python"]),
    ]:
        _txt(c, sx, sy, title, 10.5, "CVBold", colors.black)
        sy -= 8 * mm
        sy = _bullets(c, sx, sy, lines, 58 * mm, 7.2, colors.black, bullet=False) - 9 * mm

    rx = 81 * mm
    ry = PAGE_H - 20 * mm
    for title, lines in [
        ("Опыт работы", _exp_lines()),
        ("Білімі", CV["education"]),
        ("Кәсіби дағдылары", CV["skills"]),
        ("Жетістіктері", CV["achievements"]),
        ("Жеке қасиеттері", CV["qualities"]),
    ]:
        c.setFillColor(blue)
        c.circle(rx, ry + 1 * mm, 3.5 * mm, stroke=0, fill=1)
        _txt(c, rx + 7 * mm, ry, title, 12, "CVBold", blue)
        ry -= 8 * mm
        ry = _bullets(c, rx + 3 * mm, ry, lines, 112 * mm, 8.2, colors.black, bullet=True) - 7 * mm


def _exp_lines() -> list[str]:
    return [f"{date}: {title} - {place}" for date, title, place in CV["experience"]]


def _txt(c: canvas.Canvas, x: float, y: float, text: str, size: float, font: str, color) -> None:
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


def _wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _bullets(
    c: canvas.Canvas,
    x: float,
    y: float,
    lines: Iterable[str],
    width: float,
    size: float,
    color,
    bullet: bool = True,
    accent=None,
) -> float:
    max_chars = max(18, int(width / (size * 0.42)))
    c.setFont("CVRegular", size)
    c.setFillColor(color)
    for line in lines:
        wrapped = _wrap(line, max_chars)
        for index, part in enumerate(wrapped):
            if bullet and index == 0:
                if accent:
                    c.setFillColor(accent)
                    c.circle(x, y + 1.4, 1.1, stroke=0, fill=1)
                    c.setFillColor(color)
                else:
                    c.drawString(x, y, "•")
                c.drawString(x + 4 * mm, y, part)
            else:
                c.drawString(x + (4 * mm if bullet else 0), y, part)
            y -= size + 2.3
    return y


def _side_block(c: canvas.Canvas, x: float, y: float, title: str, lines: list[str], color) -> None:
    c.setFillColor(color)
    c.circle(x, y + 1 * mm, 4 * mm, stroke=0, fill=1)
    _txt(c, x + 7 * mm, y, title, 9.5, "CVBold", color)
    _bullets(c, x, y - 8 * mm, lines, 43 * mm, 7, colors.HexColor("#444444"), bullet=True, accent=color)


def _bar_group(c: canvas.Canvas, x: float, y: float, title: str, items: list[str], yellow: bool = False) -> None:
    accent = colors.HexColor("#ffd45c") if yellow else colors.HexColor("#cfcfcf")
    _txt(c, x, y, title, 7.2, "CVBold", colors.white)
    y -= 8 * mm
    for idx, item in enumerate(items[:5]):
        _txt(c, x, y, item, 6, "CVRegular", colors.white)
        for i in range(5):
            c.setFillColor(accent if i <= 3 - (idx % 2) else colors.HexColor("#686868"))
            c.rect(x + 20 * mm + i * 3.2 * mm, y - 1, 2 * mm, 2 * mm, stroke=0, fill=1)
        y -= 6 * mm


def _dark_sidebar_text(
    c: canvas.Canvas,
    x: float,
    y: float,
    title: str,
    lines: list[str],
    black: bool = True,
) -> None:
    color = colors.white if black else colors.black
    _txt(c, x, y, title, 7.5, "CVBold", color)
    _bullets(c, x, y - 8 * mm, lines, 28 * mm, 5.8, color, bullet=False)


if __name__ == "__main__":
    main()
