# -*- coding: utf-8 -*-
"""
테스트 전용 ppt_generator.py
- 템플릿(.pptx) 전혀 사용 안 함
- 배경 이미지 + 텍스트박스만으로 PPT 생성
- 우선 '확실히 동작'하는 버전

app.py에서 import 해서 사용하던 함수 시그니처와 동일:
    make_bible_ppt(json_path, ref_path, output_path, background_image)

필요 파일:
- extractor.extract_bible_verses(json_path, ref_path)  -> [{title, text}, ...]
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from extractor import extract_bible_verses

# ===== 가독성 기본값 (이전 합의안 그대로) =====
TITLE_SIZE_PT     = 36
BODY_SIZE_PT      = 50
BODY_LINE_SPACING = 1.15
FONT_NAME         = 'Apple SD Gothic Neo'  # 환경에 맞게 변경 가능

# 레이아웃(여백)
OUTER_MARGIN_IN   = 1.3
TITLE_TOP_IN      = 1.0
GAP_TITLE_BODY_IN = 0.85   # 제목 아래 본문 시작 위치 차이

def _add_title(slide, text, left, top, width):
    """제목 텍스트박스 추가"""
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
    """본문 텍스트박스 추가"""
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
    템플릿 없이 배경 이미지 + 텍스트박스로 PPT 생성 (확실히 되는 테스트 버전)
    """
    prs = Presentation()
    prs.slide_width = Inches(13.33)   # 16:9
    prs.slide_height = Inches(7.5)

    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    # 공통 레이아웃 값
    margin = Inches(OUTER_MARGIN_IN)
    box_width = prs.slide_width - 2 * margin

    for verse in verses:
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        # 배경 이미지 (있으면)
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


# ----- 로컬 단독 테스트용 (서버 없이 실행) -----
if __name__ == "__main__":
    # 예시 경로 (원하는 값으로 바꿔서 로컬에서 python ppt_generator.py 로 테스트 가능)
    json_path = "bible.jso_
