from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.dml.color import RGBColor
from pptx.oxml.xmlchemy import OxmlElement
from extractor import extract_bible_verses

# ==============================
# 가독성 중심 상수
# ==============================
# 텍스트박스 배경: 딥 올리브(순블랙 대신) + 옅은 투명도
SHADE_COLOR       = RGBColor(25, 30, 20)
SHADE_ALPHA       = 0.12        # 0.10~0.16에서 조정 (숫자↑ = 더 옅음)

# 흰 텍스트 + 윤곽선(프로젝터용 대비)
OUTLINE_HEX       = "2A2A2A"    # 짙은 회색 (더 부드럽게는 "303030")
OUTLINE_PT        = 0.9         # 0.8~1.1 권장

# 글꼴/크기/줄간격(요청 유지)
TITLE_SIZE_PT     = 36
BODY_SIZE_PT      = 50
TITLE_ALIGN       = PP_ALIGN.LEFT
BODY_ALIGN        = PP_ALIGN.JUSTIFY
BODY_LINE_SPACING = 1.15

# 레이아웃(여백)
OUTER_MARGIN_IN   = 1.3
INNER_SIDE_GAP_IN = 0.25
TITLE_TOP_IN      = 1.0
GAP_TITLE_BODY_IN = 0.25        # 제목과 본문 사이 간격(단락 간격처럼 사용)

# 텍스트박스 내부 패딩(배경 띠 과하지 않게)
MARGIN_LEFT_IN    = 0.12
MARGIN_RIGHT_IN   = 0.12
MARGIN_TOP_IN     = 0.10
MARGIN_BOTTOM_IN  = 0.10

FONT_NAME         = 'Apple SD Gothic Neo'  # 환경에 맞게 변경 가능

# ==============================
# 유틸: 텍스트 윤곽선(Outline)
# ==============================
def apply_text_outline(run, color_hex="2A2A2A", width_pt=0.9):
    r = run._r
    rPr = r.get_or_add_rPr()

    ln = OxmlElement('a:ln')
    ln.set('w', str(int(width_pt * 12700)))  # 1pt ≈ 12700 EMU

    solidFill = OxmlElement('a:solidFill')
    srgbClr = OxmlElement('a:srgbClr')
    srgbClr.set('val', color_hex)
    solidFill.append(srgbClr)
    ln.append(solidFill)

    rPr.append(ln)

# ==============================
# 핵심: "한 개 텍스트박스"에 제목+본문 단락을 넣고, 자동 높이로
# ==============================
def add_one_box_title_and_body(slide, title_text, body_text, left, top, width):
    # 초기 높이는 아주 작게 → 자동으로 텍스트만큼 커짐
    tb = slide.shapes.add_textbox(left, top, width, Inches(0.1))
    tf = tb.text_frame
    tf.word_wrap = True

    # 내부 패딩
    tf.margin_left   = Inches(MARGIN_LEFT_IN)
    tf.margin_right  = Inches(MARGIN_RIGHT_IN)
    tf.margin_top    = Inches(MARGIN_TOP_IN)
    tf.margin_bottom = Inches(MARGIN_BOTTOM_IN)

    # ■ 제목 단락
    p_title = tf.paragraphs[0]
    p_title.alignment = TITLE_ALIGN
    run_title = p_title.add_run()
    run_title.text = title_text
    run_title.font.size = Pt(TITLE_SIZE_PT)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(255, 255, 255)
    run_title.font.name = FONT_NAME
    apply_text_outline(run_title, color_hex=OUTLINE_HEX, width_pt=OUTLINE_PT)

    # 제목과 본문 사이 약간의 여백(줄바꿈)
    p_gap = tf.add_paragraph()
    p_gap.space_before = 0
    p_gap.space_after  = 0
    p_gap.add_run().text = ""  # 빈 줄
    # 필요시 GAP_TITLE_BODY_IN 값을 더 키우려면 여기서 빈 줄을 2개로

    # ■ 본문 단락
    p_body = tf.add_paragraph()
    p_body.alignment = BODY_ALIGN
    p_body.line_spacing = BODY_LINE_SPACING
    run_body = p_body.add_run()
    run_body.text = body_text
    run_body.font.size = Pt(BODY_SIZE_PT)
    run_body.font.bold = True
    run_body.font.color.rgb = RGBColor(255, 255, 255)
    run_body.font.name = FONT_NAME
    apply_text_outline(run_body, color_hex=OUTLINE_HEX, width_pt=OUTLINE_PT)

    # 텍스트박스 배경(아주 옅게) — 도형 1개라 경계선/검은 줄 없음
    fill = tb.fill
    fill.solid()
    fill.fore_color.rgb = SHADE_COLOR
    fill.transparency = SHADE_ALPHA
    tb.line.fill.background()  # 도형 테두리선 제거

    # 자동으로 텍스트에 맞춰 '도형 높이' 조절
    tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT

    return tb

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

    # 공통 좌우 폭
    margin = Inches(OUTER_MARGIN_IN)
    left   = margin + Inches(INNER_SIDE_GAP_IN)
    right  = margin + Inches(INNER_SIDE_GAP_IN)
    box_w  = prs.slide_width - (left + right)

    for verse in verses:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # 배경 이미지
        slide.shapes.add_picture(
            background_image, 0, 0,
            width=prs.slide_width, height=prs.slide_height
        )

        # 한 개 텍스트박스(제목+본문) — 경계선/이중 박스가 아예 없다
        add_one_box_title_and_body(
            slide=slide,
            title_text=verse["title"],
            body_text=verse["text"],
            left=left,
            top=Inches(TITLE_TOP_IN),
            width=box_w
        )

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
