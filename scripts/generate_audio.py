import asyncio
import toml
import os

import edge_tts

VOICE = "ja-JP-NanamiNeural"
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "audio")
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "cards.toml")

MAX_RETRIES = 5
DELAY_BETWEEN = 0.3  # seconds between requests to avoid rate limiting


async def generate_one(text, filepath):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(filepath)
            return
        except Exception as e:
            if attempt < MAX_RETRIES:
                wait = 2 ** attempt
                print(f"  Retry {attempt}/{MAX_RETRIES} for '{text}' in {wait}s ({e})")
                await asyncio.sleep(wait)
            else:
                print(f"  FAILED '{text}' after {MAX_RETRIES} attempts: {e}")
                raise


async def main():
    with open(DATA_FILE, "r") as f:
        data = toml.load(f)

    os.makedirs(AUDIO_DIR, exist_ok=True)

    cards = data["cards"]
    total = len(cards)
    generated = 0
    skipped = 0

    for i, card in enumerate(cards):
        card_id = card["id"]
        jp = card["japanese"]
        filepath = os.path.join(AUDIO_DIR, f"{card_id}.mp3")

        if os.path.exists(filepath):
            skipped += 1
            continue

        print(f"[{i+1}/{total}] Generating: {jp}")
        await generate_one(jp, filepath)
        generated += 1
        await asyncio.sleep(DELAY_BETWEEN)

    print(f"\nDone. Generated: {generated}, Skipped: {skipped}, Total: {total}")


if __name__ == "__main__":
    asyncio.run(main())
