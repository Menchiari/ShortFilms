"""The four locations. World axes: +x east, +y north. The sun sets in the west (-x).

DESERT: the dirt road comes from the east along y=0 and enters the town wall at x=0 through the only gap (|y|<7).
AVENUE: main street along x (road |y|<11), crossroads A at the origin with a N-S street (road |x|<9).
        The car dies at (0, 1) facing west. It stays there until S10.
STREETS: narrow street along x (road |y|<3.5, sidewalks to 5.5). He walks west (-x). The bar is on the north side
        at x=-30. Side street C goes south at x=-70 (road -73.5..-66.5): the fat man steps out of it.
SQUARE: square B, open x -43.5..43.5, y -31.5..31.5; the west street enters at |y|<7. He comes running east out
        of the west street and falls at the SW corner. Hero street light at (-41.6, -8.6). Helicopter pad (-12, 2).
"""
import math, random
import numpy as np
from core import *

def avenue(eye, seed=7, sky="day", clear=(), towers=True):
    rnd = random.Random(seed); mb = MB(eye); mb.excl = list(clear)
    ground(mb, -600, 600, -600, 600, PAL["asphalt"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            xa, xb = sorted((sx * 9, sx * 400)); ya, yb = sorted((sy * 11, sy * 14.5)); sidewalk(mb, xa, xb, ya, yb)
            xa, xb = sorted((sx * 9, sx * 12.5)); ya, yb = sorted((sy * 14.5, sy * 300)); sidewalk(mb, xa, xb, ya, yb)
    hr = (20, 38)
    for (bx0, bx1) in ((-260, -12.5), (12.5, 260)):
        block(mb, rnd, bx0, bx1, 14.5, 140, hr, faces="SWE")
        block(mb, rnd, bx0, bx1, -140, -14.5, hr, faces="NWE")
    for i, (x, y, w, d, h) in enumerate([(-320, 60, 24, 20, 110), (-300, -90, 30, 26, 80), (-420, 10, 20, 20, 130), (380, 70, 26, 22, 95), (-220, 210, 22, 22, 90)]):
        if towers: tower(mb, rnd, x, y, w, d, h)
    for x in range(-240, 260, 34):
        for sy in (-1, 1):
            if abs(x) > 15:
                street_light(mb, x, sy * 13.4, (x, 0), h=9)
    for x in range(-200, 220, 46):
        cable(mb, (x, -14.5, 9 + rnd.uniform(0, 3)), (x + rnd.uniform(-6, 6), 14.5, 9 + rnd.uniform(0, 3)))
    debris(mb, rnd, -200, 200, -10.5, -8, 40); debris(mb, rnd, -200, 200, 8, 10.5, 40)
    mb.build("city")
    return {"car": (0.0, 1.0), "car_facing": 90}

def desert(eye, seed=5, edge="wall"):
    """edge="towers" (draft 10): see desert_towers."""
    if edge == "towers":
        return desert_towers(eye, seed)
    rnd = random.Random(seed); mb = MB(eye, haze=(150, 900))
    ground(mb, 0, 900, -900, 900, PAL["desert"], tile=60)
    ground(mb, -900, 0, -900, 900, PAL["dirt"], tile=60)
    mb.box(0, 900, -3.5, 3.5, 0, 0.012, PAL["road_dirt"])
    mb.box(-900, 0, -7, 7, 0, 0.012, PAL["asphalt"])            # the main road runs on through the town to the horizon
    mb.box(10, 160, -16, -8, -0.01, 0.006, PAL["ditch"])
    for i in range(70):
        x = rnd.uniform(6, 120); y = rnd.uniform(8, 45); s = rnd.uniform(0.4, 2.0)
        mb.obox((x, y, s * 0.25), (s, s * 0.8, s * 0.5), rotz(rnd.uniform(0, 3)), rnd.choice([PAL["rubble"], PAL["concrete"], PAL["debris"]]))
    # the town wall: a continuous row of buildings along x in [-22, 0], one gap |y| < 7
    for (ya, yb) in ((7, 520), (-520, -7)):
        y = ya
        while y < yb - 0.1:
            w = min(rnd.uniform(10, 22), yb - y)
            building(mb, rnd, -rnd.uniform(16, 22), 0, y, y + w, rnd.uniform(14, 26), "E", "wall")
            y += w
    # inside: rising city, towers far
    for (ya, yb) in ((7, 300), (-300, -7)):
        block(mb, rnd, -560, -26, ya + (6 if ya > 0 else 0), yb - (6 if yb < 0 else 0), (22, 40), faces="SN", lot=(14, 26))
    for (x, y, w, d, h) in [(-260, 30, 26, 24, 110), (-330, -60, 30, 28, 90), (-400, 120, 22, 22, 130), (-220, -150, 24, 20, 85)]:
        tower(mb, rnd, x, y, w, d, h)
    # abandoned building and the crumbled wall, south of the road, where the dog lies
    mb.box(48, 60, -30, -20, 0, 5.5, PAL["wall_old"][1]); mb.box(48.2, 59.8, -20.05, -20.0, 1.2, 2.2, PAL["window"])
    mb.box(36, 48, -19.6, -19.2, 0, 1.4, PAL["concrete"])
    for i in range(7):
        mb.obox((36 - i * 0.6, -19.4 + i * 0.25, 0.15), (0.7, 0.4, 0.3), rotz(rnd.uniform(0, 2)), PAL["concrete"])
    mb.build("town")
    return {"stop": (7.0, 0.0), "dog": (44.5, -18.2)}

MOAT = (1.0, 5.0)                      # x range of the dry ditch along the foot of the towers
SIDE_DITCH = (5.0, 8.5, 70.0)          # |y| range and east end of the ditches along both sides of the road
DUSTY_ROAD = "#8A7457"                 # asphalt under a layer of dust
SAND = "#BC9A6C"

def _trench(mb, x0, x1, y0, y1, depth, col_wall, col_bot, slope=0.9, open_sides=""):
    """A dry ditch cut into the ground: sloped walls and a flat bottom. open_sides: sides with no wall ('NSWE')."""
    bx0, bx1, by0, by1 = x0 + ("W" not in open_sides) * slope, x1 - ("E" not in open_sides) * slope, y0 + ("S" not in open_sides) * slope, y1 - ("N" not in open_sides) * slope
    mb.box(bx0, bx1, by0, by1, -depth - 0.05, -depth, col_bot)
    z = -depth
    if "S" not in open_sides: mb.quad([(x0, y0, 0), (x1, y0, 0), (bx1, by0, z), (bx0, by0, z)], col_wall)
    if "N" not in open_sides: mb.quad([(x1, y1, 0), (x0, y1, 0), (bx0, by1, z), (bx1, by1, z)], col_wall)
    if "W" not in open_sides: mb.quad([(x0, y1, 0), (x0, y0, 0), (bx0, by0, z), (bx0, by1, z)], col_wall)
    if "E" not in open_sides: mb.quad([(x1, y0, 0), (x1, y1, 0), (bx1, by1, z), (bx1, by0, z)], col_wall)

def desert_towers(eye, seed=5):
    """Draft 10 town edge (mood_4): apartment towers shoulder to shoulder like a wall along x in [-24, 0], one gap |y| < 7.
    In front of them broken ground, rubble and a deep dry ditch (the moat, x 1..5) along the whole edge; two more ditches
    run along both sides of the road, so the only way in is the gap. The road is asphalt buried in dust and drifted sand.
    The dog's corner (crumbled wall, abandoned building) is unchanged."""
    import core as _core
    rnd = random.Random(seed); mb = MB(eye, haze=(150, 900))
    m0, m1 = MOAT; s0, s1, sx = SIDE_DITCH
    # ground around the ditches (holes left for them)
    for (x0, x1, y0, y1) in ((0, m0, -900, 900), (m0, m1, -s0, s0), (m0, m1, 520, 900), (m0, m1, -900, -520), (m1, sx, -s0, s0),
                             (m1, sx, s1, 900), (m1, sx, -900, -s1), (sx, 900, -900, 900)):
        ground(mb, x0, x1, y0, y1, PAL["desert"], tile=60)
    ground(mb, -900, 0, -900, 900, PAL["dirt"], tile=60)
    wall_c, bot_c = "#8C6E4E", PAL["ditch"]
    for sg in (1, -1):
        ya, yb = sorted((sg * s0, sg * 520)); _trench(mb, m0, m1, ya, yb, 2.4, wall_c, bot_c)
        ya, yb = sorted((sg * s0, sg * s1)); _trench(mb, m1, sx, ya, yb, 2.0, wall_c, bot_c, open_sides="W")
    # the road: dusty asphalt, sand drifted over its edges and across it in places
    mb.box(0, 900, -3.5, 3.5, 0, 0.012, DUSTY_ROAD)
    mb.box(-900, 0, -7, 7, 0, 0.012, PAL["asphalt"])
    for i in range(160):
        x = rnd.uniform(0.5, 420); L = rnd.uniform(2, 9); W = rnd.uniform(0.5, 2.2)
        y = rnd.choice((-1, 1)) * rnd.uniform(2.2, 3.6) if rnd.random() < 0.75 else rnd.uniform(-3, 3)
        if 3.0 < x < 18.0 and abs(y) < 2.0: continue                   # keep the skid lane clear of thick drifts
        mb.obox((x, y, 0.016), (L, W, 0.016), rotz(rnd.uniform(-0.25, 0.25)), SAND)
    for i in range(60):                                               # thin dust veils over the lane
        mb.obox((rnd.uniform(0.5, 300), rnd.uniform(-2.5, 2.5), 0.0135), (rnd.uniform(1.5, 5), rnd.uniform(0.6, 2.0), 0.003), rotz(rnd.uniform(-0.6, 0.6)), "#9A8160")
    # broken ground and rubble in front of the towers and beside the road (not in the ditches, not in the dog's corner)
    def free(x, y, r=0.8):
        if 34 < x < 62 and -32 < y < -12: return False
        if x < m1 + r and abs(y) > s0 - r: return False
        if x < sx + r and s0 - r < abs(y) < s1 + r: return False
        return abs(y) > 4.2
    n = 0
    while n < 420:
        x = rnd.uniform(0.0, 160) if rnd.random() < 0.8 else rnd.uniform(0.0, 12); y = rnd.choice((-1, 1)) * rnd.uniform(4.2, 90)
        if not free(x, y): continue
        k = rnd.random(); n += 1
        if k < 0.55:
            s = rnd.uniform(0.3, 1.6); mb.obox((x, y, s * 0.2), (s, s * rnd.uniform(0.5, 1.1), s * 0.45), rotz(rnd.uniform(0, 3)), rnd.choice([PAL["rubble"], PAL["concrete"], PAL["debris"]]))
        elif k < 0.75:                                                # a broken slab, tilted
            R = rotz(rnd.uniform(0, 3)) @ roty(rnd.uniform(-0.35, 0.35)); mb.obox((x, y, 0.25), (rnd.uniform(1.5, 3.5), rnd.uniform(1.0, 2.2), 0.22), R, PAL["concrete"])
        elif k < 0.92:                                                # a low mound of spoil
            s = rnd.uniform(1.5, 4.5); mb.obox((x, y, 0.1), (s, s * rnd.uniform(0.6, 1.2), rnd.uniform(0.25, 0.7)), rotz(rnd.uniform(0, 3)) @ rotx(rnd.uniform(-0.1, 0.1)), "#A4835C")
        else:                                                         # a stump of wall
            mb.obox((x, y, 0.6), (rnd.uniform(1.0, 3.0), 0.3, rnd.uniform(0.6, 1.5)), rotz(rnd.uniform(0, 3)), PAL["wall_old"][rnd.randrange(3)])
    for sg in (1, -1):                                                # rubble at the bottom of the ditches
        for i in range(70):
            y = sg * rnd.uniform(s0 + 1, 300); x = rnd.uniform(m0 + 1.0, m1 - 1.0); s = rnd.uniform(0.3, 1.0)
            mb.obox((x, y, -2.4 + s * 0.2), (s, s, s * 0.4), rotz(rnd.uniform(0, 3)), rnd.choice([PAL["rubble"], PAL["concrete"]]))
    # the edge: towers shoulder to shoulder (no laundry)
    _core.LAUNDRY = False
    try:
        for (ya, yb, sg) in ((7, 560, 1), (-560, -7, -1)):
            y = ya
            while y < yb - 0.1:
                w = min(rnd.uniform(14, 24), yb - y); g = rnd.uniform(0.3, 1.6)
                h = rnd.uniform(30, 58); d = rnd.uniform(16, 22); xf = -rnd.uniform(0.0, 1.2)
                first = (sg > 0 and y == ya) or (sg < 0 and y + w >= yb - 0.01)
                faces = "E" + (("S" if sg > 0 else "N") if first else "")
                building(mb, rnd, xf - d, xf, y + (0 if first and sg > 0 else g / 2), y + w - (0 if first and sg < 0 else g / 2), h, faces, "res")
                y += w
        for (ya, yb) in ((7, 300), (-300, -7)):
            block(mb, rnd, -560, -26, ya + (6 if ya > 0 else 0), yb - (6 if yb < 0 else 0), (26, 46), faces="SN", lot=(14, 26))
    finally:
        _core.LAUNDRY = False
    for (x, y, w, d, h) in [(-60, 40, 22, 20, 70), (-70, -38, 24, 20, 64), (-95, 90, 22, 22, 80), (-110, -95, 26, 22, 76), (-140, 20, 22, 20, 90),
                            (-150, -30, 20, 20, 84), (-60, 140, 24, 20, 62), (-75, -150, 24, 22, 68),
                            (-260, 30, 26, 24, 110), (-330, -60, 30, 28, 90), (-400, 120, 22, 22, 130), (-220, -150, 24, 20, 85)]:
        tower(mb, rnd, x, y, w, d, h)
    # abandoned building and the crumbled wall, south of the road, where the dog lies
    mb.box(48, 60, -30, -20, 0, 5.5, PAL["wall_old"][1]); mb.box(48.2, 59.8, -20.05, -20.0, 1.2, 2.2, PAL["window"])
    mb.box(36, 48, -19.6, -19.2, 0, 1.4, PAL["concrete"])
    for i in range(7):
        mb.obox((36 - i * 0.6, -19.4 + i * 0.25, 0.15), (0.7, 0.4, 0.3), rotz(rnd.uniform(0, 2)), PAL["concrete"])
    mb.build("town")
    return {"stop": (7.0, 0.0), "dog": (44.5, -18.2)}

def streets(eye, seed=3, clear=()):
    rnd = random.Random(seed); mb = MB(eye, haze=(60, 260)); mb.excl = list(clear)
    ground(mb, -400, 400, -400, 400, PAL["asphalt"], tile=30)
    sidewalk(mb, -66.5, 60, 3.5, 5.5, tile=30); sidewalk(mb, -200, -73.5, 3.5, 5.5, tile=30)
    sidewalk(mb, -66.5, 60, -5.5, -3.5, tile=30); sidewalk(mb, -200, -73.5, -5.5, -3.5, tile=30)
    sidewalk(mb, -75.5, -73.5, -200, -3.5, tile=30); sidewalk(mb, -66.5, -64.5, -200, -3.5, tile=30)
    hr = (11, 21)
    block(mb, rnd, -220, 80, 5.5, 60, hr, style="res", depth=12, faces="S", lot=(7, 12))
    block(mb, rnd, -64.5, 80, -60, -5.5, hr, style="res", depth=12, faces="NW", lot=(7, 12))
    block(mb, rnd, -220, -75.5, -60, -5.5, hr, style="res", depth=12, faces="NE", lot=(7, 12))
    # the bar: awning, plastic chairs, table on the north sidewalk at x=-30
    mb.box(-35, -25, 4.0, 5.5, 2.7, 2.85, "#7A3D33")
    mb.box(-30.6, -29.4, 4.3, 5.1, 0.7, 0.76, "#D9D4C7"); mb.cyl(-30, 4.7, 0, 0.7, 0.05, "#D9D4C7", n=6)
    for (x, y) in [(-31.4, 4.7), (-28.6, 4.7), (-30.0, 5.3)]:
        mb.box(x - 0.22, x + 0.22, y - 0.22, y + 0.22, 0.42, 0.47, "#D9D4C7"); mb.box(x - 0.22, x + 0.22, y + 0.17, y + 0.22, 0.47, 0.9, "#D9D4C7")
    # bead curtain doorway and the old woman's window
    mb.box(-9.4, -8.2, 5.48, 5.52, 0.1, 2.3, "#6B3E22")
    mb.box(-17.0, -15.2, 5.47, 5.5, 1.1, 2.3, "#22303A")
    for x in range(-110, 60, 16):
        cable(mb, (x, -5.5, 6.5 + rnd.uniform(0, 2)), (x + rnd.uniform(-3, 3), 5.5, 6.5 + rnd.uniform(0, 2)), sag=0.8)
    debris(mb, rnd, -150, 60, -3.4, -3.0, 25); debris(mb, rnd, -150, 60, 3.0, 3.4, 25)
    mb.build("city")
    return {"bar": (-30.0, 4.7), "corner": (-66.5, -5.5), "fat": (-68.5, -7.5)}

def square(eye, seed=11):
    rnd = random.Random(seed); mb = MB(eye, haze=(80, 420))
    ground(mb, -600, 600, -600, 600, PAL["asphalt"])
    # sidewalks around the square and along the streets
    sidewalk(mb, -43.5, -40, -31.5, -10.5); sidewalk(mb, -43.5, -40, 10.5, 31.5)
    sidewalk(mb, -43.5, -35.5, -10.5, -7.0)      # the corner: the street light stands on it, he hangs beside its curb
    sidewalk(mb, 40, 43.5, -31.5, -10.5); sidewalk(mb, 40, 43.5, 10.5, 31.5)
    sidewalk(mb, -40, -11.5, 28, 31.5); sidewalk(mb, 11.5, 40, 28, 31.5)
    sidewalk(mb, -40, -11.5, -31.5, -28); sidewalk(mb, 11.5, 40, -31.5, -28)
    for sx in (-1, 1):
        xa, xb = sorted((sx * 43.5, sx * 300)); sidewalk(mb, xa, xb, 7, 10.5); sidewalk(mb, xa, xb, -10.5, -7)
        for sy in (-1, 1):
            ya, yb = sorted((sy * 31.5, sy * 300)); xa, xb = sorted((sx * 8, sx * 11.5)); sidewalk(mb, xa, xb, ya, yb)
    hr = (24, 42)
    block(mb, rnd, -200, -43.5, 10.5, 140, hr, faces="SE")
    block(mb, rnd, -200, -43.5, -140, -10.5, hr, faces="NE")
    block(mb, rnd, -43.5, -11.5, 31.5, 140, hr, faces="SE")
    block(mb, rnd, 11.5, 43.5, 31.5, 140, hr, faces="SW")
    block(mb, rnd, 43.5, 200, 10.5, 140, hr, faces="SW")
    block(mb, rnd, 43.5, 200, -140, -10.5, hr, faces="NW")
    block(mb, rnd, -43.5, -11.5, -140, -31.5, hr, faces="NE")
    block(mb, rnd, 11.5, 43.5, -140, -31.5, hr, faces="NW")
    for (x, y, w, d, h) in [(-230, 120, 26, 24, 120), (160, 190, 30, 26, 100), (250, -60, 24, 22, 135), (-180, -200, 26, 26, 95), (60, 260, 22, 22, 85)]:
        tower(mb, rnd, x, y, w, d, h)
    # central island with palms, east of the landing area
    mb.cyl(22, 4, 0, 0.35, 8, PAL["curb"], n=24); mb.cyl(22, 4, 0.35, 0.4, 7.6, PAL["rubble"], n=24)
    hero = street_light(mb, -41.6, -8.6, (-36.0, -3.0), h=8.6, arm=2.8)
    for (x, y, tx, ty) in [(-41.6, 9.0, -36, 6), (-20, 29.8, -20, 20), (5, 29.8, 5, 20), (30, 29.8, 30, 20), (41.6, 18, 30, 18),
                           (41.6, -18, 30, -18), (30, -29.8, 30, -20), (-20, -29.8, -20, -20), (5, -29.8, 5, -20), (-60, 8.8, -60, 0), (-85, -8.8, -85, 0)]:
        street_light(mb, x, y, (tx, ty), h=8.6)
    for x in range(-150, -50, 18):
        cable(mb, (x, -10.5, 10 + rnd.uniform(0, 3)), (x + rnd.uniform(-5, 5), 10.5, 10 + rnd.uniform(0, 3)))
    debris(mb, rnd, -38, 38, -27, -18, 26); debris(mb, rnd, -38, 38, 18, 27, 26); debris(mb, rnd, 25, 40, -15, 15, 10)
    mb.build("city")
    return {"hero_arm": hero, "pad": (-12.0, 2.0), "case": (-50.0, -2.2), "fall": (-39.0, -6.0)}
