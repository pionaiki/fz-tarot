# Card Development Guide for fz-tarot

This document explains how to add new cards (major or minor arcana) to the fz-tarot app for Flipper Zero.

## 1. Card Types
- **Major Arcana:** 22 cards (The Fool to The World), each with upright and reversed images.
- **Minor Arcana:** Four suits (Cups, Swords, Wands, Pentacles), each with Ace–10, Page, Knight, Queen, King. Only upright images are currently used.

## 2. Adding Card Images
- Place 1-bit PNG images in the `images/` directory.
- Major arcana: Name images as `major_N.png` (upright) and `major_N_.png` (reversed), where N is 0–21.
- Minor arcana: Name images as `cups_1.png`, `swords_queen.png`, etc. (see below for naming convention).
- Images should be the same size as existing cards (see `images/major_0.png` for reference).

### Minor Arcana Naming Example
- Ace of Cups: `cups_1.png`
- 2 of Swords: `swords_2.png`
- Queen of Wands: `wands_queen.png`
- King of Pentacles: `pentacles_king.png`

## 3. Updating the Code
- Card definitions are in `cards.c` (see the `card` array).
- Add a new entry for each card, specifying its name and icon pointer (e.g., `&I_cups_1`).
- For new images, run the build system to regenerate the icon header (`tarot_icons.h`).
- If you add new cards, update any logic that uses the card array size or indices.

## 4. Adding Card Meanings (Optional)
- You can add a `const char* meaning` field to the `Card` struct for upright and reversed meanings.
- Update the deck browser and game scenes to display these meanings.

## 5. Testing
- Rebuild the app and use the deck browser to verify new cards and images appear correctly.

---

For questions or contributions, see the main [README.md](./README.md) or open an issue on GitHub. 