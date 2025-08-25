from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from extractor import extract_bible_verses

# ==============================
# 가독성 중심 튜닝 상수
# ==============================
# 텍스트박스 자체의 아주 옅은 배경(배경 이미지와 조화되는 딥 올리브)
SHADE_COLOR = RGBColor(25, 30, 20)  # 순수 블랙 대신 차분한 톤
TITLE_SHADE_ALPHA = 0.14            # 0.12~0.16 권장 (숫자↑ = 더 옅음)
BODY_SHADE_ALPHA  = 0.12            # 0.10~0.16 권장

# 윤곽선(Outline) — 프로젝터 환경에서 시인성 ↑
OUTLINE_HEX = "2A2A2A"              # "222222"보다 한 톤 부드러움
OUTLINE_PT  = 0.9                   # 0.8~1.1 사이 조정

# 글자 크기/줄 간격(요청대로 유지)
TITLE_SIZE_PT = 36
BODY_SIZE_PT  = 50
LINE_SPACING  = 1.15

# 레이아웃(여백)
OUTER_MARGIN_IN   = 1.3
INNER_SIDE_GAP_IN = 0.25

def apply_text_outline(run, color_hex="2A2A2A", width_pt=0.9):
    """
    텍스트 run에 윤곽선(Outline) 추가.
    width_pt: pt 단위(1pt ≈ 12700 EMU)
    """
    r = run._r
    rPr = r.get_or_add_rPr()

    ln = OxmlElement('a:ln')
    ln.set('w', str(int(width_pt * 12700)))

    solidFill = OxmlElement('a:solidFill')
    srgbClr = OxmlElement('a:srgbClr')
    srgbClr.set('val', color_hex)
    solidFill.append(srgbClr)
    ln.append(solidFill)

    rPr.append(ln)

def add_textbox_with_shade_and_outline(
    slide, text, left, top, width, height,
    font_size_pt=48, bold=True, align=PP_ALIGN.LEFT,
    shade_color=SHADE_COLOR, shade_alpha=0.12,
    font_name='Apple SD Gothic Neo'
):
    """
    텍스트박스 1개에:
    - 박스 배경(아주 옅은 색) + 흰 글자 + 윤곽선 적용
    → 텍스트와 배경이 일체로 움직여 수동 분할/복붙 시에도 안전
    """
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True

    # 텍스트박스 배경(아주 옅게)
    fill = box.fill
    fill.solid()
    fill.fore_color.rgb = shade_color
    fill.transparency = shade_alpha
    box.line.fill.background()  # 테두리선 제거

    # 단락/텍스트
    p = frame.paragraphs[0]
    p.alignment = align
    p.line_spacing = LINE_SPACING
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size_pt)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
    run.font.name = font_name

    # 윤곽선 적용(프로젝터 가독성 ↑)
    apply_text_outline(run, color_hex=OUTLINE_HEX, width_pt=OUTLINE_PT)

    return box

def make_bible_ppt(json_path, ref_path, output_path, background_image):
    prs = Presentation()
    prs.slide_width  = Inches(13.33)  # 16:9
    prs.slide_height = Inches(7.5)

    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # 배경 이미지 전체 채우기
        slide.shapes.add_picture(
            background_image, 0, 0,
            width=prs.slide_width, height=prs.slide_height
        )

        # 좌우 여백/폭
        margin = Inches(OUTER_MARGIN_IN)
        left   = margin + Inches(INNER_SIDE_GAP_IN)
        right  = margin + Inches(INNER_SIDE_GAP_IN)
        box_w  = prs.slide_width - (left + right)

        # ───────── 제목 ─────────
        title_top = Inches(1.0)
        title_h   = Inches(0.9)  # 필요시 0.75~1.0 조정
        add_textbox_with_shade_and_outline(
            slide,
            text=verse["title"],
            left=left, top=title_top, width=box_w, height=title_h,
            font_size_pt=TITLE_SIZE_PT, bold=True, align=PP_ALIGN.LEFT,
            shade_color=SHADE_COLOR, shade_alpha=TITLE_SHADE_ALPHA
        )

        # ───────── 본문 ─────────
        body_top = title_top + Inches(0.70)
        body_h   = Inches(2.6)   # 필요시 2.3~3.0 조정(줄 수에 맞게)
        add_textbox_with_shade_and_outline(
            slide,
            text=verse["text"],
            left=left, top=body_top, width=box_w, height=body_h,
            font_size_pt=BODY_SIZE_PT, bold=True, align=PP_ALIGN.JUSTIFY,
            shade_color=SHADE_COLOR, shade_alpha=BODY_SHADE_ALPHA
        )

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
