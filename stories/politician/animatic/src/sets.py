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

def avenue(eye, seed=7, sky="day", clear=()):
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
        tower(mb, rnd, x, y, w, d, h)
    for x in range(-240, 260, 34):
        for sy in (-1, 1):
            if abs(x) > 15:
                street_light(mb, x, sy * 13.4, (x, 0), h=9)
    for x in range(-200, 220, 46):
        cable(mb, (x, -14.5, 9 + rnd.uniform(0, 3)), (x + rnd.uniform(-6, 6), 14.5, 9 + rnd.uniform(0, 3)))
    debris(mb, rnd, -200, 200, -10.5, -8, 40); debris(mb, rnd, -200, 200, 8, 10.5, 40)
    for x in range(-220, 240, 28):
        if abs(x) > 20 and rnd.random() < 0.6:
            palm(mb, rnd, x + rnd.uniform(-4, 4), rnd.choice([-13.2, 13.2]))
    mb.build("city")
    return {"car": (0.0, 1.0), "car_facing": 90}

def desert(eye, seed=5):
    rnd = random.Random(seed); mb = MB(eye, haze=(150, 900))
    ground(mb, 0, 900, -900, 900, PAL["desert"], tile=60)
    ground(mb, -900, 0, -900, 900, PAL["dirt"], tile=60)
    mb.box(0, 900, -3.5, 3.5, 0, 0.012, PAL["road_dirt"])
    mb.box(-60, 0, -7, 7, 0, 0.012, PAL["asphalt"])
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
        block(mb, rnd, -160, -26, ya + (6 if ya > 0 else 0), yb - (6 if yb < 0 else 0), (22, 40), faces="SN", lot=(14, 26))
    block(mb, rnd, -300, -170, -260, 260, (26, 48), faces="E", lot=(16, 30))
    for (x, y, w, d, h) in [(-260, 30, 26, 24, 110), (-330, -60, 30, 28, 90), (-400, 120, 22, 22, 130), (-220, -150, 24, 20, 85)]:
        tower(mb, rnd, x, y, w, d, h)
    # abandoned building and the crumbled wall, south of the road, where the dog lies
    mb.box(48, 60, -30, -20, 0, 5.5, PAL["wall_old"][1]); mb.box(48.2, 59.8, -20.05, -20.0, 1.2, 2.2, PAL["window"])
    mb.box(36, 48, -19.6, -19.2, 0, 1.4, PAL["concrete"])
    for i in range(7):
        mb.obox((36 - i * 0.6, -19.4 + i * 0.25, 0.15), (0.7, 0.4, 0.3), rotz(rnd.uniform(0, 2)), PAL["concrete"])
    mb.build("town")
    return {"stop": (40.0, 0.0), "dog": (44.5, -18.2)}

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
    mb.cyl(22, 4, 0, 0.35, 8, PAL["curb"], n=24); mb.cyl(22, 4, 0.35, 0.4, 7.6, PAL["frond"], n=24)
    for i in range(6):
        a = i * math.pi / 3; palm(mb, rnd, 22 + 5 * math.cos(a), 4 + 5 * math.sin(a))
    hero = street_light(mb, -41.6, -8.6, (-36.0, -3.0), h=8.6, arm=2.8)
    for (x, y, tx, ty) in [(-41.6, 9.0, -36, 6), (-20, 29.8, -20, 20), (5, 29.8, 5, 20), (30, 29.8, 30, 20), (41.6, 18, 30, 18),
                           (41.6, -18, 30, -18), (30, -29.8, 30, -20), (-20, -29.8, -20, -20), (5, -29.8, 5, -20), (-60, 8.8, -60, 0), (-85, -8.8, -85, 0)]:
        street_light(mb, x, y, (tx, ty), h=8.6)
    for x in range(-150, -50, 18):
        cable(mb, (x, -10.5, 10 + rnd.uniform(0, 3)), (x + rnd.uniform(-5, 5), 10.5, 10 + rnd.uniform(0, 3)))
    debris(mb, rnd, -38, 38, -27, -18, 26); debris(mb, rnd, -38, 38, 18, 27, 26); debris(mb, rnd, 25, 40, -15, 15, 10)
    for (x, y) in [(-30, 25), (35, -25), (34, 24)]:
        palm(mb, rnd, x, y)
    mb.build("city")
    return {"hero_arm": hero, "pad": (-12.0, 2.0), "case": (-50.0, -2.2), "fall": (-39.0, -6.0)}
