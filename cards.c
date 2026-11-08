#include <gui/icon_i.h>
#include "cards.h"
#include <tarot_icons.h>
#include <stdlib.h>
#include <stddef.h>
#include <furi.h>
#include <furi_hal.h>
#include <furi_hal_subghz.h>

#define TAROT_DECK(ENTRY)                            \
    ENTRY("The Fool", major_0)                       \
    ENTRY("The Magician", major_1)                   \
    ENTRY("The High Priestess", major_2)             \
    ENTRY("The Empress", major_3)                    \
    ENTRY("The Emperor", major_4)                    \
    ENTRY("The Hierophant", major_5)                 \
    ENTRY("The Lovers", major_6)                     \
    ENTRY("The Chariot", major_7)                    \
    ENTRY("Strength", major_8)                       \
    ENTRY("The Hermit", major_9)                     \
    ENTRY("Wheel of Fortune", major_10)              \
    ENTRY("Justice", major_11)                       \
    ENTRY("The Hanged Man", major_12)                \
    ENTRY("Death", major_13)                         \
    ENTRY("Temperance", major_14)                    \
    ENTRY("The Devil", major_15)                     \
    ENTRY("The Tower", major_16)                     \
    ENTRY("The Star", major_17)                      \
    ENTRY("The Moon", major_18)                      \
    ENTRY("The Sun", major_19)                       \
    ENTRY("Judgement", major_20)                     \
    ENTRY("The World", major_21)                     \
    ENTRY("Ace of Cups", minor_cups_1)               \
    ENTRY("2 of Cups", minor_cups_2)                 \
    ENTRY("3 of Cups", minor_cups_3)                 \
    ENTRY("4 of Cups", minor_cups_4)                 \
    ENTRY("5 of Cups", minor_cups_5)                 \
    ENTRY("6 of Cups", minor_cups_6)                 \
    ENTRY("7 of Cups", minor_cups_7)                 \
    ENTRY("8 of Cups", minor_cups_8)                 \
    ENTRY("9 of Cups", minor_cups_9)                 \
    ENTRY("10 of Cups", minor_cups_10)               \
    ENTRY("Page of Cups", minor_cups_11)             \
    ENTRY("Knight of Cups", minor_cups_12)           \
    ENTRY("Queen of Cups", minor_cups_13)            \
    ENTRY("King of Cups", minor_cups_14)             \
    ENTRY("Ace of Swords", minor_swords_1)           \
    ENTRY("2 of Swords", minor_swords_2)             \
    ENTRY("3 of Swords", minor_swords_3)             \
    ENTRY("4 of Swords", minor_swords_4)             \
    ENTRY("5 of Swords", minor_swords_5)             \
    ENTRY("6 of Swords", minor_swords_6)             \
    ENTRY("7 of Swords", minor_swords_7)             \
    ENTRY("8 of Swords", minor_swords_8)             \
    ENTRY("9 of Swords", minor_swords_9)             \
    ENTRY("10 of Swords", minor_swords_10)           \
    ENTRY("Page of Swords", minor_swords_11)         \
    ENTRY("Knight of Swords", minor_swords_12)       \
    ENTRY("Queen of Swords", minor_swords_13)        \
    ENTRY("King of Swords", minor_swords_14)         \
    ENTRY("Ace of Wands", minor_wands_1)             \
    ENTRY("2 of Wands", minor_wands_2)               \
    ENTRY("3 of Wands", minor_wands_3)               \
    ENTRY("4 of Wands", minor_wands_4)               \
    ENTRY("5 of Wands", minor_wands_5)               \
    ENTRY("6 of Wands", minor_wands_6)               \
    ENTRY("7 of Wands", minor_wands_7)               \
    ENTRY("8 of Wands", minor_wands_8)               \
    ENTRY("9 of Wands", minor_wands_9)               \
    ENTRY("10 of Wands", minor_wands_10)             \
    ENTRY("Page of Wands", minor_wands_11)           \
    ENTRY("Knight of Wands", minor_wands_12)         \
    ENTRY("Queen of Wands", minor_wands_13)          \
    ENTRY("King of Wands", minor_wands_14)           \
    ENTRY("Ace of Pentacles", minor_pentacles_1)     \
    ENTRY("2 of Pentacles", minor_pentacles_2)       \
    ENTRY("3 of Pentacles", minor_pentacles_3)       \
    ENTRY("4 of Pentacles", minor_pentacles_4)       \
    ENTRY("5 of Pentacles", minor_pentacles_5)       \
    ENTRY("6 of Pentacles", minor_pentacles_6)       \
    ENTRY("7 of Pentacles", minor_pentacles_7)       \
    ENTRY("8 of Pentacles", minor_pentacles_8)       \
    ENTRY("9 of Pentacles", minor_pentacles_9)       \
    ENTRY("10 of Pentacles", minor_pentacles_10)     \
    ENTRY("Page of Pentacles", minor_pentacles_11)   \
    ENTRY("Knight of Pentacles", minor_pentacles_12) \
    ENTRY("Queen of Pentacles", minor_pentacles_13)  \
    ENTRY("King of Pentacles", minor_pentacles_14)

#define UPRIGHT_CARD(name, image) {name, &I_##image},
#define REVERSED_CARD(name, image) {name, &I_##image##_},

const Card card[] = {TAROT_DECK(UPRIGHT_CARD) TAROT_DECK(REVERSED_CARD)};
const int card_number = sizeof(card) / sizeof(card[0]) / 2;

#undef REVERSED_CARD
#undef UPRIGHT_CARD
#undef TAROT_DECK

static uint32_t radio_noise_entropy()
{
    furi_hal_subghz_reset();
    furi_hal_subghz_set_frequency(433920000); // ISM band
    furi_hal_subghz_rx();
    uint32_t entropy = 0;
    for (int i = 0; i < 32; ++i)
    {
        furi_delay_ms(2);
        float rssi = furi_hal_subghz_get_rssi();
        // Use the lowest bit of the mantissa for entropy
        uint32_t bit = ((uint32_t)(rssi * 1000)) & 0x01;
        entropy = (entropy << 1) ^ bit;
    }
    furi_hal_subghz_idle();
    return entropy;
}

uint16_t unbiased_rand(uint16_t max)
{
    if (max == 0)
        return 0;
    uint32_t x, remainder = UINT32_MAX % max;
    do
    {
        x = furi_hal_random_get() ^ radio_noise_entropy();
    } while (x >= UINT32_MAX - remainder);
    return x % max;
}

int get_total_card_count(void)
{
    return card_number;
}
