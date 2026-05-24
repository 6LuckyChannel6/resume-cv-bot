from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image, ImageDraw
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


PAGE_W, PAGE_H = A4
LANGUAGES = ("kk", "ru", "en")
LANGUAGE_NAMES = {"kk": "Қазақша", "ru": "Русский", "en": "English"}

TEMPLATES = {
    "gray": "Gray",
    "neon": "Neon",
    "brown": "Brown",
    "navy": "Navy",
}

FIELD_LABELS = {
    "profile": {"kk": "Өзім туралы", "ru": "О себе", "en": "About me"},
    "contacts": {"kk": "Байланыс", "ru": "Контакты", "en": "Contact"},
    "facts": {"kk": "Жеке ақпарат", "ru": "Личные данные", "en": "Personal info"},
    "education": {"kk": "Білімі", "ru": "Образование", "en": "Education"},
    "experience": {"kk": "Жұмыс тәжірибесі", "ru": "Опыт работы", "en": "Experience"},
    "additional_education": {
        "kk": "Қосымша білім",
        "ru": "Дополнительное образование",
        "en": "Additional education",
    },
    "qualification": {"kk": "Біліктілігі", "ru": "Квалификация", "en": "Qualification"},
    "skills": {"kk": "Дағдылар", "ru": "Навыки", "en": "Skills"},
    "qualities": {"kk": "Жеке қасиеттер", "ru": "Качества", "en": "Qualities"},
    "achievements": {"kk": "Жетістіктер", "ru": "Достижения", "en": "Achievements"},
    "additional_info": {
        "kk": "Қосымша ақпарат",
        "ru": "Дополнительная информация",
        "en": "Additional information",
    },
    "birth_date": {"kk": "Туған күні", "ru": "Дата рождения", "en": "Date of birth"},
    "city": {"kk": "Қала", "ru": "Город", "en": "City"},
    "marital_status": {"kk": "Отбасылық жағдай", "ru": "Семейное положение", "en": "Marital status"},
    "phone": {"kk": "Телефон", "ru": "Телефон", "en": "Phone"},
    "email": {"kk": "Email", "ru": "Email", "en": "Email"},
}


@dataclass
class CVData:
    full_name: str
    degree_program: str
    current_education: str
    birth_date: str
    city: str
    marital_status: str
    phone: str
    email: str
    experience: str
    education_details: str
    additional_education: str
    qualification: str
    professional_skills: list[str] = field(default_factory=list)
    personal_qualities: list[str] = field(default_factory=list)
    achievements: list[str] = field(default_factory=list)
    additional_info: list[str] = field(default_factory=list)
    photo_path: str | None = None
    template: str = "gray"
    translations: dict[str, dict[str, str | list[str]]] = field(default_factory=dict)


def split_items(raw_text: str) -> list[str]:
    text = raw_text.replace(";", "\n").replace(",", "\n")
    items = []
    for item in text.splitlines():
        cleaned = item.strip(" -•\t")
        if cleaned and cleaned != "-":
            items.append(cleaned)
    return items


