"""Animatic v2 core: render setup, materials with distance haze, a fast mesh builder, Cairo-style city sets."""
import bpy, math, random
import numpy as np
from mathutils import Matrix, Vector

FPS = 12
W, H = 1120, 480

def srgb(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)

SKY = {"day": "#E9D3A8", "warm": "#E8BE8C", "sunset": "#E59A63", "cabin": "#E59A63"}
PAL = {
    "wall": ["#A9825A", "#B8915F", "#9A7650", "#C4A074", "#8E6C4C", "#B39573", "#A48A68", "#9C6F4A"],
    "wall_old": ["#7E5E42", "#86654A", "#735740"],
    "window": "#2B2219", "frame": "#5A4634", "balcony": "#8A6A4A", "shutter": "#6A5642", "shutter2": "#5B4E44",
    "awning": ["#7A6450", "#6B5F52", "#857260", "#5E564C"],
    "asphalt": "#7E6850", "sidewalk": "#98805F", "curb": "#A08A6B", "dirt": "#A07F58", "desert": "#B48D60",
    "road_dirt": "#9C7A52", "ditch": "#6E5338", "rubble": "#8E7656", "pole": "#3A3530", "palm": "#5E4B39",
    "frond": "#55603F", "tank": "#2E2E2E", "tank2": "#BDBAB2", "dish": "#C9C4B8", "sign": ["#6E6258", "#5C5650", "#7A6A5A"],
    "laundry": ["#C9C2B0", "#8E3B36", "#3D5C7A", "#C8A85A", "#6F7F5A"], "cable": "#2A2622", "tower": "#9C8C78",
    "concrete": "#8F8676", "debris": "#5F5244", "tire": "#1E1C1A", "car": "#141414", "carglass": "#3B4148",
    "seat": "#D8CDB5", "heli": "#EDEDEA", "heli_dark": "#2A2A2C", "rope": "#C2A878",
}

class Mats:
    """Material cache: (hex, haze level) -> material. Workbench MATERIAL color mode reads diffuse_color."""
    def __init__(self, sky="day", levels=8):
        self.cache = {}; self.sky = tuple(v * 0.55 for v in srgb(SKY[sky])); self.levels = levels
    def get(self, hexcol, haze=0):
        key = (hexcol, haze)
        if key not in self.cache:
            c = srgb(hexcol); k = min(0.85, haze * 0.11)
            col = tuple(c[i] * (1 - k) + self.sky[i] * k for i in range(3))
            m = bpy.data.materials.new(f"m_{hexcol}_{haze}"); m.diffuse_color = (*col, 1)
            self.cache[key] = m
        return self.cache[key]

MATS = None
SIDEWALKS = []

def ground_z(x, y):
    """Height of the ground under (x, y): 0.15 on a sidewalk, 0 elsewhere."""
    for (x0, x1, y0, y1) in SIDEWALKS:
        if x0 <= x <= x1 and y0 <= y <= y1:
            return 0.15
    return 0.0

def reset(sky="day", light=(0.55, -0.35, 0.75)):
    global MATS
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.render.fps = FPS
    sh = sc.display.shading
    sh.light = "STUDIO"; sh.studio_light = "Default"; sh.use_world_space_lighting = True; sh.studiolight_rotate_z = math.radians(200)
    sh.color_type = "MATERIAL"; sh.show_shadows = False
    sh.show_cavity = True; sh.cavity_type = "WORLD"; sh.cavity_ridge_factor = 0.6; sh.cavity_valley_factor = 1.0
    sh.background_type = "WORLD"
    w = bpy.data.worlds.new("W"); w.color = tuple(v * 0.55 for v in srgb(SKY[sky])); sc.world = w
    sc.display.light_direction = light
    sc.display.shadow_shift = 0.02; sc.display.shadow_focus = 0.0
    sc.view_settings.view_transform = "Standard"; sc.view_settings.exposure = 0.9
    sc.render.image_settings.file_format = "PNG"
    MATS = Mats(sky)
    SIDEWALKS.clear()
    return sc

