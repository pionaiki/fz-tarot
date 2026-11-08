"""Reproduce the minor arcana PNGs. Requires Pillow; not needed to build the app.

The artwork is hand-authored pixel art stored as ASCII maps ("#" is black).
Cards follow the conventions of the original major arcana: a 23x32 frame
with rounded corners, a three-pixel label in the header, a divider on row 6
and a 21x24 illustration area. Reversed cards are 180-degree rotations.
"""

import math
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SUITS = ("cups", "swords", "wands", "pentacles")
WIDTH, HEIGHT = 23, 32
ART_LEFT, ART_TOP, ART_WIDTH, ART_HEIGHT = 1, 7, 21, 24
LABELS = (
    "A", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "P", "KN", "Q", "K"
)
GLYPHS = {
    "A": (".#.", "###", "#.#"),
    "I": ("#", "#", "#"),
    "V": ("#.#", "#.#", ".#."),
    "X": ("#.#", ".#.", "#.#"),
    "P": ("##", "##", "#."),
    "N": ("##.#", "#.##", "#..#"),
    "Q": ("###.", "#.#.", "####"),
    "K": ("#.#", "##.", "#.#"),
}

# Small suit emblems for the numbered cards (5x5).
PIPS = {
    "cups": ("#####", "#####", ".###.", "..#..", ".###."),
    "swords": ("...##", "..###", "#.##.", ".#...", "#.#.."),
    "wands": ("..#.#", "...##", "..##.", ".##..", "##..."),
    "pentacles": (".###.", "#.#.#", "##.##", "#.#.#", ".###."),
}
# Pip centres in illustration coordinates.
_SIDES_3 = ((4, 4), (16, 4), (4, 12), (16, 12), (4, 20), (16, 20))
_SIDES_4 = ((4, 2), (16, 2), (4, 8), (16, 8), (4, 14), (16, 14), (4, 20), (16, 20))
PIP_LAYOUTS = {
    2: ((10, 6), (10, 18)),
    3: ((10, 4), (10, 12), (10, 20)),
    4: ((4, 6), (16, 6), (4, 18), (16, 18)),
    5: ((4, 6), (16, 6), (10, 12), (4, 18), (16, 18)),
    6: _SIDES_3,
    7: _SIDES_3 + ((10, 8),),
    8: _SIDES_3 + ((10, 8), (10, 16)),
    9: _SIDES_4 + ((10, 11),),
    10: _SIDES_4 + ((10, 5), (10, 17)),
}

# Suit objects held by court figures, with the grip pixel (column, row).
HELD = {
    "cups": (("#####", "#####", ".###.", "..#..", ".###."), (2, 4)),
    "swords": ((".#.", ".#.", ".#.", ".#.", ".#.", ".#.", ".#.", "###",
                ".#.", ".#.", ".#."), (1, 9)),
    "wands": (("#.#", ".#.", ".##", ".#.", "##.", ".#.", ".#.", ".##",
               ".#.", ".#.", ".#.", ".#."), (1, 9)),
    "pentacles": (("..###..", ".#.#.#.", "#.###.#", "#..#..#", "#.#.#.#",
                   ".#...#.", "..###.."), (3, 6)),
}

ACES = {
    "cups": (
        "..........#..........",
        ".........#.#.........",
        "......#...#...#......",
        ".....#.#.....#.#.....",
        "...###############...",
        "...#.............#...",
        "...###############...",
        "....#############....",
        "....##.#######.##....",
        ".....###########.....",
        "......#########......",
        ".......#######.......",
        ".........###.........",
        "..........#..........",
        "..........#..........",
        ".........###.........",
        "..........#..........",
        "..........#..........",
        ".......#######.......",
        "......#########......",
        ".....................",
        "..##.............##..",
        ".#..#...........#..#.",
        ".....................",
    ),
    "swords": (
        "..........#..........",
        ".........#.#.........",
        ".....#.#.#.#.#.#.....",
        ".....###########.....",
        "......#########......",
        "....#....#.#....#....",
        "...#.#...#.#...#.#...",
        "....#....#.#....#....",
        "...#.#...#.#...#.#...",
        ".........#.#.........",
        ".........#.#.........",
        ".........#.#.........",
        ".........#.#.........",
        ".........#.#.........",
        "..#################..",
        "..#.......#.......#..",
        ".........###.........",
        ".........###.........",
        ".........###.........",
        "........#####........",
        ".........###.........",
        ".....................",
        ".....................",
        ".....................",
    ),
    "wands": (
        "............#.#.#....",
        ".............#.#.....",
        ".............###.....",
        ".............######..",
        "............###.##...",
        "............####.....",
        "...#.......###.......",
        "....#.###..###.......",
        ".......##.###........",
        ".........####........",
        ".........###.........",
        ".........######...#..",
        "........###.##...#...",
        "........####.........",
        ".......###...........",
        "..###..###...........",
        "...##.###............",
        ".....####............",
        ".....###.............",
        ".....###........#....",
        "....###..........#...",
        "....###..............",
        "...###...............",
        "#.#.#.#.#.#.#.#.#.#.#",
    ),
}

