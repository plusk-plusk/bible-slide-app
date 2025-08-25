# -*- coding: utf-8 -*-
"""
서버용 최소/안정 ppt_generator.py
- 템플릿(.pptx) 사용 안 함 (우회)
- 배경 이미지 + 텍스트박스로 PPT 생성
- __main__ 테스트 블록 없음 (문법 에러 방지)
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from extractor import extract_bible_verses

# 가독성 기본값
TITLE_SIZE_PT     = 36
BODY_SIZE_PT      = 50
BODY_LINE_SPACING = 1.15
FONT_NAME         = 'Apple SD Gothic Neo'

# 레이아웃(여백)
OUTER_MARGIN_IN   = 1.3
TITLE_TOP_IN      = 1.0
GAP_TITLE_BODY_IN = 0.85   # 제목 아래 본문 시작 위치 차이

def _add_title(slide, text, left, top, width):
    box = slide.shapes.add_textbox(left, top, width, Inches(0.6))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text or ""
    run.font.size = Pt(TITLE_SIZE_PT)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    run.font.name = FONT_NAME

def _add_body(slide, text, left, top, width, height):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.JUSTIFY
    p.line_spacing = BODY_LINE_SPACING
    run = p.add_run()
    run.text = text or ""
    run.font.size = Pt(BODY_SIZE_PT)
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)
    run.font.name = FONT_NAME

def make_bible_ppt(json_path, ref_path, output_path, background_image):
    """
    템플릿 없이 배경 이미지 + 텍스트박스로 PPT 생성 (서버용 안정 버전)
    app.py에서: from ppt_generator import make_bible_ppt as generate_ppt
    """
    prs = Presentation()
    prs.slide_width = Inches(13.33)   # 16:9
    prs.slide_height = Inches(7.5)

    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    margin = Inches(OUTER_MARGIN_IN)
    box_width = prs.slide_width - 2 * margin

    for verse in verses:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # 배경 이미지
        if background_image:
            try:
                slide.shapes.add_picture(
                    background_image, 0, 0,
                    width=prs.slide_width, height=prs.slide_height
                )
            except Exception as e:
                print("배경 이미지 로드 실패:", repr(e))

        # 제목
        title_top = Inches(TITLE_TOP_IN)
        _add_title(slide, verse.get("title", ""), margin, title_top, box_width)

        # 본문
        body_top = title_top + Inches(GAP_TITLE_BODY_IN)
        body_height = Inches(3.8)  # 필요시 조정
        _add_body(slide, verse.get("text", ""), margin, body_top, box_width, body_height)

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
