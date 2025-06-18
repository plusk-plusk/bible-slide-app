from flask import Flask, render_template, request, redirect, send_file
from ppt_generator import make_bible_ppt as generate_ppt
import re
from bible_loader import get_verse_text  # ✅ 필요 시 실제 본문 로딩 함수로 교체

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    raw_input = request.form.get("verses", "").strip()
    if not raw_input:
        return "❌ 구절이 입력되지 않았습니다.", 400

    processed_refs = []

    # ✅ 여러 줄 입력 처리
    for line in raw_input.splitlines():
        line = line.strip()
        if not line:
            continue

        # 🎯 1. 절 범위 (예: 요3:16~18)
        match_range = re.match(r"^([가-힣]{1,3})(\d+):(\d+)~(\d+)$", line)
        if match_range:
            book, chapter, start, end = match_range.groups()
            for verse in range(int(start), int(end)+1):
                processed_refs.append(f"{book}{chapter}:{verse}")
            continue

        # 🎯 2. 단일 절 (예: 요3:16)
        match_single = re.match(r"^([가-힣]{1,3})(\d+):(\d+)$", line)
        if match_single:
            book, chapter, verse = match_single.groups()
            processed_refs.append(f"{book}{chapter}:{verse}")
            continue

        # 🎯 3. 장 전체 (예: 요3 → 요3:1~끝)
        match_chapter_only = re.match(r"^([가-힣]{1,3})(\d+)$", line)
        if match_chapter_only:
            book, chapter = match_chapter_only.groups()

            # ⛏️ 안전하게 1~200절까지 시도 → 본문 없으면 종료
            for verse in range(1, 200):
                text = get_verse_text(book, chapter, verse)  # ❗️본문 로딩 함수에 맞게 수정 필요
                if text:
                    processed_refs.append(f"{book}{chapter}:{verse}")
                else:
                    break
            continue

        # ⚠️ 예외 처리: 형식 오류
        processed_refs.append(f"# 형식 오류: {line}")

    # 🎯 텍스트 저장
    with open("selected_refs.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(processed_refs))

    try:
        generate_ppt(
            json_path="bible.json",
            ref_path="selected_refs.txt",
            output_path="BibleSlides.pptx",
            background_image="001.jpg"
        )
        return redirect("/done")
    except Exception as e:
        return f"❌ 슬라이드 생성 중 오류 발생: {e}", 500

@app.route("/done")
def done():
    return render_template("done.html")

@app.route("/download")
def download():
    return send_file("BibleSlides.pptx", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