COURTS = {
    11: ((
        ".....................",
        ".........###..#......",
        "........#####.#......",
        ".......#######.......",
        "........#...#........",
        "........#...#........",
        ".........###.........",
        ".......#######.......",
        "......#.#####.#......",
        "......#.#####..##....",
        ".....##.#####........",
        "........#####........",
        ".......#######.......",
        "......#########......",
        "......#########......",
        "........#...#........",
        "........#...#........",
        "........#...#........",
        "........#...#........",
        "........#...#........",
        ".......##...##.......",
        ".....................",
        "#.#.#.#.#.#.#.#.#.#.#",
        "#####################",
    ), (16, 9)),
    12: ((
        "...........#.#.......",
        "..........###........",
        "..........#.#........",
        "..........###........",
        ".........#####.......",
        "........#.###.#......",
        ".....#.#..###..#.....",
        "....####..###........",
        "...##.###.###........",
        "..#######.####.......",
        ".####..###.####......",
        ".###....##########.##",
        ".......############.#",
        ".......####.#######.#",
        ".......####.#######.#",
        "........###.######..#",
        "........##########...",
        "........#.#....#.#...",
        "........#.#....#.#...",
        ".......#..#....#..#..",
        ".......#..#....#..#..",
        "......##.##...##.##..",
        "#.#.#.#.#.#.#.#.#.#.#",
        "#####################",
    ), (15, 6)),
    13: ((
        "..#.....#.#.#.....#..",
        ".###....#####....###.",
        "..#....#######....#..",
        "..#...##.....##...#..",
        "..#...##.#.#.##...#..",
        "..#...##.....##...#..",
        "..#..###..#..###..#..",
        "..#..####...####..#..",
        "..#..##.#####.##..#..",
        "..#.##.#######.##.#..",
        "..#.#.#########.#.#..",
        "..#.#..#######..#.#..",
        "..####.#######.####..",
        "..#...#########...#..",
        "..#..###########..#..",
        "..#.#############.#..",
        "..#################..",
        "..##.###########.##..",
        "..#..###########..#..",
        "..#.#############.#..",
        "..#.#############.#..",
        "..#################..",
        ".###################.",
        ".....................",
    ), (16, 12)),
    14: ((
        ".....................",
        "...#..#.#.#.#.#..#...",
        "..###.#########.###..",
        "...#..##.###.##..#...",
        "...#...#.....#...#...",
        "...#...#.#.#.#...#...",
        "...#...#.....#...#...",
        "...#...#######...#...",
        "...#...##.#.##...#...",
        "...#.###.###.###.#...",
        "...###############...",
        "...##.#########.##...",
        "...#.#.#######.#.#...",
        "..###.#.#####.#.###..",
        "..#.#.#########.#.#..",
        "..#.#.#########.#.#..",
        "..#.#.####.####.#.#..",
        "..#####.##.##.#####..",
        "..#.....##.##.....#..",
        "..#.....##.##.....#..",
        "..#....###.###....#..",
        ".###################.",
        ".#.................#.",
        "#####################",
    ), (16, 13)),
}


