"""Bigger building parts for the lairs, on top of the main mod's kit: stair roofs, framed halls, furniture, props.
Coordinates as in kit.py: x east, y up, z south. Facing names follow Minecraft (a stair's facing is the side that is high)."""
import math
import random

from kit import B, AIR, FENCE, LANTERN, HANG, BARREL, CHAIN, PANE, log, leaves, pane, ladder, bed  # noqa: F401

SIDES = ("north", "south", "east", "west")
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def stair(m, facing, half="bottom"):
    return f"minecraft:{m}_stairs[facing={facing},half={half},shape=straight,waterlogged=false]"


def slab(m, t="bottom"):
    return f"minecraft:{m}_slab[type={t},waterlogged=false]"


def trap(m, facing, half="top", open_=False):
    return f"minecraft:{m}_trapdoor[facing={facing},half={half},open={'true' if open_ else 'false'},powered=false,waterlogged=false]"


def wall_post(m):
    return f"minecraft:{m}_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]"


def fence(m):
    return FENCE.format(m)


def candle(n=3, color=None):
    return f"minecraft:{color + '_' if color else ''}candle[candles={n},lit=true,waterlogged=false]"


def carpet(color):
    return f"minecraft:{color}_carpet"


CHAIN_X = "minecraft:iron_chain[axis=x,waterlogged=false]"
CHAIN_Z = "minecraft:iron_chain[axis=z,waterlogged=false]"
SOUL_HANG = "minecraft:soul_lantern[hanging=true,waterlogged=false]"
SOUL_LANTERN = "minecraft:soul_lantern[hanging=false,waterlogged=false]"
CAMPFIRE = "minecraft:campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]"
SMOKE = "minecraft:campfire[facing=north,lit=true,signal_fire=true,waterlogged=false]"
SOUL_FIRE = "minecraft:soul_campfire[facing=north,lit=true,signal_fire=false,waterlogged=false]"
WATER = "minecraft:water[level=0]"


