# bible_loader.py
import json

with open("bible.json", "r", encoding="utf-8") as f:
    bible_data = json.load(f)

def get_verse_text(book, chapter, verse):
    try:
        return bible_data[book][chapter][str(verse)]
    except KeyError:
        return None
