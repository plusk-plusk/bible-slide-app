import json
import re

# 책 약어 → 전체 이름 변환 맵
book_map = {
    "창": "창세기", "출": "출애굽기", "레": "레위기", "민": "민수기", "신": "신명기",
    "마": "마태복음", "막": "마가복음", "눅": "누가복음", "요": "요한복음",
    "행": "사도행전", "롬": "로마서", "고전": "고린도전서", "고후": "고린도후서",
    "갈": "갈라디아서", "엡": "에베소서", "빌": "빌립보서", "골": "골로새서",
    "살전": "데살로니가전서", "살후": "데살로니가후서", "딤전": "디모데전서",
    "딤후": "디모데후서", "딛": "디도서", "몬": "빌레몬서", "히": "히브리서",
    "약": "야고보서", "벧전": "베드로전서", "벧후": "베드로후서",
    "요일": "요한일서", "요이": "요한이서", "요삼": "요한삼서",
    "유": "유다서", "계": "요한계시록", "시": "시편", "잠": "잠언", "전": "전도서", "아": "아가"
}

def extract_bible_verses(json_path, selected_refs_path):
    with open(json_path, "r", encoding="utf-8") as f:
        bible_data = json.load(f)

    with open(selected_refs_path, "r", encoding="utf-8") as f:
        refs = [line.strip() for line in f if line.strip()]

    results = []

    for ref in refs:
        ref = ref.replace(" ", "")
        match = re.match(r"([가-힣]+)(\d+):(\d+)(?:~(\d+))?", ref)
        if not match:
            print(f"[형식 오류] '{ref}'")
            continue

        book_short, chapter, verse_start, verse_end = match.groups()
        full_book = book_map.get(book_short, book_short)
        chapter = int(chapter)
        verse_start = int(verse_start)
        verse_end = int(verse_end) if verse_end else verse_start

        for verse in range(verse_start, verse_end + 1):
            key = f"{book_short}{chapter}:{verse}"
            if key in bible_data:
                body = bible_data[key].strip()
                results.append({
                    "title": f"{full_book} {chapter}장 {verse}절",
                    "text": body
                })
            else:
                print(f"[경고] '{key}' 구절 없음")

    return results
