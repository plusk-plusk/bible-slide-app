from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from extractor import extract_bible_verses
import textwrap
import math

# ==============================
# 가독성 & 페이지네이션 상수
# ==============================
# 줄당 대략 글자 수(한글 기준) — 필요시 20~26에서 미세 조정
CHARS_PER_LINE   = 22
# 한 슬라이드에 허용할 본문 최대 줄수
MAX_BODY_LINES   = 5

# 텍스트박스 배경(아주 옅은 딥 올리브)
SHADE_COLOR      = RGBColor(25, 30, 20)
TITLE_SHADE_ALPHA= 0.14
BODY_SHADE_ALPHA = 0.12

# 윤곽선(Outline) — 프로젝터 환경 시인성 ↑
OUTLINE_HEX      = "2A2A2A"
OUTLINE_PT       = 0.9

# 폰트 크기/줄간격(요청대로 유지)
TITLE_SIZE_PT    = 36
BODY_SIZE_PT     = 50
LINE_SPACING     = 1.15

# 레이아웃(여백)
OUTER_MARGIN_IN   = 1.3
INNER_SIDE_GAP_IN = 0.25

# ==============================
# 유틸: 텍스트 윤곽선(Outline)
# ==============================
def apply_text_outline(run, color_hex="2A2A2A", width_pt=0.9):
    r = run._r
    rPr = r.get_or_add_rPr()
    ln = OxmlElement('a:ln')
    ln.set('w', str(int(width_pt * 12700)))  # 1pt ≈ 12700
    solidFill = OxmlElement('a:solidFill')
    srgbClr = OxmlElement('a:srgbClr')
    srgbClr.set('val', color_hex)
    solidFill.append(srgbClr)
    ln.append(solidFill)
    rPr.append(ln)

# ==============================
# 유틸: 텍스트 줄 나누기(래핑)
# ==============================
def wrap_text_to_lines(text: str, width_chars: int):
    """
    text를 대략 width_chars 길이 기준으로 줄바꿈하여 줄 리스트를 반환.
    - 기존 줄바꿈(\n)은 우선 존중
    - 긴 줄은 textwrap으로 추가 감싸기
    """
    lines = []
    for block in text.splitlines():
        block = block.strip()
        if not block:
            continue
        wrapped = textwrap.wrap(
            block,
            width=width_chars,
            break_long_words=True,
            break_on_hyphens=False
        )
        if not wrapped:
            continue
        lines.extend(wrapped)
    return lines

# ==============================
# 유틸: 텍스트박스(배경+윤곽선 일체)
# ==============================
def add_textbox_with_shade_and_outline(
    slide, text, left, top, width, height,
    font_size_pt=48, bold=True, align=PP_ALIGN.LEFT,
    shade_color=SHADE_COLOR, shade_alpha=0.12,
    font_name='Apple SD Gothic Neo'
):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True

    # 박스 배경(아주 옅게)
    fill = box.fill
    fill.solid()
    fill.fore_color.rgb = shade_color
    fill.transparency = shade_alpha
    box.line.fill.background()

    p = frame.paragraphs[0]
    p.alignment = align
    p.line_spacing = LINE_SPACING
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size_pt)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
    run.font.name = font_name
    apply_text_outline(run, color_hex=OUTLINE_HEX, width_pt=OUTLINE_PT)
    return box

# ==============================
# 메인
# ==============================
def make_bible_ppt(json_path, ref_path, output_path, background_image):
    prs = Presentation()
    prs.slide_width  = Inches(13.33)  # 16:9
    prs.slide_height = Inches(7.5)

    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    # 공통 레이아웃 계산
    margin = Inches(OUTER_MARGIN_IN)
    left   = margin + Inches(INNER_SIDE_GAP_IN)
    right  = margin + Inches(INNER_SIDE_GAP_IN)
    box_w  = prs.slide_width - (left + right)

    for verse in verses:
        # 1) 본문을 줄 배열로 변환
        body_lines = wrap_text_to_lines(verse["text"], CHARS_PER_LINE)
        # 2) 필요한 슬라이드 수
        pages = max(1, math.ceil(len(body_lines) / MAX_BODY_LINES))

        for page_idx in range(pages):
            # 슬라이드 생성 & 배경
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.shapes.add_picture(
                background_image, 0, 0,
                width=prs.slide_width, height=prs.slide_height
            )

            # 제목 텍스트 (페이지 표기 붙이기: 1/3, 2/3 ...)
            title_text = verse["title"]
            if pages > 1:
                title_text = f"{title_text}  ({page_idx+1}/{pages})"

            title_top = Inches(1.0)
            title_h   = Inches(0.9)
            add_textbox_with_shade_and_outline(
                slide,
                text=title_text,
                left=left, top=title_top, width=box_w, height=title_h,
                font_size_pt=TITLE_SIZE_PT, bold=True, align=PP_ALIGN.LEFT,
                shade_color=SHADE_COLOR, shade_alpha=TITLE_SHADE_ALPHA
            )

            # 이번 페이지에 들어갈 본문 줄들
            start = page_idx * MAX_BODY_LINES
            end   = start + MAX_BODY_LINES
            lines_this_page = body_lines[start:end]
            body_text = "\n".join(lines_this_page) if lines_this_page else ""

            body_top = title_top + Inches(0.70)
            # 높이는 5줄 기준으로 넉넉히 — 텍스트박스 1개(배경 포함)이므로 항상 일체 이동
            # (줄이 5줄 미만이면 남는 공간이 있어도 문제 없음)
            body_h   = Inches(2.6)

            add_textbox_with_shade_and_outline(
                slide,
                text=body_text,
                left=left, top=body_top, width=box_w, height=body_h,
                font_size_pt=BODY_SIZE_PT, bold=True, align=PP_ALIGN.JUSTIFY,
                shade_color=SHADE_COLOR, shade_alpha=BODY_SHADE_ALPHA
            )

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