def generate_cv_pdf(data: CVData, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    _register_fonts()
    photo = _circle_photo(data.photo_path, output.with_suffix(".photo.png"))

    pdf = canvas.Canvas(str(output), pagesize=A4)
    drawers: dict[str, Callable[[canvas.Canvas, CVData, str, Path | None], None]] = {
        "gray": _draw_gray,
        "neon": _draw_neon,
        "brown": _draw_brown,
        "navy": _draw_navy,
    }
    draw = drawers.get(data.template, _draw_gray)

    for index, language in enumerate(LANGUAGES):
        if index:
            pdf.showPage()
        draw(pdf, _localized_data(data, language), language, photo)

    pdf.save()
    return output


def _localized_data(data: CVData, language: str) -> CVData:
    values = data.translations.get(language)
    if not values:
        return data
    return replace(
        data,
        degree_program=str(values.get("degree_program", data.degree_program)),
        current_education=str(values.get("current_education", data.current_education)),
        city=str(values.get("city", data.city)),
        marital_status=str(values.get("marital_status", data.marital_status)),
        experience=str(values.get("experience", data.experience)),
        education_details=str(values.get("education_details", data.education_details)),
        additional_education=str(values.get("additional_education", data.additional_education)),
        qualification=str(values.get("qualification", data.qualification)),
        professional_skills=list(values.get("professional_skills", data.professional_skills)),
        personal_qualities=list(values.get("personal_qualities", data.personal_qualities)),
        achievements=list(values.get("achievements", data.achievements)),
        additional_info=list(values.get("additional_info", data.additional_info)),
    )


def _draw_gray(c: canvas.Canvas, data: CVData, lang: str, photo: Path | None) -> None:
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

    first, last = _name_parts(data.full_name)
    _txt(c, 92 * mm, PAGE_H - 43 * mm, first, 25, "CVBold", colors.white)
    _txt(c, 92 * mm, PAGE_H - 57 * mm, last, 25, "CVRegular", colors.white)
    _txt(c, 92 * mm, PAGE_H - 70 * mm, data.degree_program, 10.5, "CVRegular", colors.white)
    _soft_shadow(c, 0, PAGE_H - 75 * mm, PAGE_W, 5 * mm)

    y = PAGE_H - 101 * mm
    for marker, title, lines, bullet in [
        ("A", _label("profile", lang), [_profile_text(data, lang)], False),
        ("C", _label("contacts", lang), _contacts(data, lang), False),
        ("S", _label("skills", lang), data.professional_skills[:7], True),
        ("L", _label("qualities", lang), data.personal_qualities[:5], True),
    ]:
        c.setFillColor(text)
        c.circle(20 * mm, y + 1.8 * mm, 3.3 * mm, stroke=0, fill=1)
        _txt(c, 18.3 * mm, y - 0.3 * mm, marker, 7, "CVBold", colors.white)
        _txt(c, 28 * mm, y, title, 12.5, "CVBold", text)
        y -= 9 * mm
        y = _paragraphs(c, 18 * mm, y, lines, 51 * mm, 7.2, text, bullet=bullet, min_y=16 * mm) - 10 * mm

    x = 92 * mm
    y = PAGE_H - 100 * mm
    y = _timeline_section(c, x, y, _label("education", lang), _education_items(data), dark, text)
    y -= 7 * mm
    y = _timeline_section(c, x, y, _label("experience", lang), _experience_items(data), dark, text)
    y = _simple_section(c, x, y - 7 * mm, _label("achievements", lang), data.achievements, 92 * mm, dark, text)
    _simple_section(c, x, y - 5 * mm, _label("additional_info", lang), data.additional_info, 92 * mm, dark, text)


def _draw_neon(c: canvas.Canvas, data: CVData, lang: str, photo: Path | None) -> None:
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
    first, last = _name_parts(data.full_name)
    _txt(c, 68 * mm, PAGE_H - 34 * mm, first.upper(), 21, "CVBold", lime)
    _txt(c, 68 * mm, PAGE_H - 50 * mm, last.upper(), 21, "CVBold", lime)
    _txt(c, 68 * mm, PAGE_H - 63 * mm, data.degree_program.upper(), 9.4, "CVBold", white)
    _txt(c, 176 * mm, PAGE_H - 20 * mm, LANGUAGE_NAMES[lang], 8, "CVBold", muted)

    left_x = 8 * mm
    right_x = 64 * mm
    y = PAGE_H - 86 * mm
    _neon_card(c, left_x, y, 52 * mm, 42 * mm, _label("contacts", lang), _contacts(data, lang), lime, card2, white)
    y -= 51 * mm
    _neon_skill_grid(c, left_x, y, data.professional_skills[:4], lime, card2, white)
    y -= 58 * mm
    _neon_card(c, left_x, y, 52 * mm, 36 * mm, _label("education", lang), _compact_lines(data.current_education), lime, card2, white)
    y -= 44 * mm
    _neon_card(c, left_x, y, 52 * mm, 32 * mm, _label("qualities", lang), data.personal_qualities[:4], lime, card2, white)

    _neon_card(c, right_x, PAGE_H - 105 * mm, 138 * mm, 48 * mm, _label("profile", lang), [_profile_text(data, lang)], lime, card2, muted)
    _neon_card(c, right_x, PAGE_H - 165 * mm, 138 * mm, 49 * mm, _label("additional_info", lang), _nonempty(data.additional_info, data.qualification), lime, card2, muted, toggles=True)
    _neon_card(c, right_x, PAGE_H - 223 * mm, 138 * mm, 49 * mm, _label("experience", lang), _compact_lines(data.experience), lime, card2, muted)
    _neon_card(c, right_x, PAGE_H - 266 * mm, 138 * mm, 32 * mm, _label("skills", lang), data.professional_skills[:7], lime, card2, muted, chips=True)


def _draw_brown(c: canvas.Canvas, data: CVData, lang: str, photo: Path | None) -> None:
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
    _txt(c, 88 * mm, PAGE_H - 46 * mm, data.full_name, 20, "CVBold", colors.white)
    _txt(c, 88 * mm, PAGE_H - 59 * mm, data.degree_program, 9.2, "CVRegular", colors.white)
    _grid(c, 5 * mm, PAGE_H - 45 * mm, brown)

    sy = PAGE_H - 92 * mm
    for title, lines, stars in [
        (_label("contacts", lang), _contacts(data, lang), False),
        (_label("facts", lang), _facts(data, lang), False),
        (_label("skills", lang), data.professional_skills[:6], True),
        (_label("qualities", lang), data.personal_qualities[:4], False),
    ]:
        c.setFillColor(brown)
        c.circle(13 * mm, sy + 1 * mm, 5 * mm, stroke=0, fill=1)
        _txt(c, 21 * mm, sy, title, 13.5, "CVBold", colors.white)
        sy -= 12 * mm
        sy = _paragraphs(c, 13 * mm, sy, lines, 50 * mm, 7.4, colors.white, bullet=False, stars=stars, min_y=12 * mm) - 12 * mm

    x = 92 * mm
    y = PAGE_H - 91 * mm
    y = _brown_section(c, x, y, _label("education", lang), _education_items(data), brown)
    y -= 10 * mm
    y = _brown_section(c, x, y, _label("experience", lang), _experience_items(data), brown)
    y -= 10 * mm
    y = _brown_section(c, x, y, _label("achievements", lang), _dated_items(data.achievements), brown)
    _simple_section(c, x, y - 6 * mm, _label("additional_info", lang), data.additional_info, 93 * mm, brown, colors.black)


def _draw_navy(c: canvas.Canvas, data: CVData, lang: str, photo: Path | None) -> None:
    navy = colors.HexColor("#333b50")
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(navy)
    c.roundRect(0, PAGE_H - 58 * mm, 72 * mm, 58 * mm, 12 * mm, stroke=0, fill=1)
    if photo:
        c.drawImage(str(photo), 22 * mm, PAGE_H - 42 * mm, 30 * mm, 30 * mm, mask="auto")
    first, last = _name_parts(data.full_name)
    _txt(c, 84 * mm, PAGE_H - 27 * mm, first.upper(), 22, "CVBold", colors.black)
    _txt(c, 84 * mm, PAGE_H - 44 * mm, last.upper(), 22, "CVBold", colors.black)
    _txt(c, 84 * mm, PAGE_H - 57 * mm, data.degree_program.upper(), 9.5, "CVRegular", colors.black)

    c.setFillColor(navy)
    c.roundRect(5 * mm, PAGE_H - 78 * mm, 200 * mm, 14 * mm, 7 * mm, stroke=0, fill=1)
    contacts = [data.phone, data.email, data.city]
    cx = 12 * mm
    for item in contacts:
        _txt(c, cx, PAGE_H - 72 * mm, "• " + item, 7, "CVRegular", colors.white)
        cx += 62 * mm

    c.setFillColor(navy)
    c.rect(0, 0, 70 * mm, PAGE_H - 83 * mm, stroke=0, fill=1)
    lx = 14 * mm
    ly = PAGE_H - 103 * mm
    for title, lines in [
        (_label("education", lang), _compact_lines(data.current_education)),
        (_label("additional_education", lang), _nonempty(_compact_lines(data.additional_education), data.qualification)),
        (_label("skills", lang), data.professional_skills[:6]),
        (_label("qualities", lang), data.personal_qualities[:5]),
    ]:
        _txt(c, lx, ly, title, 12.5, "CVBold", colors.white)
        c.setStrokeColor(colors.white)
        c.line(lx, ly - 3 * mm, 61 * mm, ly - 3 * mm)
        ly -= 10 * mm
        ly = _paragraphs(c, lx, ly, lines, 45 * mm, 7.2, colors.white, bullet=title == _label("additional_education", lang), min_y=13 * mm) - 10 * mm

    rx = 82 * mm
    ry = PAGE_H - 98 * mm
    for title, lines, bullet in [
        (_label("profile", lang), [_profile_text(data, lang)], False),
        (_label("experience", lang), _compact_lines(data.experience), True),
        (_label("achievements", lang), data.achievements, True),
        (_label("additional_info", lang), data.additional_info, True),
    ]:
        _txt(c, rx, ry, title, 13.5, "CVBold", navy)
        c.setStrokeColor(navy)
        c.line(rx, ry - 3 * mm, 195 * mm, ry - 3 * mm)
        ry -= 9 * mm
        ry = _paragraphs(c, rx, ry, lines, 104 * mm, 8, colors.black, bullet=bullet, min_y=14 * mm) - 8 * mm


def _register_fonts() -> None:
    candidates = [
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "CVRegular"),
        ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "CVBold"),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", "CVRegular"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "CVRegular"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "CVBold"),
    ]
    for path, name in candidates:
        if Path(path).exists() and name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, path))
    if "CVRegular" not in pdfmetrics.getRegisteredFontNames():
        return
    if "CVBold" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("CVBold", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"))


def _circle_photo(photo_path: str | None, dst: Path) -> Path | None:
    if not photo_path or not Path(photo_path).exists():
        return None
    img = Image.open(photo_path).convert("RGB")
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


def _name_parts(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _label(key: str, lang: str) -> str:
    return FIELD_LABELS[key][lang]


def _profile_text(data: CVData, lang: str) -> str:
    skills = ", ".join(data.professional_skills[:4])
    if lang == "kk":
        return f"{data.degree_program} бағыты бойынша дамып жүрген кандидат. Негізгі дағдылары: {skills}. Жаңа технологияларды тез меңгереді және командалық жұмысқа бейім."
    if lang == "en":
        return f"Candidate focused on {data.degree_program}. Key skills: {skills}. Fast learner with strong teamwork and practical project experience."
    return f"Кандидат по направлению {data.degree_program}. Ключевые навыки: {skills}. Быстро изучает новые технологии и умеет работать в команде."


def _contacts(data: CVData, lang: str) -> list[str]:
    return [
        f"{_label('phone', lang)}: {data.phone}",
        f"{_label('email', lang)}: {data.email}",
        f"{_label('city', lang)}: {data.city}",
    ]


def _facts(data: CVData, lang: str) -> list[str]:
    return [
        f"{_label('birth_date', lang)}: {data.birth_date}",
        f"{_label('marital_status', lang)}: {data.marital_status}",
    ]


def _education_items(data: CVData) -> list[tuple[str, str, str]]:
    lines = _compact_lines(data.education_details or data.current_education)
    if not lines:
        return []
    first = lines[0]
    rest = " ".join(lines[1:]) if len(lines) > 1 else data.current_education
    items = [("2022 - 2026", first, rest)]
    extra = _compact_lines(data.additional_education)
    if extra:
        items.append(("2024 - 2026", extra[0], " ".join(extra[1:])))
    return items[:3]


def _experience_items(data: CVData) -> list[tuple[str, str, str]]:
    lines = _compact_lines(data.experience)
    if not lines:
        return []
    if len(lines) == 1:
        return [("2026", lines[0], "")]
    if len(lines) == 2:
        return [(lines[1], lines[0], "")]
    return [(lines[1], lines[0], " ".join(lines[2:]))]


def _dated_items(lines: list[str]) -> list[tuple[str, str, str]]:
    items = []
    for index, line in enumerate(lines[:3], start=1):
        items.append((f"#{index}", line, ""))
    return items


def _compact_lines(text: str) -> list[str]:
    return [line.strip(" -•\t") for line in text.splitlines() if line.strip(" -•\t")]


def _nonempty(items: list[str], fallback: str) -> list[str]:
    if items:
        return items
    return _compact_lines(fallback)


def _txt(c: canvas.Canvas, x: float, y: float, text: str, size: float, font: str, color) -> None:
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, _clean(text))


def _clean(text: str) -> str:
    return " ".join(str(text).split())


def _wrap(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = _clean(text).split()
    if not words:
        return []
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if pdfmetrics.stringWidth(candidate, font, size) <= max_width:
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
    lines: Iterable[str],
    width: float,
    size: float,
    color,
    bullet: bool = False,
    stars: bool = False,
    min_y: float = 10 * mm,
) -> float:
    font = "CVRegular"
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        wrapped = _wrap(line, font, size, width - (4 * mm if bullet else 0))
        for index, part in enumerate(wrapped):
            if y < min_y:
                return y
            prefix = "• " if bullet and index == 0 else ""
            offset = 4 * mm if bullet and index > 0 else 0
            c.drawString(x + offset, y, prefix + part)
            y -= size + 2.2
        if stars and y >= min_y:
            c.setFillColor(colors.HexColor("#b57d52"))
            c.drawString(x + 37 * mm, y + size + 2.2, "■■■■□")
            c.setFillColor(color)
        y -= 1.2
    return y


def _simple_section(c: canvas.Canvas, x: float, y: float, title: str, lines: list[str], width: float, accent, text) -> float:
    if not lines or y < 18 * mm:
        return y
    _txt(c, x, y, title, 10.5, "CVBold", accent)
    return _paragraphs(c, x, y - 6.5 * mm, lines[:5], width, 7.3, text, bullet=True, min_y=12 * mm)


def _timeline_section(c: canvas.Canvas, x: float, y: float, title: str, items: list[tuple[str, str, str]], accent, text) -> float:
    if not items:
        return y
    c.setFillColor(accent)
    c.circle(x + 1 * mm, y + 1 * mm, 3 * mm, stroke=0, fill=1)
    _txt(c, x + 10 * mm, y, title, 12.5, "CVBold", text)
    y -= 10 * mm
    c.setStrokeColor(colors.HexColor("#d2d2d2"))
    c.line(x + 1 * mm, y + 4 * mm, x + 1 * mm, max(18 * mm, y - 44 * mm))
    for date, heading, detail in items[:3]:
        if y < 30 * mm:
            return y
        c.setFillColor(accent)
        c.circle(x + 1 * mm, y + 1 * mm, 2.4 * mm, stroke=0, fill=1)
        _txt(c, x + 10 * mm, y, f"({date})", 9.5, "CVBold", text)
        _txt(c, x + 10 * mm, y - 5.5 * mm, heading.upper(), 7.7, "CVBold", text)
        y = _paragraphs(c, x + 10 * mm, y - 11 * mm, [detail], 82 * mm, 7, text, min_y=18 * mm)
        y -= 8 * mm
    return y


def _brown_section(c: canvas.Canvas, x: float, y: float, title: str, items: list[tuple[str, str, str]], accent) -> float:
    if not items or y < 25 * mm:
        return y
    c.setFillColor(accent)
    c.circle(x, y + 1 * mm, 5 * mm, stroke=0, fill=1)
    _txt(c, x + 9 * mm, y, title, 15, "CVBold", colors.black)
    y -= 12 * mm
    c.setStrokeColor(colors.HexColor("#d0d0d0"))
    c.line(x + 2 * mm, y + 6 * mm, x + 2 * mm, max(22 * mm, y - 44 * mm))
    for date, role, place in items[:3]:
        if y < 25 * mm:
            return y
        c.setFillColor(accent)
        c.circle(x + 2 * mm, y + 1 * mm, 2.2 * mm, stroke=0, fill=1)
        _txt(c, x + 12 * mm, y, date, 7.6, "CVBold", colors.black)
        _txt(c, x + 34 * mm, y, role, 8.1, "CVBold", colors.black)
        y = _paragraphs(c, x + 34 * mm, y - 6 * mm, [place], 64 * mm, 6.7, colors.black, min_y=18 * mm)
        y -= 8 * mm
    return y


def _neon_card(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    lines: list[str],
    accent,
    fill,
    text,
    toggles: bool = False,
    chips: bool = False,
) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 4 * mm, stroke=0, fill=1)
    _txt(c, x + 7 * mm, y + h - 11 * mm, title.upper(), 10, "CVBold", accent)
    if chips:
        cx, cy = x + 7 * mm, y + h - 20 * mm
        for item in lines:
            tw = min(40 * mm, max(18 * mm, pdfmetrics.stringWidth(item, "CVRegular", 5.6) + 5 * mm))
            c.setFillColor(colors.HexColor("#4b4f5b"))
            c.roundRect(cx, cy, tw, 5 * mm, 2.5 * mm, stroke=0, fill=1)
            _txt(c, cx + 2 * mm, cy + 1.4 * mm, item, 5.6, "CVRegular", colors.white)
            cx += tw + 2 * mm
            if cx > x + w - 35 * mm:
                cx, cy = x + 7 * mm, cy - 7 * mm
        return
    yy = y + h - 20 * mm
    for line in lines[:5]:
        if toggles:
            c.setFillColor(accent)
            c.roundRect(x + 7 * mm, yy - 0.5 * mm, 6 * mm, 3 * mm, 1.5 * mm, stroke=0, fill=1)
            tx = x + 17 * mm
            bullet = False
        else:
            tx = x + 7 * mm
            bullet = len(lines) > 1
        yy = _paragraphs(c, tx, yy, [line], w - 18 * mm, 6.2, text, bullet=bullet, min_y=y + 3 * mm)


def _neon_skill_grid(c: canvas.Canvas, x: float, y: float, skills: list[str], accent, fill, text) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, 52 * mm, 50 * mm, 4 * mm, stroke=0, fill=1)
    labels = skills[:4] or ["Python", "SQL", "Web", "Office"]
    for index, label in enumerate(labels):
        cx = x + (14 if index % 2 == 0 else 38) * mm
        cy = y + (35 if index < 2 else 16) * mm
        abbr = _clean(label)[:2].title()
        c.setStrokeColor(accent)
        c.setLineWidth(2)
        c.circle(cx, cy, 7 * mm, stroke=1, fill=0)
        _txt(c, cx - 3.5 * mm, cy - 2 * mm, abbr, 9, "CVBold", colors.white)
        _txt(c, cx - 8 * mm, cy - 11 * mm, _clean(label)[:14], 5, "CVRegular", text)


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
