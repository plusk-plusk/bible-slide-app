import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import PP_PLACEHOLDER
from extractor import extract_bible_verses

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "bible_verse_template.pptx")

LAYOUT_NAME = None
TITLE_PLACEHOLDER_NAME = "Title"
BODY_PLACEHOLDER_NAME  = "Verse"

# -----------------------
# 유틸
# -----------------------
def _has_text_frame(shape):
    try:
        return getattr(shape, "has_text_frame", False) and shape.has_text_frame
    except Exception:
        return False

def _shape_bbox(shape):
    try:
        return shape.left, shape.top, shape.width, shape.height
    except Exception:
        return None

def _debug_dump_placeholders(slide):
    print("---- placeholders on slide ----")
    for ph in slide.placeholders:
        t = None
        nm = getattr(ph, "name", "?")
        try:
            t = ph.placeholder_format.type
        except Exception:
            pass
        print(f"name={nm}, type={t}, has_tf={_has_text_frame(ph)}")

def _get_layout(prs, name_or_none):
    if name_or_none:
        for layout in prs.slide_layouts:
            if getattr(layout, "name", "") == name_or_none:
                return layout
    return prs.slide_layouts[0]

def _find_by_name(slide, name):
    for ph in slide.placeholders:
        if ph.name == name:
            return ph
    return None

def _safe_set_in_placeholder_or_textbox(slide, target_shape, text, fallback_bbox=None):
    """
    target_shape에 텍스트를 넣되, 불가하면 같은 위치(fallback_bbox)나
    적절한 여백 영역에 새 텍스트박스를 만들어 텍스트를 입력.
    """
    text = text or ""
    # 1) placeholder에 직접 넣기 시도
    if target_shape is not None and _has_text_frame(target_shape):
        try:
            tf = target_shape.text_frame
            tf.clear()
            tf.text = text
            return
        except Exception as e:
            print("placeholder set failed:", repr(e))

    # 2) 동일 위치에 텍스트박스 생성 시도
    bbox = None
    if fallback_bbox:
        bbox = fallback_bbox
    elif target_shape is not None:
        bbox = _shape_bbox(target_shape)

    if bbox:
        left, top, width, height = bbox
    else:
        # 완전한 fallback: 화면의 안전한 영역 잡기
        # 16:9 가정(템플릿도 16:9일 가능성 높음)
        prs = slide.part.presentation
        sw, sh = prs.slide_width, prs.slide_height
        m = Inches(1.0)
        left, top = m, Inches(1.2)
        width, height = sw - 2*m, sh - 2*Inches(1.4)

    try:
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame
        tf.clear()
        tf.text = text
    except Exception as e:
        print("textbox fallback failed:", repr(e))

def _find_title_placeholder(slide):
    # 1) 이름
    ph = _find_by_name(slide, TITLE_PLACEHOLDER_NAME)
    if ph: return ph
    # 2) 타입
    for typ in (PP_PLACEHOLDER.TITLE, PP_PLACEHOLDER.CENTER_TITLE):
        for shp in slide.placeholders:
            try:
                if shp.placeholder_format.type == typ:
                    return shp
            except Exception:
                continue
    # 3) 보조
    return getattr(slide.shapes, "title", None)

def _find_body_placeholder(slide):
    # 1) 이름
    ph = _find_by_name(slide, BODY_PLACEHOLDER_NAME)
    if ph: return ph
    # 2) 타입 우선순위
    type_order = [
        PP_PLACEHOLDER.BODY,
        PP_PLACEHOLDER.SUBTITLE,
        PP_PLACEHOLDER.CONTENT,
        PP_PLACEHOLDER.OBJECT,
    ]
    for t in type_order:
        for shp in slide.placeholders:
            try:
                if shp.placeholder_format.type == t:
                    return shp
            except Exception:
                continue
    # 3) 마지막: 제목이 아닌 아무 placeholder
    for shp in slide.placeholders:
        try:
            if shp.placeholder_format.type != PP_PLACEHOLDER.TITLE:
                return shp
        except Exception:
            continue
    return None

# -----------------------
# 메인
# -----------------------
def make_bible_ppt(json_path, ref_path, output_path, background_image=None):
    print("TEMPLATE_PATH:", TEMPLATE_PATH)
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(
            f"템플릿이 없습니다: {TEMPLATE_PATH}\n"
            f"- templates/bible_verse_template.pptx 가 존재하는지 확인하세요."
        )

    prs = Presentation(TEMPLATE_PATH)
    layout = _get_layout(prs, LAYOUT_NAME)

    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        slide = prs.slides.add_slide(layout)

        # 진단 로그
        _debug_dump_placeholders(slide)

        # 제목 채우기 (실패하면 동일 위치에 텍스트박스 생성)
        title_ph = _find_title_placeholder(slide)
        title_bbox = _shape_bbox(title_ph) if title_ph is not None else None
        try:
            _safe_set_in_placeholder_or_textbox(
                slide, title_ph, verse.get("title", ""), fallback_bbox=title_bbox
            )
        except Exception as e:
            print("제목 처리 오류:", repr(e))

        # 본문 채우기 (실패하면 동일 위치에 텍스트박스 생성)
        body_ph = _find_body_placeholder(slide)
        body_bbox = _shape_bbox(body_ph) if body_ph is not None else None
        try:
            _safe_set_in_placeholder_or_textbox(
                slide, body_ph, verse.get("text", ""), fallback_bbox=body_bbox
            )
        except Exception as e:
            print("본문 처리 오류:", repr(e))

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
