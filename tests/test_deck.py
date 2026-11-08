"""Host-side deck and asset checks: python3 -m unittest discover -s tests."""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SUITS = ("cups", "swords", "wands", "pentacles")


def function_source(name):
    source = (ROOT / "tarot.c").read_text()
    match = re.search(
        rf"^(?:static )?(?:void|bool) {name}\([^\n]*\).*?^}}",
        source,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"Missing function: {name}")
    return match.group(0)


HARNESS = r"""
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#define unbiased_rand hardware_unbiased_rand
#include "cards.c"
#undef unbiased_rand

typedef struct { bool allow_reversed; void* widget; void* view_dispatcher; } App;
typedef struct { int type; int key; } InputEvent;
enum { InputTypeShort, InputKeyRight, InputKeyLeft, AlignCenter, AlignBottom,
       AlignRight, AlignTop, FontPrimary, FontSecondary, AppView_Widget };
struct { int card[3]; bool selected[3]; } spread;
static int deck_browser_index;
static const int card_x = 23;
static unsigned random_values[16];
static unsigned random_count;
static unsigned random_index;
static const struct Icon* displayed_icons[2];
static unsigned displayed_count;
static const char* displayed_name;
static char displayed_position[16];

uint16_t unbiased_rand(uint16_t max) {
    assert(random_index < random_count);
    unsigned value = random_values[random_index++];
    assert(value < max);
    return value;
}
static void widget_reset(void* widget) {
    (void)widget;
    displayed_count = 0;
}
static void widget_add_icon_element(
    void* widget, int x, int y, const struct Icon* icon) {
    (void)widget;
    assert(x >= 0 && x + 23 <= 128);
    assert(y >= 0 && y + 32 <= 64);
    assert(icon != NULL && displayed_count < 2);
    displayed_icons[displayed_count++] = icon;
}
static void widget_add_string_element(
    void* widget, int x, int y, int horizontal, int vertical, int font,
    const char* text) {
    (void)widget; (void)x; (void)y; (void)horizontal; (void)vertical;
    if(font == FontPrimary) displayed_name = text;
    else snprintf(displayed_position, sizeof(displayed_position), "%s", text);
}
static void draw_tarot(void* app) { (void)app; }
static bool widget_input_callback(InputEvent* event, void* app) {
    (void)event; (void)app; return false;
}
static void* widget_get_view(void* widget) { return widget; }
static void view_set_context(void* view, void* app) { (void)view; (void)app; }
static void view_set_input_callback(void* view, bool (*callback)(InputEvent*, void*)) {
    (void)view; (void)callback;
}
static void view_dispatcher_switch_to_view(void* dispatcher, int view) {
    (void)dispatcher; (void)view;
}
#define TAG "test"
#define FURI_LOG_T(...) ((void)0)
"""

CHECKS = r"""
int main(void) {
    assert(card_number == 78);
    assert(get_total_card_count() == 78);
    assert(sizeof(card) / sizeof(card[0]) == 156);
    for(int base = 0; base < card_number; ++base) {
        assert(card[base].icon && card[base + card_number].icon);
        assert(strcmp(card[base].name, card[base + card_number].name) == 0);
        for(int other = 0; other < base; ++other)
            assert(strcmp(card[base].name, card[other].name) != 0);
        for(int reversed = 0; reversed < 2; ++reversed) {
            App app = {.allow_reversed = reversed};
            int next = (base + 1) % card_number;
            int last = (base + 2) % card_number;
            random_count = 0;
            random_index = 0;
            random_values[random_count++] = base;
            if(reversed) random_values[random_count++] = 1;
            random_values[random_count++] = base;
            random_values[random_count++] = next;
            if(reversed) random_values[random_count++] = 0;
            random_values[random_count++] = base;
            random_values[random_count++] = next;
            random_values[random_count++] = last;
            if(reversed) random_values[random_count++] = 1;
            tarot_app_scene_on_enter_game(&app);
            assert(random_index == random_count);
            assert(spread.card[0] == base + reversed * card_number);
            assert(spread.card[1] == next);
            assert(spread.card[2] == last + reversed * card_number);
            for(int position = 0; position < 3; ++position) {
                assert(spread.card[position] >= 0 && spread.card[position] < 156);
                for(int earlier = 0; earlier < position; ++earlier)
                    assert(spread.card[position] % card_number !=
                           spread.card[earlier] % card_number);
            }
        }
        App app = {0};
        deck_browser_index = base;
        draw_deck_browser(&app);
        assert(displayed_count == 2);
        assert(displayed_icons[0] == card[base].icon);
        assert(displayed_icons[1] == card[base + card_number].icon);
        assert(strcmp(displayed_name, card[base].name) == 0);
        char expected_position[16];
        snprintf(expected_position, sizeof(expected_position), "%d/77", base);
        assert(strcmp(displayed_position, expected_position) == 0);
    }
    assert(strcmp(card[21].name, "The World") == 0);
    assert(strcmp(card[22].name, "Ace of Cups") == 0);
    assert(strcmp(card[77].name, "King of Pentacles") == 0);
    App app = {0};
    InputEvent event = {.type = InputTypeShort, .key = InputKeyRight};
    deck_browser_index = 77;
    assert(deck_browser_input_callback(&event, &app));
    assert(deck_browser_index == 0);
    event.key = InputKeyLeft;
    assert(deck_browser_input_callback(&event, &app));
    assert(deck_browser_index == 77);
    puts("All 78 cards reachable; reversals unique; all browser indices valid.");
    return 0;
}
"""


