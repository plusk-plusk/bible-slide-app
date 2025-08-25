from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from extractor import extract_bible_verses

# ==============================
# 템플릿 설정 (경로/이름만 맞추면 나머지는 템플릿이 다 처리)
# ==============================
# 템플릿 파일이 templates/ 폴더 안에 있다면:
TEMPLATE_PATH = "templates/bible_verse_template.potx"
# 만약 루트(맨 위)에 두었다면: TEMPLATE_PATH = "bible_verse_template.potx"

# 슬라이드 마스터에서 만든 레이아웃 이름 (모르면 일단 None → 0번 레이아웃 사용)
LAYOUT_NAME = None  # 예: "Verse Slide" 처럼 이름을 지정했다면 문자열로 넣기

# Placeholder(자리표시자) 이름 (선택사항)
TITLE_PLACEHOLDER_NAME = "Title"  # 선택창에서 이름을 이렇게 주었다면 그대로 사용
BODY_PLACEHOLDER_NAME  = "Verse"  # 못 찾으면 타입으로 자동 탐색

# ==============================
# 유틸: 레이아웃/플레이스홀더 찾기
# ==============================
def _get_layout(prs, name_or_none):
    if name_or_none:
        for layout in prs.slide_layouts:
            if getattr(layout, "name", "") == name_or_none:
                return layout
    # 이름이 없거나 못 찾으면 0번 레이아웃 사용
    return prs.slide_layouts[0]

def _find_placeholder_by_name(slide, name):
    for ph in slide.placeholders:
        if ph.name == name:
            return ph
    return None

def _find_title_placeholder(slide):
    # 1) 이름으로
    ph = _find_placeholder_by_name(slide, TITLE_PLACEHOLDER_NAME)
    if ph:
        return ph
    # 2) 타입이 TITLE 인 것
    for ph in slide.placeholders:
        try:
            if ph.placeholder_format.type == PP_PLACEHOLDER.TITLE:
                return ph
        except Exception:
            continue
    # 3) shapes.title 보조
    if slide.shapes.title:
        return slide.shapes.title
    return None

def _find_body_placeholder(slide):
    # 1) 이름으로
    ph = _find_placeholder_by_name(slide, BODY_PLACEHOLDER_NAME)
    if ph:
        return ph
    # 2) 타입 후보군에서 첫 번째 (BODY → CONTENT → SUBTITLE 순)
    type_order = [
        PP_PLACEHOLDER.BODY,
        PP_PLACEHOLDER.CONTENT,
        PP_PLACEHOLDER.SUBTITLE,
        PP_PLACEHOLDER.OBJECT,
    ]
    for ph in slide.placeholders:
        try:
            if ph.placeholder_format.type in type_order:
                return ph
        except Exception:
            continue
    # 3) 마지막 수단: 제목이 아닌 첫 번째 placeholder
    for ph in slide.placeholders:
        try:
            if ph.placeholder_format.type != PP_PLACEHOLDER.TITLE:
                return ph
        except Exception:
            continue
    return None

# ==============================
# 메인: 템플릿에 텍스트만 채워 넣기
# ==============================
def make_bible_ppt(json_path, ref_path, output_path, background_image=None):
    """
    템플릿(.potx/.pptx)을 불러와서
    - 레이아웃 그대로 쓰고
    - Title / Verse 자리(placeholder)에 텍스트만 채웁니다.
    스타일(배경/글꼴/윤곽선/여백/자동맞춤)은 템플릿에서 관리합니다.
    background_image 인자는 호환을 위해 남겨두되 사용하지 않습니다.
    """
    prs = Presentation(TEMPLATE_PATH)
    layout = _get_layout(prs, LAYOUT_NAME)

    verses = extract_bible_verses(json_path, ref_path)
    if not verses:
        print("⚠️ 구절이 없어서 PPT를 생성하지 않았습니다.")
        return

    for verse in verses:
        slide = prs.slides.add_slide(layout)

        # 제목 채우기
        title_ph = _find_title_placeholder(slide)
        if title_ph is not None:
            title_ph.text = verse.get("title", "")
        else:
            print("⚠️ 제목 placeholder를 찾지 못해 이 슬라이드의 제목을 건너뜁니다.")

        # 본문 채우기
        body_ph = _find_body_placeholder(slide)
        if body_ph is not None:
            body_ph.text = verse.get("text", "")
        else:
            print("⚠️ 본문 placeholder를 찾지 못해 이 슬라이드의 본문을 건너뜁니다.")

    prs.save(output_path)
    print(f"✅ PPT 저장 완료: {output_path}")
