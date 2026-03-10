import os
import hashlib
import toml
import genanki

SCRIPT_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "data", "cards.toml")
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "audio")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "output")

# Stable IDs derived from deck/model name so they stay consistent across rebuilds
def stable_id(name):
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

DECK_NAME = "Japanese Vocabulary"
MODEL_NAME = "Japanese Vocab (Recognition + Production)"

CARD_CSS = """\
.card {
    font-family: "Hiragino Sans", "Yu Gothic", "Meiryo", "Noto Sans JP", sans-serif;
    font-size: 24px;
    text-align: center;
    color: #1a1a1a;
    background-color: #fafaf8;
    padding: 20px;
}

.japanese {
    font-size: 48px;
    font-weight: bold;
    margin-bottom: 20px;
    color: #2c2c2c;
}

.english {
    font-size: 28px;
    margin-bottom: 16px;
    color: #333;
}

.reading {
    font-size: 20px;
    color: #888;
    margin-bottom: 20px;
}

.example {
    font-size: 22px;
    margin-top: 20px;
    padding: 12px;
    background-color: #f0efe8;
    border-radius: 8px;
    text-align: left;
    display: inline-block;
}

.example-jp {
    margin-bottom: 8px;
    color: #2c2c2c;
}

details {
    cursor: pointer;
    margin-top: 4px;
}

details summary {
    color: #6a9fb5;
    font-size: 16px;
    user-select: none;
}

details .example-en {
    color: #666;
    font-size: 18px;
    margin-top: 6px;
}

.type-prompt {
    font-size: 18px;
    color: #888;
    margin-top: 12px;
}

input[type="text"] {
    font-size: 24px;
    text-align: center;
}

.correct {
    color: #4a8;
}

.incorrect {
    color: #c44;
}
"""

# Recognition card: Japanese front -> English back
RECOGNITION_FRONT = """\
<div class="japanese">{{Japanese}}</div>
{{Audio}}
"""

RECOGNITION_BACK = """\
<div class="japanese">{{Japanese}}</div>
{{Audio}}
<hr>
<div class="english">{{English}}</div>
{{#Reading}}
<div class="reading">{{Reading}}</div>
{{/Reading}}
{{#Example}}
<div class="example">
    <div class="example-jp">{{Example}}</div>
    <details>
        <summary>[translation]</summary>
        <div class="example-en">{{ExampleEn}}</div>
    </details>
</div>
{{/Example}}
"""

# Production card: English front -> type Japanese
PRODUCTION_FRONT = """\
<div class="english">{{English}}</div>
<div class="type-prompt">Type the Japanese word:</div>
{{type:Japanese}}
"""

PRODUCTION_BACK = """\
<div class="english">{{English}}</div>
<hr>
{{type:Japanese}}
<div class="japanese">{{Japanese}}</div>
{{#Reading}}
<div class="reading">{{Reading}}</div>
{{/Reading}}
{{Audio}}
{{#Example}}
<div class="example">
    <div class="example-jp">{{Example}}</div>
    <details>
        <summary>[translation]</summary>
        <div class="example-en">{{ExampleEn}}</div>
    </details>
</div>
{{/Example}}
"""

model = genanki.Model(
    stable_id(MODEL_NAME),
    MODEL_NAME,
    fields=[
        {"name": "Japanese"},
        {"name": "Reading"},
        {"name": "English"},
        {"name": "Answer"},
        {"name": "Example"},
        {"name": "ExampleEn"},
        {"name": "Audio"},
    ],
    templates=[
        {
            "name": "Recognition (JP → EN)",
            "qfmt": RECOGNITION_FRONT,
            "afmt": RECOGNITION_BACK,
        },
        {
            "name": "Production (EN → JP)",
            "qfmt": PRODUCTION_FRONT,
            "afmt": PRODUCTION_BACK,
        },
    ],
    css=CARD_CSS,
)


def card_guid(card_id, template_idx):
    """Stable GUID from card UUID so Anki can track cards across deck updates."""
    return genanki.guid_for(card_id, template_idx)


def main():
    with open(DATA_FILE, "r") as f:
        data = toml.load(f)

    deck = genanki.Deck(stable_id(DECK_NAME), DECK_NAME)
    media_files = []

    cards = data["cards"]

    for card in cards:
        card_id = card["id"]
        audio_filename = f"{card_id}.mp3"
        audio_path = os.path.join(AUDIO_DIR, audio_filename)

        audio_field = ""
        if os.path.exists(audio_path):
            audio_field = f"[sound:{audio_filename}]"
            media_files.append(audio_path)

        note = genanki.Note(
            model=model,
            fields=[
                card["japanese"],
                card.get("reading", ""),
                card["english"],
                card.get("answer", card["english"].split(",")[0].strip()),
                card.get("example", ""),
                card.get("example_en", ""),
                audio_field,
            ],
            guid=card_guid(card_id, 0),
        )
        deck.add_note(note)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "japanese_vocabulary.apkg")

    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file(output_path)

    print(f"Deck generated: {output_path}")
    print(f"Cards: {len(cards)} words x 2 types = {len(cards) * 2} cards")
    print(f"Audio files bundled: {len(media_files)}")


if __name__ == "__main__":
    main()
