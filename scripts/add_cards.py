"""
Add new cards to the deck.

Usage:
    python scripts/add_cards.py [path_to_add.toml]

If no path is given, defaults to data/add.toml.

This script will:
1. Read new cards from the add.toml file
2. Generate UUIDs and readings (for kanji words) automatically
3. Append them to data/cards.toml
4. Generate audio for the new cards only
5. Rebuild the Anki deck
6. Delete the add.toml file when done
"""

import sys
import os
import uuid
import asyncio

import toml
import pykakasi
import edge_tts

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
DATA_FILE = os.path.join(ROOT_DIR, "data", "cards.toml")
AUDIO_DIR = os.path.join(ROOT_DIR, "audio")
DEFAULT_ADD_FILE = os.path.join(ROOT_DIR, "data", "add.toml")

VOICE = "ja-JP-NanamiNeural"

kks = pykakasi.kakasi()


def has_kanji(text):
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def get_reading(jp):
    if has_kanji(jp):
        result = kks.convert(jp)
        return "".join([item["hira"] for item in result])
    return ""


def load_existing_cards():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return toml.load(f)


def get_existing_japanese(cards):
    return {card["japanese"] for card in cards}


def write_cards_toml(data):
    lines = []
    for card in data["cards"]:
        lines.append("[[cards]]")
        lines.append(f'id = "{card["id"]}"')
        lines.append(f'japanese = "{card["japanese"]}"')
        lines.append(f'reading = "{card["reading"]}"')
        lines.append(f'english = "{card["english"]}"')
        lines.append(f'answer = "{card["answer"]}"')
        lines.append(f'example = "{card["example"]}"')
        lines.append(f'example_en = "{card["example_en"]}"')
        lines.append("")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


async def generate_audio(text, filepath):
    for attempt in range(1, 6):
        try:
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(filepath)
            return
        except Exception as e:
            if attempt < 5:
                wait = 2 ** attempt
                print(f"  Retry {attempt}/5 for '{text}' in {wait}s ({e})")
                await asyncio.sleep(wait)
            else:
                print(f"  FAILED '{text}' after 5 attempts: {e}")
                raise


async def main():
    add_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ADD_FILE

    if not os.path.exists(add_file):
        print(f"No file found at {add_file}")
        print(f"Create {add_file} with new cards in this format:")
        print()
        print('[[cards]]')
        print('japanese = "犬"')
        print('english = "dog"')
        print('answer = "dog"')
        print('example = "犬がいます。"')
        print('example_en = "There is a dog."')
        sys.exit(1)

    # Load new cards
    with open(add_file, "r", encoding="utf-8") as f:
        new_data = toml.load(f)

    new_cards = new_data.get("cards", [])
    if not new_cards:
        print("No cards found in add file.")
        sys.exit(1)

    # Load existing cards
    existing_data = load_existing_cards()
    existing_japanese = get_existing_japanese(existing_data["cards"])

    # Process new cards
    added = []
    skipped = []

    for card in new_cards:
        jp = card["japanese"]

        if jp in existing_japanese:
            skipped.append(jp)
            continue

        # Generate UUID and reading
        card["id"] = str(uuid.uuid4())
        card["reading"] = card.get("reading", get_reading(jp))
        card["answer"] = card.get("answer", card["english"].split(",")[0].strip())
        card["example"] = card.get("example", "")
        card["example_en"] = card.get("example_en", "")

        existing_data["cards"].append(card)
        existing_japanese.add(jp)
        added.append(card)

    if skipped:
        print(f"Skipped {len(skipped)} duplicates: {', '.join(skipped)}")

    if not added:
        print("No new cards to add.")
        sys.exit(0)

    # Write updated cards.toml
    write_cards_toml(existing_data)
    print(f"Added {len(added)} cards to cards.toml (total: {len(existing_data['cards'])})")

    # Generate audio for new cards
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print("\nGenerating audio...")
    for i, card in enumerate(added):
        filepath = os.path.join(AUDIO_DIR, f"{card['id']}.mp3")
        if os.path.exists(filepath):
            continue
        print(f"  [{i+1}/{len(added)}] {card['japanese']}")
        await generate_audio(card["japanese"], filepath)
        await asyncio.sleep(0.3)

    # Rebuild Anki deck
    print("\nRebuilding Anki deck...")
    build_deck = os.path.join(SCRIPT_DIR, "build_deck.py")
    os.system(f"python {build_deck}")

    # Clean up add file
    os.remove(add_file)
    print(f"\nDone! Removed {add_file}")


if __name__ == "__main__":
    asyncio.run(main())
