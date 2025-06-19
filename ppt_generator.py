from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from extractor import extract_bible_verses

def make_bible_ppt(json_path, ref_path, output_path, background_image):
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    verses = extract_bible_verses(json_path, ref_path)

    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.shapes.add_picture(background_image, 0, 0,
                                 width=prs.slide_width, height=prs.slide_height)

        margin_h = Inches(1.2)
        box_width = prs.slide_width - 2 * margin_h

        # 제목 텍스트 박스
        title_top = Inches(1.0)
        title_box = slide.shapes.add_textbox(margin_h, title_top, box_width, Inches(0.6))
        title_frame = title_box.text_frame
        title_frame.word_wrap = True
        p_title = title_frame.paragraphs[0]
        p_title.alignment = PP_ALIGN.LEFT
        run_title = p_title.add_run()
        run_title.text = verse["title"]
        run_title.font.size = Pt(36)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(51, 51, 51)  # 회색 (#333333)
        run_title.font.name = 'Apple SD Gothic Neo'

        # 본문 텍스트 박스
        body_top = title_top + Inches(0.7)
        body_box = slide.shapes.add_textbox(margin_h, body_top, box_width, Inches(3.5))
        body_frame = body_box.text_frame
        body_frame.word_wrap = True
        p_body = body_frame.paragraphs[0]
        p_body.alignment = PP_ALIGN.JUSTIFY
        p_body.line_spacing = 1.1
        run_body = p_body.add_run()
        run_body.text = verse["text"]
        run_body.font.size = Pt(55)
        run_body.font.bold = True
        run_body.font.color.rgb = RGBColor(34, 34, 34)  # 더 진한 회색 (#222222)
        run_body.font.name = 'Apple SD Gothic Neo'

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