class DeckTests(unittest.TestCase):
    def test_minor_artwork(self):
        pixels = set()
        for suit in SUITS:
            for rank in range(1, 15):
                stem = f"minor_{suit}_{rank}"
                with Image.open(ROOT / "images" / f"{stem}.png") as upright:
                    with Image.open(ROOT / "images" / f"{stem}_.png") as reversed_icon:
                        self.assertEqual(upright.size, (23, 32))
                        self.assertEqual(upright.mode, "1")
                        self.assertEqual(reversed_icon.size, upright.size)
                        self.assertEqual(reversed_icon.mode, "1")
                        self.assertEqual(
                            reversed_icon.tobytes(),
                            upright.transpose(Image.Transpose.ROTATE_180).tobytes(),
                        )
                        self.assertEqual(set(upright.convert("L").getdata()), {0, 255})
                        pixels.add(upright.tobytes())
                        pixels.add(reversed_icon.tobytes())
        self.assertEqual(len(pixels), 112)

    def test_card_selection_and_browser(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "gui").mkdir()
            (directory / "gui" / "icon_i.h").write_text(
                "#pragma once\nstruct Icon { unsigned id; };\n"
            )
            icons = sorted((ROOT / "images").glob("*.png"))
            (directory / "tarot_icons.h").write_text(
                "\n".join(
                    f"const struct Icon I_{icon.stem} = {{{index}}};"
                    for index, icon in enumerate(icons)
                )
            )
            (directory / "furi.h").write_text(
                "#include <stdint.h>\n"
                "static inline void furi_delay_ms(unsigned delay) { (void)delay; }\n"
            )
            (directory / "furi_hal.h").write_text(
                "static inline uint32_t furi_hal_random_get(void) { return 0; }\n"
            )
            (directory / "furi_hal_subghz.h").write_text(
                "static inline void furi_hal_subghz_reset(void) {}\n"
                "static inline void furi_hal_subghz_rx(void) {}\n"
                "static inline void furi_hal_subghz_idle(void) {}\n"
                "static inline float furi_hal_subghz_get_rssi(void) { return 0; }\n"
                "static inline void furi_hal_subghz_set_frequency(unsigned frequency) "
                "{ (void)frequency; }\n"
            )
            source = directory / "test.c"
            source.write_text(
                HARNESS
                + function_source("tarot_app_scene_on_enter_game")
                + "\n"
                + function_source("draw_deck_browser")
                + "\n"
                + function_source("deck_browser_input_callback")
                + "\n"
                + CHECKS
            )
            executable = directory / "test"
            compiler = shutil.which("cc")
            self.assertIsNotNone(compiler, "A host C compiler is required")
            subprocess.run(
                [
                    compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                    f"-I{directory}", f"-I{ROOT}", str(source), "-o", str(executable),
                ],
                check=True,
            )
            subprocess.run([str(executable)], check=True, timeout=10)


if __name__ == "__main__":
    unittest.main()