class Canvas:
    def __init__(self):
        self.pixels = [[False] * WIDTH for _ in range(HEIGHT)]

    def set(self, x, y, black=True):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.pixels[y][x] = black

    def stamp(self, rows, left, top, halo=False):
        cells = [
            (left + column, top + row)
            for row, line in enumerate(rows)
            for column, pixel in enumerate(line)
            if pixel == "#"
        ]
        if halo:
            occupied = set(cells)
            for x, y in cells:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    neighbour = (x + dx, y + dy)
                    if neighbour not in occupied:
                        self.set(*neighbour, black=False)
        for x, y in cells:
            self.set(x, y)

    def image(self):
        image = Image.new("1", (WIDTH, HEIGHT), 1)
        for y, row in enumerate(self.pixels):
            for x, black in enumerate(row):
                if black:
                    image.putpixel((x, y), 0)
        return image


def check(rows, width, height, name):
    if len(rows) != height or any(len(row) != width for row in rows):
        raise ValueError(f"{name} must be {width}x{height}")


def frame(canvas, text):
    for x in range(1, WIDTH - 1):
        canvas.set(x, 0)
        canvas.set(x, HEIGHT - 1)
    for y in range(1, HEIGHT - 1):
        canvas.set(0, y)
        canvas.set(WIDTH - 1, y)
    for x in range(WIDTH):
        canvas.set(x, 6)
    width = sum(len(GLYPHS[letter][0]) + 1 for letter in text) - 1
    left = (WIDTH - width) // 2
    for letter in text:
        canvas.stamp(GLYPHS[letter], left, 2)
        left += len(GLYPHS[letter][0]) + 1


def art(canvas, rows, name):
    check(rows, ART_WIDTH, ART_HEIGHT, name)
    canvas.stamp(rows, ART_LEFT, ART_TOP)


def line(canvas, start, end):
    (x0, y0), (x1, y1) = start, end
    steps = max(abs(x1 - x0), abs(y1 - y0))
    for step in range(steps + 1):
        canvas.set(
            round(x0 + (x1 - x0) * step / steps), round(y0 + (y1 - y0) * step / steps)
        )


def ace_of_pentacles(canvas):
    centre_x, centre_y, radius = 11, 17, 8
    for y in range(HEIGHT):
        for x in range(WIDTH):
            distance = math.hypot(x - centre_x, y - centre_y)
            if radius - 0.5 <= distance < radius + 0.5:
                canvas.set(x, y)
    points = [
        (
            round(centre_x + 6 * math.sin(math.radians(angle))),
            round(centre_y - 6 * math.cos(math.radians(angle))),
        )
        for angle in range(0, 360, 72)
    ]
    for index, point in enumerate(points):
        line(canvas, point, points[(index + 2) % 5])
    for x, y in ((11, 7), (3, 9), (19, 9), (2, 17), (20, 17)):
        canvas.set(x, y)
    canvas.stamp(("..#.....#.....#..", ".#.#...#.#...#.#.", "..#.....#.....#.."), 3, 26)
    canvas.stamp(("#.#.#.#.#.#.#.#.#.#.#",), 1, 29)


def make_card(suit, rank):
    canvas = Canvas()
    frame(canvas, LABELS[rank - 1])
    name = f"minor_{suit}_{rank}"
    if rank == 1 and suit == "pentacles":
        ace_of_pentacles(canvas)
    elif rank == 1:
        art(canvas, ACES[suit], name)
    elif rank <= 10:
        pip = PIPS[suit]
        check(pip, 5, 5, suit)
        for centre_x, centre_y in PIP_LAYOUTS[rank]:
            canvas.stamp(pip, ART_LEFT + centre_x - 2, ART_TOP + centre_y - 2)
    else:
        figure, (hand_x, hand_y) = COURTS[rank]
        art(canvas, figure, name)
        held, (grip_x, grip_y) = HELD[suit]
        canvas.stamp(
            held, ART_LEFT + hand_x - grip_x, ART_TOP + hand_y - grip_y, halo=True
        )
    return canvas.image()


def main():
    for suit in SUITS:
        for rank in range(1, 15):
            image = make_card(suit, rank)
            stem = f"minor_{suit}_{rank}"
            image.save(ROOT / "images" / f"{stem}.png")
            image.transpose(Image.Transpose.ROTATE_180).save(
                ROOT / "images" / f"{stem}_.png"
            )
    print("Generated 56 upright and 56 reversed minor arcana icons.")


if __name__ == "__main__":
    main()
