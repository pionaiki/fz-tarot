[![FAP: Build for multiple SDK sources](https://github.com/pionaiki/fz-tarot/actions/workflows/build.yml/badge.svg)](https://github.com/pionaiki/fz-tarot/actions/workflows/build.yml)

![Banner](.flipcorg/banner.png)

# fz-tarot

Tarot spread for Flipper Zero, with artwork for all 78 cards: 22 major arcana and
56 minor arcana (Cups, Swords, Wands, and Pentacles).

Run draws three distinct cards from the full deck. Left and Right select a card
to show its name. Settings can enable reversed cards (off by default); a card
cannot appear twice in a spread, even in different orientations. Browse Deck
shows the upright and reversed artwork for every card.

## Download

- [Official app store](https://lab.flipper.net/apps/tarot)
- Auto-built releases are available on the [Github actions page](https://github.com/pionaiki/fz-tarot/actions/workflows/build.yml)

## Roadmap

- [x] Add upside-down cards
- [x] Make the random number generator source radio
- [x] Make a deck browser
- [x] Add Minor arcana

## Development

Build with the official [uFBT](https://github.com/flipperdevices/flipperzero-ufbt)
tool by running `ufbt` in the repository root. The installable package is
written to `dist/tarot.fap`.

The PNG assets are checked in, so no artwork generator is needed to build the
app. Minor arcana follow the frame of the original cards (rounded corners,
three-pixel header label, divider) and are labelled A, II–X, P, KN, Q and K.
Numbered cards use suit pips; aces show a large emblem of their suit. Court
figures each have a distinct pose: the Page stands, the Knight rides, the Queen
sits in a gown before her throne, and the bearded King sits on a dais. Each
holds their suit's object. Reversed minor arcana images are exact 180-degree
rotations.

To reproduce the minor arcana artwork or run the host regression checks, use
Python with Pillow 9.1 or newer and a C compiler (`cc`):

```sh
python3 tools/generate_minor_icons.py
python3 -m unittest discover -s tests -v
```

The tests check the 112 minor arcana assets and compile the real card table,
selection scene, and browser functions with minimal host stubs. Scripted
random values exercise every card, both reversal settings, duplicate rejection,
and browser wraparound. They do not test radio entropy or replace testing on
a Flipper Zero. Pull-request CI runs these checks and builds against the dev,
release-candidate, and release SDKs.

## Credits

- Code: [pionaiki](https://github.com/pionaiki), [OrionW06](https://github.com/OrionW06)
- Art: [tihyltew](https://github.com/tihyltew)
- Minor arcana: original pixel artwork reproduced by `tools/generate_minor_icons.py`