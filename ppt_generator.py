from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE  # ✅ 자동 높이
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

# 텍스트박스 안쪽 패딩(배경이 ‘띠’처럼 보이도록, 과하지 않게)
TITLE_MARGINS_IN = (0.10, 0.10, 0.06, 0.06)  # left, right, top, bottom
BODY_MARGINS_IN  = (0.12, 0.12, 0.08, 0.08)

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

def add_autofit_textbox_with_shade_and_outline(
    slide, text, left, top, width,
    font_size_pt=48, bold=True, align=PP_ALIGN.LEFT,
    shade_color=SHADE_COLOR, shade_alpha=0.12,
    margins_in=(0.10, 0.10, 0.06, 0.06),
    font_name='Apple SD Gothic Neo'
):
    """
    텍스트박스 1개에:
    - 박스 배경(아주 옅은 색) + 흰 글자 + 윤곽선 적용
    - ✅ 텍스트 양에 따라 '도형 높이'를 자동으로 늘림 (SHAPE_TO_FIT_TEXT)
      → 수동 분할/복붙 시에도 텍스트와 배경이 항상 일체로 움직이고, 크기도 함께 조절됨
    """
    # 초기 높이는 아주 작게(예: 0.1in) 줘도 됨. 자동으로 텍스트만큼 커짐.
    box = slide.shapes.add_textbox(left, top, width, Inches(0.1))
    frame = box.text_frame
    frame.word_wrap = True

    # 내부 패딩
    m_left, m_right, m_top, m_bottom = margins_in
    frame.margin_left   = Inches(m_left)
    frame.margin_right  = Inches(m_right)
    frame.margin_top    = Inches(m_top)
    frame.margin_bottom = Inches(m_bottom)

    # 텍스트/단락
    p = frame.paragraphs[0]
    p.alignment = align
    p.line_spacing = LINE_SPACING
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size_pt)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
    run.font.name = font_name

    # 윤곽선 적용
    apply_text_outline(run, color_hex=OUTLINE_HEX, width_pt=OUTLINE_PT)

    # 텍스트박스 배경(아주 옅게)
    fill = box.fill
    fill.solid()
    fill.fore_color.rgb = shade_color
    fill.transparency = shade_alpha
    box.line.fill.background()  # 테두리선 제거

    # ✅ 핵심: 텍스트에 맞춰 '도형 높이'가 자동으로 늘어나게
    frame.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

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

        # ───────── 제목 (자동 높이) ─────────
        title_top = Inches(1.0)
        add_autofit_textbox_with_shade_and_outline(
            slide,
            text=verse["title"],
            left=left, top=title_top, width=box_w,
            font_size_pt=TITLE_SIZE_PT, bold=True, align=PP_ALIGN.LEFT,
            shade_color=SHADE_COLOR, shade_alpha=TITLE_SHADE_ALPHA,
            margins_in=TITLE_MARGINS_IN
        )

        # ───────── 본문 (자동 높이) ─────────
        body_top = title_top + Inches(0.70)
        add_autofit_textbox_with_shade_and_outline(
            slide,
            text=verse["text"],
            left=left, top=body_top, width=box_w,
            font_size_pt=BODY_SIZE_PT, bold=True, align=PP_ALIGN.JUSTIFY,
            shade_color=SHADE_COLOR, shade_alpha=BODY_SHADE_ALPHA,
            margins_in=BODY_MARGINS_IN
        )

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
