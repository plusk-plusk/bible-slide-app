from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from extractor import extract_bible_verses

# ====== 쉬운 튜닝용 상수 ======
# 은은한 음영 색상: 어두운 카키/올리브 톤 (가을 배경과 자연스러운 조화)
SHADE_COLOR = RGBColor(25, 30, 20)

# 투명도(0.0=불투명, 1.0=완전투명) — 너무 어두우면 값을 "올리면" 옅어짐
TITLE_SHADE_ALPHA = 0.14  # 권장 범위: 0.12 ~ 0.16
BODY_SHADE_ALPHA  = 0.12  # 권장 범위: 0.10 ~ 0.16

# 텍스트 박스 높이(“띠”만 보이도록 낮게)
TITLE_BOX_HEIGHT_IN = 0.65
BODY_BOX_HEIGHT_IN  = 2.60

# 좌우를 살짝 좁혀 전체를 덮지 않게
INNER_SIDE_GAP_IN = 0.25

# 내부 패딩(글자가 박스에 붙지 않게)
TITLE_MARGINS_IN = (0.10, 0.10, 0.06, 0.06)  # left, right, top, bottom
BODY_MARGINS_IN  = (0.12, 0.12, 0.08, 0.08)

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

        # 배경 전체
        slide.shapes.add_picture(
            background_image, 0, 0,
            width=prs.slide_width, height=prs.slide_height
        )

        # 여백/영역
        outer_margin = Inches(1.3)
        left  = outer_margin + Inches(INNER_SIDE_GAP_IN)
        right = outer_margin + Inches(INNER_SIDE_GAP_IN)
        box_width = prs.slide_width - (left + right)

        # ================================
        # ① 제목 (은은한 띠 + 흰색 Bold)
        # ================================
        title_top = Inches(1.0)
        title_h   = Inches(TITLE_BOX_HEIGHT_IN)

        title_box = slide.shapes.add_textbox(left, title_top, box_width, title_h)
        tframe = title_box.text_frame
        tframe.word_wrap = True

        # 내부 패딩
        t_left, t_right, t_top, t_bottom = TITLE_MARGINS_IN
        tframe.margin_left   = Inches(t_left)
        tframe.margin_right  = Inches(t_right)
        tframe.margin_top    = Inches(t_top)
        tframe.margin_bottom = Inches(t_bottom)

        # 텍스트 박스 배경을 아주 옅게(자연스러운 카키/올리브)
        tfill = title_box.fill
        tfill.solid()
        tfill.fore_color.rgb = SHADE_COLOR
        tfill.transparency   = TITLE_SHADE_ALPHA
        title_box.line.fill.background()  # 테두리 제거

        p_title = tframe.paragraphs[0]
        p_title.alignment = PP_ALIGN.LEFT
        run_title = p_title.add_run()
        run_title.text = verse["title"]
        run_title.font.size = Pt(36)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
        run_title.font.name = 'Apple SD Gothic Neo'

        # 제목-본문 간 간격
        body_top = title_top + Inches(0.70)

        # ================================
        # ② 본문 (은은한 띠 + 흰색 Bold)
        # ================================
        body_h = Inches(BODY_BOX_HEIGHT_IN)

        body_box = slide.shapes.add_textbox(left, body_top, box_width, body_h)
        bframe = body_box.text_frame
        bframe.word_wrap = True

        # 내부 패딩
        b_left, b_right, b_top, b_bottom = BODY_MARGINS_IN
        bframe.margin_left   = Inches(b_left)
        bframe.margin_right  = Inches(b_right)
        bframe.margin_top    = Inches(b_top)
        bframe.margin_bottom = Inches(b_bottom)

        # 본문 박스 배경 (제목보다도 한 단계 더 옅게)
        bfill = body_box.fill
        bfill.solid()
        bfill.fore_color.rgb = SHADE_COLOR
        bfill.transparency   = BODY_SHADE_ALPHA
        body_box.line.fill.background()

        p_body = bframe.paragraphs[0]
        p_body.alignment = PP_ALIGN.JUSTIFY
        p_body.line_spacing = 1.15  # 살짝만 줄여 박스 높이 최적화
        run_body = p_body.add_run()
        run_body.text = verse["text"]
        run_body.font.size = Pt(50)  # 너무 커서 띠가 넓어지지 않게 소폭 다운
        run_body.font.bold = True
        run_body.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
        run_body.font.name = 'Apple SD Gothic Neo'

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
