from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from extractor import extract_bible_verses

# ====== 튜닝용 상수 ======
SHADOW_COLOR = RGBColor(22, 24, 20)   # 검정보다 부드러운 짙은 올리브
SHADOW_OFFSET_IN = 0.02               # 매우 작게 (0.015~0.03 권장 범위)

TITLE_SIZE_PT = 36
BODY_SIZE_PT  = 50                    # 필요시 48~52 사이에서 조정
LINE_SPACING  = 1.15                  # 본문 줄간격 (1.15~1.25 추천)

# 좌우 여백/박스 폭(텍스트만 깔끔히 보이도록)
OUTER_MARGIN_IN   = 1.3
INNER_SIDE_GAP_IN = 0.25

def add_text_with_micro_shadow(slide, text, left, top, width, height,
                               font_size_pt=48, bold=True, align=PP_ALIGN.LEFT,
                               font_name='Apple SD Gothic Neo'):
    """
    반투명 패널 없이, '초미세' 그림자 텍스트 한 겹 + 흰 텍스트 한 겹으로 가독성 확보.
    그림자 오프셋을 매우 작게 해서 '검은 윤곽선 느낌'만 살짝 남기는 게 핵심.
    """
    # 1) 그림자(뒤쪽) — 짙은 올리브, 매우 작은 오프셋
    s_off = Inches(SHADOW_OFFSET_IN)
    shadow_box = slide.shapes.add_textbox(left + s_off, top + s_off, width, height)
    sframe = shadow_box.text_frame
    sframe.word_wrap = True
    p = sframe.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size_pt)
    run.font.bold = bold
    run.font.color.rgb = SHADOW_COLOR
    run.font.name = font_name

    # 2) 실제 텍스트(앞쪽) — 흰색
    main_box = slide.shapes.add_textbox(left, top, width, height)
    mframe = main_box.text_frame
    mframe.word_wrap = True
    p2 = mframe.paragraphs[0]
    p2.alignment = align
    run2 = p2.add_run()
    run2.text = text
    run2.font.size = Pt(font_size_pt)
    run2.font.bold = bold
    run2.font.color.rgb = RGBColor(255, 255, 255)  # 흰색
    run2.font.name = font_name

    return main_box, shadow_box

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

        # 레이아웃 계산
        margin = Inches(OUTER_MARGIN_IN)
        left   = margin + Inches(INNER_SIDE_GAP_IN)
        right  = margin + Inches(INNER_SIDE_GAP_IN)
        box_w  = prs.slide_width - (left + right)

        # ----- 제목 -----
        title_top = Inches(1.0)
        # 텍스트만 넣고(패널/배경 없음) 초미세 그림자만
        add_text_with_micro_shadow(
            slide,
            text=verse["title"],
            left=left, top=title_top,
            width=box_w, height=Inches(0.9),
            font_size_pt=TITLE_SIZE_PT,
            bold=True, align=PP_ALIGN.LEFT
        )

        # ----- 본문 -----
        body_top = title_top + Inches(0.70)
        body_box_h = Inches(2.6)   # 도형 높이는 단순 캔버스; 텍스트 줄 수에 맞게 필요시 2.4~3.0 조정

        main_box, shadow_box = add_text_with_micro_shadow(
            slide,
            text=verse["text"],
            left=left, top=body_top,
            width=box_w, height=body_box_h,
            font_size_pt=BODY_SIZE_PT,
            bold=True, align=PP_ALIGN.JUSTIFY
        )

        # 본문 줄간격만 살짝 조정
        main_box.text_frame.paragraphs[0].line_spacing = LINE_SPACING
        shadow_box.text_frame.paragraphs[0].line_spacing = LINE_SPACING

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