# ------------------------------------------------------------------ mesh builder
class MB:
    """Accumulates boxes/quads/cylinders with per-face material keys, then builds one mesh object."""
    def __init__(self, eye=None, haze=(90, 520), detail=True):
        self.v = []; self.f = []; self.m = []; self.mkeys = {}; self.eye = eye; self.haze = haze
        self.d = MB(eye, haze, detail=False) if detail else None
        self.excl = []
    def excluded(self, x, y, z):
        return any(math.dist((x, y, z), c[:3]) < c[3] for c in self.excl)
    def far(self, x, y, lim=240):
        return self.eye is not None and math.dist(self.eye[:2], (x, y)) > lim
    def _mi(self, hexcol, pos):
        lvl = 0
        if self.eye is not None and pos is not None:
            d = math.dist(self.eye[:2], pos[:2])
            lvl = int(max(0, min(MATS.levels - 1, (d - self.haze[0]) / (self.haze[1] - self.haze[0]) * MATS.levels)))
        key = (hexcol, lvl)
        if key not in self.mkeys:
            self.mkeys[key] = len(self.mkeys)
        return self.mkeys[key]
    def box(self, x0, x1, y0, y1, z0, z1, col, at=None):
        mi = self._mi(col, at or ((x0 + x1) / 2, (y0 + y1) / 2))
        b = len(self.v)
        self.v += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.f.append(tuple(b + i for i in q)); self.m.append(mi)
    def quad(self, pts, col, at=None):
        mi = self._mi(col, at or pts[0]); b = len(self.v)
        self.v += list(pts); self.f.append((b, b + 1, b + 2, b + 3)); self.m.append(mi)
    def obox(self, center, size, R, col, at=None):
        """Oriented box: R is a 3x3 numpy rotation."""
        mi = self._mi(col, at or center)
        sx, sy, sz = [s / 2 for s in size]; c = np.array(center); b = len(self.v)
        for (x, y, z) in ((-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz), (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)):
            self.v.append(tuple(c + R @ np.array((x, y, z))))
        for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.f.append(tuple(b + i for i in q)); self.m.append(mi)
    def cyl(self, cx, cy, z0, z1, r, col, n=10, r2=None, at=None):
        mi = self._mi(col, at or (cx, cy)); b = len(self.v); r2 = r if r2 is None else r2
        for i in range(n):
            a = 2 * math.pi * i / n
            self.v.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
        for i in range(n):
            a = 2 * math.pi * i / n
            self.v.append((cx + r2 * math.cos(a), cy + r2 * math.sin(a), z1))
        for i in range(n):
            j = (i + 1) % n
            self.f.append((b + i, b + j, b + n + j, b + n + i)); self.m.append(mi)
        self.f.append(tuple(b + i for i in reversed(range(n)))); self.m.append(mi)
        self.f.append(tuple(b + n + i for i in range(n))); self.m.append(mi)
    def build(self, name):
        if self.d is not None:
            od = self.d.build(name + "_detail")
            if od is not None:
                od.visible_shadow = False
        if not self.f:
            return None
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        inv = sorted(self.mkeys.items(), key=lambda kv: kv[1])
        for (hexcol, lvl), _ in inv:
            me.materials.append(MATS.get(hexcol, lvl))
        me.polygons.foreach_set("material_index", self.m)
        me.update()
        o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
        return o

def rotz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array(((c, -s, 0), (s, c, 0), (0, 0, 1)))

def rotx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array(((1, 0, 0), (0, c, -s), (0, s, c)))

def roty(a):
    c, s = math.cos(a), math.sin(a)
    return np.array(((c, 0, s), (0, 1, 0), (-s, 0, c)))

