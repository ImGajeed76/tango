# Tango (単語)

*It takes two to learn vocabulary.*

A Japanese vocabulary Anki deck with 587 words, audio pronunciation, and example sentences. Features two card types for both recognition and production practice.

## Card Types

**Recognition (Japanese → English)**
- Front: Japanese word with audio
- Back: English translation, hiragana reading (for kanji), example sentence with collapsible translation

**Production (English → Type Japanese)**
- Front: English meaning with text input
- Back: Correct Japanese word with audio, reading, and example sentence

## Setup

### Install Anki

- **Desktop**: [apps.ankiweb.net](https://apps.ankiweb.net)
- **Android**: AnkiDroid from F-Droid or Google Play
- **iOS**: AnkiMobile ($25, one-time)

### Import the Deck

1. Download [`japanese_vocabulary.apkg`](https://github.com/ImGajeed76/tango/blob/main/output/japanese_vocabulary.apkg)
2. Open Anki → File → Import → select the `.apkg` file
3. Create a free [AnkiWeb](https://ankiweb.net) account to sync across devices

## Adding New Cards

1. Create `data/add.toml`:

```toml
[[cards]]
japanese = "犬"
english = "dog"
answer = "dog"
example = "犬がいます。"
example_en = "There is a dog."
```

2. Run the pipeline:

```bash
python scripts/add_cards.py
```

This will generate a UUID, auto-detect hiragana readings for kanji, generate audio, append to `data/cards.toml`, and rebuild the `.apkg`.

3. Re-import the `.apkg` in Anki (see [Updating the Deck](#updating-the-deck)).

## Updating the Deck

After adding new cards or rebuilding the deck, re-import the updated `.apkg`:

1. Open Anki → File → Import → select `japanese_vocabulary.apkg`
2. Set **Update notes** and **Update note types** to **Always**
3. Import — new cards are added and existing cards are updated
4. Your review history, intervals, and scheduling are preserved
5. Sync to AnkiWeb to update your other devices

## Project Structure

```
├── data/
│   └── cards.toml              # All card data (source of truth)
├── audio/
│   └── {uuid}.mp3              # TTS audio per card (ja-JP-NanamiNeural)
├── scripts/
│   ├── add_cards.py            # Add new cards pipeline
│   ├── build_deck.py           # Generate .apkg from cards.toml
│   └── generate_audio.py       # Bulk audio generation
└── output/
    └── japanese_vocabulary.apkg # Ready-to-import Anki deck
```

## Dependencies

```bash
pip install toml pykakasi edge-tts genanki
```

## Recommended Anki Settings

- Enable **FSRS** (under Deck Options → Advanced)
- **Desired retention**: 0.90
- **New cards/day**: 15–20
- **Max reviews/day**: 9999
- **Bury new siblings**: On (so you don't see both card types for the same word on the same day)
