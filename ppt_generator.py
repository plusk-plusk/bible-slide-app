from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE   # ✅ 음영 패널(사각형) 추가용
from extractor import extract_bible_verses

# ✅ 반투명 음영 패널 유틸 함수
def add_shaded_panel(slide, left, top, width, height,
                     color=RGBColor(0, 0, 0), alpha=0.35, radius=True):
    """
    텍스트 뒤에 까는 반투명 음영 패널(사각형).
    alpha: 0.0=불투명, 1.0=완전투명 (보통 0.25~0.45 권장)
    radius: 둥근 모서리 사용 여부
    """
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    panel = slide.shapes.add_shape(shape_type, left, top, width, height)
    fill = panel.fill
    fill.solid()
    fill.fore_color.rgb = color
    fill.transparency = alpha
    panel.line.fill.background()  # 테두리 제거
    return panel

def make_bible_ppt(json_path, ref_path, output_path, background_image):
    prs = Presentation()
    prs.slide_width  = Inches(13.33)   # 16:9
    prs.slide_height = Inches(7.5)

    verses = extract_bible_verses(json_path, ref_path)

    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # ✅ 배경 이미지 전체 깔기
        slide.shapes.add_picture(
            background_image, 0, 0,
            width=prs.slide_width, height=prs.slide_height
        )

        # ✅ 여백 및 텍스트 영역 계산
        margin_h  = Inches(1.3)
        box_width = prs.slide_width - 2 * margin_h

        # =============================
        # ① 제목 영역: 음영 패널 → 텍스트
        # =============================
        title_top = Inches(1.0)

        # ✅ 제목 음영 패널(먼저 그리기)
        add_shaded_panel(
            slide,
            left=margin_h, top=title_top,
            width=box_width, height=Inches(0.9),
            color=RGBColor(0, 0, 0),   # 검정 패널
            alpha=0.35,                # 진하면 0.40~0.45, 옅게 0.25~0.30
            radius=True
        )

        # ✅ 제목 텍스트(흰색)
        title_box = slide.shapes.add_textbox(margin_h, title_top, box_width, Inches(0.9))
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        p_title = title_frame.paragraphs[0]
        p_title.alignment = PP_ALIGN.LEFT
        run_title = p_title.add_run()
        run_title.text = verse["title"]
        run_title.font.size = Pt(36)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(255, 255, 255)  # ✅ 흰색
        run_title.font.name = 'Apple SD Gothic Neo'

        # =============================
        # ② 본문 영역: 음영 패널 → 텍스트
        # =============================
        body_top = title_top + Inches(0.85)

        # ✅ 본문 음영 패널(먼저 그리기)
        add_shaded_panel(
            slide,
            left=margin_h, top=body_top,
            width=box_width, height=Inches(3.6),
            color=RGBColor(0, 0, 0),
            alpha=0.30,                # 본문은 약간 더 옅게
            radius=True
        )

        # ✅ 본문 텍스트(흰색)
        body_box = slide.shapes.add_textbox(margin_h, body_top, box_width, Inches(3.6))
        body_frame = body_box.text_frame
        body_frame.word_wrap = True
        p_body = body_frame.paragraphs[0]
        p_body.alignment = PP_ALIGN.JUSTIFY
        p_body.line_spacing = 1.2
        run_body = p_body.add_run()
        run_body.text = verse["text"]
        run_body.font.size = Pt(53)
        run_body.font.bold = True
        run_body.font.color.rgb = RGBColor(255, 255, 255)  # ✅ 흰색
        run_body.font.name = 'Apple SD Gothic Neo'

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