class Parts(B):
    # ---------------------------------------------------------------- roofs
    def gable_roof(self, x0, z0, x1, z1, y, fam, fill, ov=1, axis="x", eave=None):
        """A stair roof with its ridge along `axis`, overhanging by `ov`; the gable ends are filled with `fill`.
        Returns the ridge height."""
        if axis == "x":
            lo, hi = z0 - ov, z1 + ov
            a0, a1 = x0 - ov, x1 + ov
            put = lambda a, c, yy, s: self.set(a, yy, c, s)
            up_lo, up_hi = "south", "north"
            end0, end1 = x0, x1
        else:
            lo, hi = x0 - ov, x1 + ov
            a0, a1 = z0 - ov, z1 + ov
            put = lambda a, c, yy, s: self.set(c, yy, a, s)
            up_lo, up_hi = "east", "west"
            end0, end1 = z0, z1
        i = 0
        while lo + i <= hi - i:
            yy = y + i
            cl, ch = lo + i, hi - i
            for a in range(a0, a1 + 1):
                if cl == ch:
                    put(a, cl, yy, slab(fam))
                else:
                    put(a, cl, yy, stair(fam, up_lo)); put(a, ch, yy, stair(fam, up_hi))
            for c in range(cl + 1, ch):
                put(end0, c, yy, fill); put(end1, c, yy, fill)
            if i == 0 and eave:   # upside-down stairs under the eaves give the roof a thick edge
                for a in range(a0, a1 + 1):
                    put(a, cl, yy - 1, stair(fam, OPP[up_lo], "top")); put(a, ch, yy - 1, stair(fam, OPP[up_hi], "top"))
            i += 1
        return y + i - 1

    def hip_roof(self, x0, z0, x1, z1, y, fam, fill, ov=1, cap=None):
        """A pyramid of stairs over a rectangle; the ridge (if long) is filled with full blocks and slabs on top."""
        x0, z0, x1, z1 = x0 - ov, z0 - ov, x1 + ov, z1 + ov
        i = 0
        while x0 + i <= x1 - i and z0 + i <= z1 - i:
            a0, a1, c0, c1, yy = x0 + i, x1 - i, z0 + i, z1 - i, y + i
            if a0 == a1 or c0 == c1:
                self.box(a0, yy, c0, a1, yy, c1, slab(fam))
                break
            for x in range(a0, a1 + 1):
                self.set(x, yy, c0, stair(fam, "south")); self.set(x, yy, c1, stair(fam, "north"))
            for z in range(c0 + 1, c1):
                self.set(a0, yy, z, stair(fam, "east")); self.set(a1, yy, z, stair(fam, "west"))
            if a1 - a0 > 1 and c1 - c0 > 1:
                self.box(a0 + 1, yy, c0 + 1, a1 - 1, yy, c1 - 1, fill) if i > 0 else None
            i += 1
        if cap:
            cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
            self.set(cx, y + i, cz, cap)
        return y + i

    def eave_tips(self, x0, z0, x1, z1, y, fam):
        """Upturned corners (East Asian roofs): a stair one higher at each corner."""
        for (x, z, f) in ((x0, z0, "south"), (x1, z0, "south"), (x0, z1, "north"), (x1, z1, "north")):
            self.set(x, y + 1, z, stair(fam, f))

    def pagoda_roof(self, x0, z0, x1, z1, y, fam, fill, ov=2):
        """A wide, low roof with upturned corners."""
        top = self.hip_roof(x0, z0, x1, z1, y, fam, fill, ov=ov)
        self.eave_tips(x0 - ov, z0 - ov, x1 + ov, z1 + ov, y, fam)
        return top

    # ---------------------------------------------------------------- buildings
    def hall(self, x0, z0, x1, z1, y, h, wall, base, post, trim=None, floor=None, win=PANE, every=4,
             doors=(), proud=True, win_h=2, ceiling=None):
        """A framed building shell: base course, walls, posts (1 proud of the wall every `every` blocks), a trim band
        under the eaves, framed windows between posts, and door openings. doors = [(side, offset, width, height)].
        Returns the interior floor y (y+1 is where you stand)."""
        self.room(x0, y, z0, x1, y + h, z1, wall, floor=floor or base, ceiling=ceiling)
        self.box(x0 + 1, y + h, z0 + 1, x1 - 1, y + h, z1 - 1, ceiling or wall)
        self.walls(x0, y, z0, x1, y, z1, base)   # darker base course
        self.walls(x0, y + 1, z0, x1, y + 1, z1, base)
        if trim:
            self.walls(x0, y + h, z0, x1, y + h, z1, trim)
        posts = []
        for x in list(range(x0, x1, every)) + [x1]:
            posts += [(x, z0, "north"), (x, z1, "south")]
        for z in list(range(z0, z1, every)) + [z1]:
            posts += [(x0, z, "west"), (x1, z, "east")]
        for (x, z, side) in posts:
            self.box(x, y, z, x, y + h, z, post)
            if proud and (x, z) not in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
                dx = {"east": 1, "west": -1}.get(side, 0); dz = {"south": 1, "north": -1}.get(side, 0)
                self.box(x + dx, y, z + dz, x + dx, y + h - 1, z + dz, post)
        # windows: centred between posts, with a sill (an upside-down stair) outside
        if win:
            for x in range(x0 + 2, x1 - 1):
                if (x - x0) % every == every // 2:
                    for (z, side) in ((z0, "north"), (z1, "south")):
                        self.box(x, y + 2, z, x, y + 1 + win_h, z, win)
            for z in range(z0 + 2, z1 - 1):
                if (z - z0) % every == every // 2:
                    for (x, side) in ((x0, "west"), (x1, "east")):
                        self.box(x, y + 2, z, x, y + 1 + win_h, z, win)
        for (side, off, w, dh) in doors:
            self.opening(x0, z0, x1, z1, y + 1, side, off, w, dh)
        return y

    def opening(self, x0, z0, x1, z1, y, side, off, w, h, lamp=True):
        if side in ("north", "south"):
            z = z0 if side == "north" else z1
            self.box(x0 + off, y, z, x0 + off + w - 1, y + h - 1, z, AIR)
            if lamp:
                dz = -1 if side == "north" else 1
                self.set(x0 + off - 1, y + h, z + dz, "minecraft:lantern[hanging=true,waterlogged=false]") if self.get(x0 + off - 1, y + h + 1, z + dz) else None
        else:
            x = x0 if side == "west" else x1
            self.box(x, y, z0 + off, x, y + h - 1, z0 + off + w - 1, AIR)

    def stair_run(self, x, y, z, n, fam, facing, fill, width=1):
        """A flight of n steps going up toward `facing`, starting at (x, y, z)."""
        dx = {"east": 1, "west": -1}.get(facing, 0); dz = {"south": 1, "north": -1}.get(facing, 0)
        for i in range(n):
            for w in range(width):
                xx = x + dx * i + (w if dz else 0); zz = z + dz * i + (w if dx else 0)
                self.set(xx, y + i, zz, stair(fam, facing))
                for yy in range(y + i - 1, y - 1, -1):
                    if self.get(xx, yy, zz) in (None, AIR):
                        self.set(xx, yy, zz, fill)

    # ---------------------------------------------------------------- furniture
    def table(self, x, y, z, leg="spruce", top="minecraft:brown_carpet", w=1, axis="x"):
        """A table: fence legs with a carpet (or pressure plate) on top."""
        for i in range(w):
            xx, zz = (x + i, z) if axis == "x" else (x, z + i)
            self.set(xx, y, zz, fence(leg)); self.set(xx, y + 1, zz, top)

    def chair(self, x, y, z, wood, facing):
        self.set(x, y, z, stair(wood, facing))

    def shelf(self, x, y, z, h=2, axis="x", n=1):
        for i in range(n):
            xx, zz = (x + i, z) if axis == "x" else (x, z + i)
            self.box(xx, y, zz, xx, y + h - 1, zz, "minecraft:bookshelf")

    def crates(self, x, y, z, rnd, n=4, spread=2):
        for _ in range(n):
            xx = x + rnd.randint(0, spread); zz = z + rnd.randint(0, spread)
            yy = y
            while self.get(xx, yy, zz) not in (None, AIR) and yy < y + 2:
                yy += 1
            self.set(xx, yy, zz, rnd.choice([BARREL, "minecraft:barrel[facing=north,open=false]", "minecraft:spruce_planks", "minecraft:composter[level=0]"]))

    def lamp_post(self, x, y, z, wood="dark_oak", h=3, lamp=LANTERN, arm=None):
        self.box(x, y, z, x, y + h - 1, z, fence(wood))
        if arm:
            dx = {"east": 1, "west": -1}.get(arm, 0); dz = {"south": 1, "north": -1}.get(arm, 0)
            self.set(x, y + h, z, fence(wood)); self.set(x + dx, y + h, z + dz, fence(wood))
            self.set(x + dx, y + h - 1, z + dz, lamp.replace("hanging=false", "hanging=true"))
        else:
            self.set(x, y + h, z, lamp)

    def stone_lantern(self, x, y, z, stone="stone_brick", lamp=None):
        self.set(x, y, z, wall_post(stone)); self.set(x, y + 1, z, lamp or SOUL_LANTERN)
        self.set(x, y + 2, z, slab(stone))

    def hanging(self, x, y_top, z, length, lamp=HANG):
        for yy in range(y_top, y_top - length, -1):
            self.set(x, yy, z, CHAIN)
        self.set(x, y_top - length, z, lamp)

    def hang_from(self, x, y, z, lamp=HANG, up=12):
        """A lantern at (x, y, z) on a chain running up to the first block above it."""
        self.set(x, y, z, lamp)
        for yy in range(y + 1, y + up):
            if self.get(x, yy, z) not in (None, AIR):
                return
            self.set(x, yy, z, CHAIN)

    def mast_yard(self, x0, dy, z0, W, masts):
        """kit.ship() hangs its sails beside the mast without touching it: add the yard they hang from."""
        cz = z0 + W // 2
        for (mx, mh) in masts:
            for y in range(dy + 4, dy + mh - 2):
                self.set(x0 + mx + 1, y, cz, log("spruce"))

    def tower_cap(self, cx, cz, r, h, roof, y=0):
        """kit.tower()'s cone ends in a tip that only touches the ring below at the corners: fill under it."""
        self.set(cx, y + h + r, cz, roof)

    def floating_parts(self, ground=0):
        """Groups of blocks (touching, corners included) that touch nothing at or below `ground`: they would hang in the air."""
        solid = {p for p, s in self.blocks.items() if s and s != AIR and not s.startswith("minecraft:water[")}
        seen, bad = set(), []
        for p in solid:
            if p in seen:
                continue
            stack, comp, grounded = [p], [], False
            seen.add(p)
            while stack:
                q = stack.pop(); comp.append(q)
                if q[1] <= ground:
                    grounded = True
                x, y, z = q
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for dz in (-1, 0, 1):
                            n = (x + dx, y + dy, z + dz)
                            if n in solid and n not in seen:
                                seen.add(n); stack.append(n)
            if not grounded:
                bad.append(comp)
        return bad