# ------------------------------------------------------------------ buildings
def facade(mb, rnd, side, x0, x1, y0, y1, h, style, ground_shop=True):
    """Detail the face of a building box on `side` ('S','N','W','E'). Facade-local: u along the face, v up, w outward."""
    md = mb.d or mb
    if side in "SN":
        u0, u1 = x0, x1; base = y0 if side == "S" else y1; sgn = -1 if side == "S" else 1
        def B(ua, ub, va, vb, wa, wb, col):
            if mb.excluded((ua + ub) / 2, base, (va + vb) / 2): return
            ya, yb = sorted((base + sgn * wa, base + sgn * wb)); mb.box(ua, ub, ya, yb, va, vb, col, at=((ua + ub) / 2, base))
        def Q(ua, ub, va, vb, col):
            y = base + sgn * 0.03
            pts = [(ua, y, va), (ub, y, va), (ub, y, vb), (ua, y, vb)] if sgn < 0 else [(ub, y, va), (ua, y, va), (ua, y, vb), (ub, y, vb)]
            md.quad(pts, col, at=((ua + ub) / 2, base))
    else:
        u0, u1 = y0, y1; base = x0 if side == "W" else x1; sgn = -1 if side == "W" else 1
        def B(ua, ub, va, vb, wa, wb, col):
            if mb.excluded(base, (ua + ub) / 2, (va + vb) / 2): return
            xa, xb = sorted((base + sgn * wa, base + sgn * wb)); mb.box(xa, xb, ua, ub, va, vb, col, at=(base, (ua + ub) / 2))
        def Q(ua, ub, va, vb, col):
            x = base + sgn * 0.03
            pts = [(x, ub, va), (x, ua, va), (x, ua, vb), (x, ub, vb)] if sgn < 0 else [(x, ua, va), (x, ub, va), (x, ub, vb), (x, ua, vb)]
            md.quad(pts, col, at=(base, (ua + ub) / 2))
    if mb.far((x0 + x1) / 2, (y0 + y1) / 2, 260):
        return
    L = u1 - u0
    if style == "wall":
        fh = 3.0; floors = int(h // fh)
        cols = max(1, int(L / 4.5))
        for fl in range(1, floors):
            for c in range(cols):
                if rnd.random() < 0.55:
                    uc = u0 + (c + 0.5) * L / cols
                    Q(uc - 0.4, uc + 0.4, fl * fh + 1.0, fl * fh + 1.9, PAL["window"])
        return
    fh = 3.3 if style == "downtown" else 3.0
    gf = 4.2 if style == "downtown" else 3.2
    floors = max(1, int((h - gf) // fh))
    pitch = rnd.choice([2.3, 2.6, 3.0]) if style == "downtown" else rnd.choice([3.0, 3.4, 3.8])
    cols = max(1, int((L - 1.0) // pitch))
    pad = (L - cols * pitch) / 2
    bal = rnd.random() < (0.6 if style == "downtown" else 0.75)
    bal_every = rnd.choice([1, 2, 2, 3])
    ww = 1.1 if style == "downtown" else 1.3
    wh = 1.9 if style == "downtown" else 1.4
    wcol = rnd.choice(PAL["wall"])
    for fl in range(floors):
        vz = gf + fl * fh
        for c in range(cols):
            uc = u0 + pad + (c + 0.5) * pitch
            Q(uc - ww / 2, uc + ww / 2, vz + 0.6, vz + 0.6 + wh, PAL["window"])
            if bal and c % bal_every == 0 and fl < floors:
                bw = pitch * bal_every - 0.4 if bal_every > 1 else pitch - 0.3
                ub = uc - ww / 2 - 0.15
                B(ub, ub + bw, vz, vz + 0.14, 0, 1.0, PAL["balcony"])
                B(ub, ub + bw, vz + 0.14, vz + 1.0, 0.92, 1.0, PAL["balcony"])
                if rnd.random() < 0.18:
                    lc = rnd.choice(PAL["laundry"])
                    B(ub + 0.3, ub + 0.9, vz + 0.5, vz + 1.1, 1.02, 1.05, lc)
            elif rnd.random() < 0.12:
                B(uc + ww / 2 + 0.1, uc + ww / 2 + 0.9, vz + 0.5, vz + 1.0, 0, 0.45, "#B9B3A6")   # AC unit
        if style == "downtown" and fl % 3 == 0:
            B(u0, u1, vz - 0.12, vz + 0.06, 0, 0.18, PAL["frame"])
    # cornice and pilasters
    B(u0 - 0.2, u1 + 0.2, h - 0.5, h, 0, 0.45, PAL["frame"])
    if style == "downtown":
        B(u0, u0 + 0.5, gf, h - 0.5, 0, 0.12, PAL["frame"]); B(u1 - 0.5, u1, gf, h - 0.5, 0, 0.12, PAL["frame"])
    # ground floor shops
    if ground_shop:
        shops = max(1, int(L // 5.5))
        sw = L / shops
        for s in range(shops):
            ua = u0 + s * sw + 0.4; ub = ua + sw - 0.8
            r = rnd.random()
            if r < 0.88:
                Q(ua, ub, 0.15, gf - 0.9, rnd.choice([PAL["shutter"], PAL["shutter2"]]))
            else:
                Q(ua, ub, 0.15, gf - 0.9, PAL["window"])
            if rnd.random() < 0.2:
                B(ua - 0.1, ub + 0.1, gf - 0.85, gf - 0.65, 0, 1.6, rnd.choice(PAL["awning"]))
            if rnd.random() < 0.1:
                Q(ua + 0.3, ub - 0.3, gf - 0.55, gf - 0.05, rnd.choice(PAL["sign"]))

def roof(mb, rnd, x0, x1, y0, y1, h, style):
    if style == "wall" or mb.far((x0 + x1) / 2, (y0 + y1) / 2, 200):
        return
    mb.box(x0, x1, y0, y0 + 0.25, h, h + 0.9, PAL["frame"]); mb.box(x0, x1, y1 - 0.25, y1, h, h + 0.9, PAL["frame"])
    for _ in range(rnd.randint(0, 3)):
        cx = rnd.uniform(x0 + 1.5, x1 - 1.5); cy = rnd.uniform(y0 + 1.5, y1 - 1.5)
        k = rnd.random()
        if k < 0.45:
            mb.cyl(cx, cy, h, h + 1.4, 0.6, rnd.choice([PAL["tank"], PAL["tank2"]]), n=8)
        elif k < 0.7:
            mb.box(cx - 1.5, cx + 1.5, cy - 1.2, cy + 1.2, h, h + 2.6, rnd.choice(PAL["wall_old"]))
        else:
            mb.cyl(cx, cy, h, h + 0.9, 0.05, PAL["pole"], n=4); mb.cyl(cx, cy, h + 0.9, h + 0.95, 0.45, PAL["dish"], n=10)

def building(mb, rnd, x0, x1, y0, y1, h, faces, style, haze_at=None):
    col = rnd.choice(PAL["wall_old"] if style == "wall" and rnd.random() < 0.5 else PAL["wall"])
    mb.box(x0, x1, y0, y1, 0, h, col)
    for side in faces:
        facade(mb, rnd, side, x0, x1, y0, y1, h, style, ground_shop=(style != "wall"))
    roof(mb, rnd, x0, x1, y0, y1, h, style)

def block(mb, rnd, x0, x1, y0, y1, hr, style="downtown", depth=16, faces="SNWE", lot=(10, 20)):
    """Fill a rectangular block with buildings around its perimeter, facades on the given street sides."""
    d = min(depth, (y1 - y0) / 2, (x1 - x0) / 2)
    # south and north rows (full width, corners included)
    for side, ya, yb in (("S", y0, y0 + d), ("N", y1 - d, y1)):
        if side not in faces and not (("W" in faces) or ("E" in faces)):
            pass
        x = x0
        while x < x1 - 0.1:
            w = min(rnd.uniform(*lot), x1 - x)
            if x1 - (x + w) < lot[0] * 0.6: w = x1 - x
            f = [side] if side in faces else []
            if x == x0 and "W" in faces: f.append("W")
            if x + w >= x1 - 0.01 and "E" in faces: f.append("E")
            building(mb, rnd, x, x + w, ya, yb, rnd.uniform(*hr), f, style)
            x += w
    # west and east rows between
    for side, xa, xb in (("W", x0, x0 + d), ("E", x1 - d, x1)):
        y = y0 + d
        while y < y1 - d - 0.1:
            w = min(rnd.uniform(*lot), y1 - d - y)
            if (y1 - d) - (y + w) < lot[0] * 0.6: w = y1 - d - y
            f = [side] if side in faces else []
            building(mb, rnd, xa, xb, y, y + w, rnd.uniform(*hr), f, style)
            y += w
    if (x1 - x0) > 2 * d + 1 and (y1 - y0) > 2 * d + 1:
        mb.box(x0 + d, x1 - d, y0 + d, y1 - d, 0, hr[0] * 0.8, PAL["wall_old"][0])

def ground(mb, x0, x1, y0, y1, col, z=0.0, tile=40):
    x = x0
    while x < x1:
        y = y0
        while y < y1:
            xb, yb = min(x + tile, x1), min(y + tile, y1)
            mb.box(x, xb, y, yb, z - 0.05, z, col); y = yb
        x = xb

def sidewalk(mb, x0, x1, y0, y1, tile=40):
    SIDEWALKS.append((min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)))
    ground(mb, x0, x1, y0, y1, PAL["sidewalk"], z=0.15, tile=tile)

def street_light(mb, x, y, toward, h=9.0, arm=2.6):
    mb.cyl(x, y, 0, h, 0.12, PAL["pole"], n=8, r2=0.08)
    d = np.array(toward[:2], float) - np.array((x, y)); d /= np.linalg.norm(d)
    p0 = np.array((x, y, h)); p1 = p0 + np.array((d[0] * arm * 0.55, d[1] * arm * 0.55, 0.35)); p2 = p0 + np.array((d[0] * arm, d[1] * arm, 0.2))
    for a, b in ((p0, p1), (p1, p2)):
        seg(mb, a, b, 0.06, PAL["pole"])
    mb.box(p2[0] - 0.35, p2[0] + 0.35, p2[1] - 0.18, p2[1] + 0.18, p2[2] - 0.2, p2[2], PAL["pole"])
    return tuple(p2)

def seg(mb, a, b, r, col):
    a = np.array(a, float); b = np.array(b, float); v = b - a; L = np.linalg.norm(v)
    z = v / L; x = np.cross(z, (0, 0, 1) if abs(z[2]) < 0.9 else (1, 0, 0)); x /= np.linalg.norm(x); y = np.cross(z, x)
    R = np.stack([x, y, z], axis=1)
    mb.obox(tuple((a + b) / 2), (2 * r, 2 * r, L), R, col)

def palm(mb, rnd, x, y, h=None):
    h = h or rnd.uniform(7, 11)
    mb.cyl(x, y, 0, h, 0.22, PAL["palm"], n=7, r2=0.16)
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.2, 0.2)
        d = np.array((math.cos(a), math.sin(a), 0))
        p0 = np.array((x, y, h)); p1 = p0 + d * 1.6 + np.array((0, 0, 0.5)); p2 = p0 + d * 3.0 + np.array((0, 0, -0.6))
        seg(mb, p0, p1, 0.09, PAL["frond"]); seg(mb, p1, p2, 0.07, PAL["frond"])

def cable(mb, a, b, sag=1.2, n=6):
    a = np.array(a, float); b = np.array(b, float)
    pts = [a + (b - a) * t + np.array((0, 0, -sag * 4 * t * (1 - t))) for t in np.linspace(0, 1, n + 1)]
    for p, q in zip(pts, pts[1:]):
        seg(mb, p, q, 0.025, PAL["cable"])

def debris(mb, rnd, x0, x1, y0, y1, n):
    for _ in range(n):
        x = rnd.uniform(x0, x1); y = rnd.uniform(y0, y1); s = rnd.uniform(0.2, 0.9)
        k = rnd.random()
        if k < 0.6:
            mb.obox((x, y, s * 0.2), (s, s * rnd.uniform(0.5, 1.2), s * 0.4), rotz(rnd.uniform(0, 3)), rnd.choice([PAL["debris"], PAL["rubble"], PAL["concrete"]]))
        elif k < 0.8:
            mb.cyl(x, y, 0, 0.25, 0.35, PAL["tire"], n=8)
        else:
            mb.obox((x, y, 0.4), (2.0, 0.6, 0.8), rotz(rnd.uniform(0, 3)), PAL["concrete"])

def tower(mb, rnd, x, y, w, d, h):
    mb.box(x - w / 2, x + w / 2, y - d / 2, y + d / 2, 0, h, PAL["tower"])
    for side in "SNWE":
        for fl in range(2, int(h // 3.4)):
            z = fl * 3.4
            if side in "SN":
                yy = y - d / 2 - 0.03 if side == "S" else y + d / 2
                (mb.d or mb).box(x - w / 2 + 0.5, x + w / 2 - 0.5, yy, yy + 0.03, z + 0.8, z + 2.2, PAL["window"])
            else:
                xx = x - w / 2 - 0.03 if side == "W" else x + w / 2
                (mb.d or mb).box(xx, xx + 0.03, y - d / 2 + 0.5, y + d / 2 - 0.5, z + 0.8, z + 2.2, PAL["window"])
