import json

with open("bible.json", "r", encoding="utf-8") as f:
    bible_data = json.load(f)

def get_verse_text(book, chapter, verse):
    key = f"{book}{int(chapter)}:{int(verse)}"
    return bible_data.get(key)
