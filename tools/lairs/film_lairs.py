"""The film villains' lairs: Gild Tesoro, Uta, Zephyr, Douglas Bullet and Shiki. gen_lairs.py calls add() to register
them (they use their own structure set, film_lairs, so the six rogue lairs stay as common as they were).
Same rules as the rogue lairs: a compound about 80 blocks across, an approach, an arena at the heart, the boss's own
quarters with the chest, crew quarters, props everywhere, several levels and a landmark you can see from far off."""
import math
import random

from kit import AIR, FENCE, LANTERN, HANG, BARREL, CHAIN, PANE, CAMPFIRE, log, leaves, pane, ladder, bed  # noqa: F401
from parts import (stair, slab, trap, wall_post, fence, candle, carpet, CHAIN_X, CHAIN_Z, SOUL_HANG, SOUL_LANTERN,  # noqa: F401
                   SMOKE, SOUL_FIRE, WATER)

GOLD_BRICK = "onepiece:shandora_gold_bricks"      # gold to look at, not a free stack of gold blocks
GOLD_FAM = "onepiece:shandora_gold_brick"
MARINE_BRICK = "onepiece:marine_bricks"
MARINE_FAM = "onepiece:marine_brick"
MARINE_TILE = "onepiece:marine_tiles"
LAMP_POST_GOLD = "minecraft:ochre_froglight"


def facing(name, f):
    return f"onepiece:{name}[facing={f}]"


def note_block():
    return "minecraft:note_block[instrument=harp,note=0,powered=false]"


def lit_lamp():
    return "minecraft:pearlescent_froglight[axis=y]"


def add(lair, OCEANS, DEEP):
    """Registers the five film lairs with gen_lairs's @lair decorator."""

    # ============================================================ Gild Tesoro: the Gran Tesoro
    @lair("gran_tesoro", "The Gran Tesoro", "gild_tesoro", OCEANS + DEEP + ["onepiece:new_world_sea"], "sea", group="film_lairs")
    def _(b):
        rnd = random.Random(11)
        L, W = 104, 52               # x 0..103 (bow at +x), z 0..51
        CZ = W // 2
        KEEL, DECK = -9, 0
        HULL_HI = ["minecraft:yellow_concrete"] * 4 + ["minecraft:honeycomb_block"]
        HULL_LO = ["minecraft:orange_terracotta", "minecraft:yellow_terracotta"]

        def half(x, y):
            f = x / (L - 1)
            t = (y - KEEL) / (DECK - KEEL)
            taper = 1.0 - max(0.0, (f - 0.72) / 0.28) ** 1.6 * 0.92 - max(0.0, (0.08 - f) / 0.08) * 0.25
            return max(0, round((W / 2 - 1) * (0.5 + 0.5 * t) * taper))

        # --- The hull: a shell (the sea and the vault are inside), gold above the waterline, a band of portholes.
        for x in range(L):
            for y in range(KEEL, DECK + 1):
                h = half(x, y)
                for z in range(CZ - h, CZ + h + 1):
                    k = abs(z - CZ)
                    edge = (y == KEEL or k >= h or x in (0, L - 1) or k > half(x, y - 1)
                            or k > half(min(x + 1, L - 1), y) or k > half(max(x - 1, 0), y))
                    if y == DECK:
                        b.set(x, y, z, "minecraft:smooth_quartz" if k < h else "minecraft:honeycomb_block")
                    elif edge:
                        b.set(x, y, z, rnd.choice(HULL_HI) if y >= -3 else rnd.choice(HULL_LO))
                    else:
                        b.set(x, y, z, AIR)   # keep the sea out of the hull
            h = half(x, DECK)
            for z in (CZ - h, CZ + h):   # gold rail all round, glass between
                b.set(x, 1, z, GOLD_BRICK if x % 4 == 0 else pane("yellow"))
            if x % 6 == 3 and 4 < x < L - 10:
                for z in (CZ - half(x, -2), CZ + half(x, -2)):
                    b.set(x, -2, z, "minecraft:yellow_stained_glass")
        b.waterline = -4   # y = -4 sits at the sea's top: the deck stands 4 above it
        # deck inlays: two gold lines running the length
        for x in range(4, L - 14):
            for z in (CZ - 9, CZ + 9):
                if b.get(x, 0, z) == "minecraft:smooth_quartz":
                    b.set(x, 0, z, "minecraft:yellow_concrete")

        # --- The casino (stern): a gold-framed hall under a glass dome, with a gallery.
        CX0, CZ0, CX1, CZ1 = 5, 9, 37, 43
        b.hall(CX0, CZ0, CX1, CZ1, 0, 13, "minecraft:quartz_bricks", GOLD_BRICK, "minecraft:quartz_pillar[axis=y]", trim=GOLD_BRICK,
               floor="minecraft:red_concrete", win=pane("yellow"), every=4, win_h=5, doors=[("east", 15, 5, 6)])
        for x in range(CX0 + 1, CX1):          # a black and red casino carpet
            for z in range(CZ0 + 1, CZ1):
                if (x + z) % 2 == 0:
                    b.set(x, 0, z, "minecraft:black_concrete")
        dcx, dcz = (CX0 + CX1) // 2, (CZ0 + CZ1) // 2
        b.box(CX0 + 1, 13, CZ0 + 1, CX1 - 1, 13, CZ1 - 1, "minecraft:quartz_bricks")
        b.sphere(dcx, 13, dcz, 13, "minecraft:yellow_stained_glass", hollow=True, upper=True, ry=11)
        b.cyl(dcx, dcz, 12, 13, 13, AIR)
        for i in range(0, 360, 30):            # gold ribs over the dome
            a = math.radians(i)
            for k in range(0, 90, 3):
                t = math.radians(k)
                x = round(dcx + 13 * math.cos(t) * math.cos(a)); z = round(dcz + 13 * math.cos(t) * math.sin(a)); y = 13 + round(11 * math.sin(t))
                b.set(x, y, z, GOLD_BRICK)
        b.set(dcx, 25, dcz, GOLD_BRICK); b.set(dcx, 26, dcz, "minecraft:gold_block"); b.set(dcx, 27, dcz, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
        for y in range(14, 24):
            b.set(dcx, y, dcz, CHAIN)
        b.set(dcx, 13, dcz, facing("chandelier", "north"))
        # the gallery: a balcony all round at y = 7 with a gold rail
        for x in range(CX0 + 1, CX1):
            for z in range(CZ0 + 1, CZ1):
                if x < CX0 + 4 or x > CX1 - 4 or z < CZ0 + 4 or z > CZ1 - 4:
                    b.set(x, 7, z, slab("smooth_quartz", "top"))
                elif x in (CX0 + 4, CX1 - 4) or z in (CZ0 + 4, CZ1 - 4):
                    b.set(x, 8, z, "minecraft:gold_block" if (x + z) % 9 == 0 else pane("yellow"))
        b.stair_run(CX0 + 1, 1, CZ0 + 5, 7, "quartz", "north", "minecraft:quartz_block") if False else None
        for i in range(7):   # the grand stair up to the gallery, along the west wall
            for w in range(3):
                b.set(CX0 + 1 + w, 1 + i, CZ1 - 4 - i, stair("smooth_quartz", "north"))
                for yy in range(1, 1 + i):
                    b.set(CX0 + 1 + w, yy, CZ1 - 4 - i, "minecraft:smooth_quartz")
        # roulette tables, card tables, slot machines, the bar
        for (tx, tz) in ((13, 18), (13, 32), (25, 18), (25, 32)):
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    b.set(tx + dx, 1, tz + dz, "minecraft:dark_oak_fence[east=false,north=false,south=false,west=false,waterlogged=false]")
                    b.set(tx + dx, 2, tz + dz, carpet("green"))
            b.set(tx, 2, tz, slab(GOLD_FAM)); b.set(tx, 1, tz, GOLD_BRICK)
            for (sx, sz, f) in ((tx - 2, tz, "east"), (tx + 2, tz, "west"), (tx, tz - 2, "south"), (tx, tz + 2, "north")):
                b.set(sx, 1, sz, facing("bar_stool", f))
        for x in range(CX0 + 6, CX1 - 3, 2):     # slot machines along the north and south walls
            for (z, f) in ((CZ0 + 1, "south"), (CZ1 - 1, "north")):
                if b.get(x, 1, z) in (None, AIR, "minecraft:red_concrete", "minecraft:black_concrete"):
                    b.set(x, 1, z, "minecraft:polished_blackstone"); b.set(x, 2, z, "minecraft:ochre_froglight[axis=y]")
                    b.set(x, 3, z, "minecraft:yellow_concrete"); b.set(x, 4, z, candle(1, "yellow"))
                    dz = 1 if f == "south" else -1
                    b.set(x, 2, z + dz, f"minecraft:lever[face=wall,facing={f},powered=false]")
        for z in range(CZ0 + 12, CZ1 - 11):      # the bar
            b.set(CX0 + 2, 1, z, "minecraft:polished_blackstone_bricks"); b.set(CX0 + 2, 2, z, slab(GOLD_FAM))
            b.set(CX0 + 4, 1, z, facing("bar_stool", "west")) if z % 2 else None
            b.set(CX0 + 1, 2, z, facing("wine_rack", "east")) if z % 3 == 0 else None
        for (lx, lz) in ((12, 15), (12, 37), (30, 15), (30, 37)):
            b.hang_from(lx, 10, lz, facing("chandelier", "north"), up=4)
        # the stage at the east end of the hall, with Tesoro's golden piano
        b.box(CX1 - 6, 1, CZ0 + 8, CX1 - 1, 1, CZ1 - 8, GOLD_BRICK)
        b.box(CX1 - 6, 2, CZ0 + 8, CX1 - 1, 2, CZ1 - 8, carpet("yellow"))
        b.set(CX1 - 3, 2, dcz - 3, facing("piano", "west"))
        b.box(CX1 - 6, 1, dcz - 2, CX1 - 1, 2, dcz + 2, AIR)   # the walkway out of the east door stays open

        # --- The gold vault, in the hull under the casino: Tesoro's own room, where the chest is.
        VX0, VZ0, VX1, VZ1 = 12, 17, 30, 35
        b.room(VX0, -7, VZ0, VX1, -1, VZ1, "minecraft:iron_block", floor=GOLD_BRICK, ceiling="minecraft:smooth_quartz")
        b.box(VX0 + 1, -6, VZ0 + 1, VX1 - 1, -2, VZ1 - 1, AIR)
        for x in range(VX0 + 2, VX1 - 1, 3):
            for z in (VZ0 + 1, VZ1 - 1):
                b.box(x, -6, z, x, -4, z, GOLD_BRICK)             # stacked "bullion"
                b.set(x, -3, z, "minecraft:gold_block") if x % 9 == 2 else None
        b.chest((VX0 + VX1) // 2, -6, VZ0 + 2, "gran_tesoro", "south")
        b.set((VX0 + VX1) // 2, -6, VZ0 + 4, facing("throne", "north"))
        b.set((VX0 + VX1) // 2 - 2, -6, VZ0 + 2, facing("chart_table", "south")); b.set((VX0 + VX1) // 2 + 2, -6, VZ0 + 2, BARREL)
        for x in (VX0 + 4, VX1 - 4):
            b.hang_from(x, -3, (VZ0 + VZ1) // 2, HANG)
        for (vx, vz) in ((VX0 + 3, VZ1 - 3), (VX1 - 3, VZ1 - 3)):
            b.set(vx, -6, vz, "minecraft:gold_block")
        b.box(VX1 - 4, -6, VZ1 - 1, VX1 - 2, -2, VZ1 - 1, "minecraft:iron_bars[east=true,north=false,south=false,west=true,waterlogged=false]")   # vault grille
        for i in range(6):   # stairs down from the casino floor (north-east corner) into the vault
            b.set(CX1 - 9 - i, -i, CZ0 + 3, stair("quartz", "east"))
            b.set(CX1 - 9 - i, -i, CZ0 + 2, stair("quartz", "east"))
            b.box(CX1 - 9 - i, 1 - i, CZ0 + 2, CX1 - 9 - i, 3 - i, CZ0 + 3, AIR)
        b.box(CX1 - 15, -6, CZ0 + 2, CX1 - 14, -2, CZ0 + 3, AIR)
        b.box(VX1 - 1, -6, VZ0 + 1, VX1 + 1, -3, VZ0 + 1, AIR) if False else None
        b.box(CX1 - 15, -7, CZ0 + 2, CX1 - 14, -7, CZ0 + 3, "minecraft:iron_block")
        b.box(VX0 + 1, -6, VZ0 - 6, VX0 + 3, -2, VZ0, AIR)   # corridor from the stair foot into the vault
        b.box(VX0, -7, VZ0 - 7, VX0 + 4, -1, VZ0 - 7, "minecraft:iron_block")
        b.box(VX0 + 1, -6, VZ0 - 7, VX1 - 8, -2, VZ0 - 5, AIR)
        b.box(VX0, -7, VZ0 - 7, VX1 - 7, -7, VZ0 - 4, "minecraft:iron_block")
        b.set(VX0 + 6, -3, VZ0 - 6, HANG)

        # --- The Gold Stage (the arena, midship): a roulette wheel set in the deck, spotlights at the corners.
        AX, AZ, R = 56, CZ, 13
        for x in range(AX - R - 1, AX + R + 2):
            for z in range(AZ - R - 1, AZ + R + 2):
                d = math.hypot(x - AX, z - AZ)
                if d <= R + 0.5:
                    if d < 2.5:
                        s = "minecraft:gold_block" if d < 1 else GOLD_BRICK
                    elif d < 7:
                        s = "minecraft:green_concrete" if d < 6.3 else GOLD_BRICK
                    elif d < R - 0.5:
                        wedge = int((math.degrees(math.atan2(z - AZ, x - AX)) + 360) // 10)
                        s = "minecraft:red_concrete" if wedge % 2 else "minecraft:black_concrete"
                        if wedge == 0:
                            s = "minecraft:lime_concrete"
                    else:
                        s = GOLD_BRICK
                    b.set(x, 0, z, s)
        for i in range(0, 360, 12):
            a = math.radians(i)
            x, z = round(AX + (R + 1) * math.cos(a)), round(AZ + (R + 1) * math.sin(a))
            if b.get(x, 1, z) is None:
                b.set(x, 1, z, slab(GOLD_FAM) if i % 36 else "minecraft:ochre_froglight[axis=y]")
        for (px, pz) in ((AX - R, AZ - R + 2), (AX + R, AZ - R + 2), (AX - R, AZ + R - 2), (AX + R, AZ + R - 2)):
            b.box(px, 1, pz, px, 9, pz, "minecraft:quartz_pillar[axis=y]")
            b.set(px, 10, pz, GOLD_BRICK); b.set(px, 11, pz, "minecraft:pearlescent_froglight[axis=y]")
            b.set(px, 1, pz, GOLD_BRICK)
        # --- The hotel tower (port side, by the stage) and the casino's twin neon masts.
        HX, HZ = 46, CZ - 18
        b.hall(HX - 4, HZ - 3, HX + 4, HZ + 3, 0, 32, "minecraft:quartz_bricks", GOLD_BRICK, "minecraft:quartz_pillar[axis=y]", trim=GOLD_BRICK,
               floor="minecraft:smooth_quartz", win="minecraft:yellow_stained_glass", every=2, win_h=2, doors=[("south", 4, 1, 3)], proud=False)
        for y in range(6, 32, 5):
            b.box(HX - 3, y, HZ - 2, HX + 3, y, HZ + 2, "minecraft:smooth_quartz")
            b.box(HX - 3, y + 1, HZ - 2, HX - 3, y + 1, HZ - 2, BARREL)
            b.set(HX + 2, y + 1, HZ + 1, "minecraft:yellow_bed[facing=west,occupied=false,part=foot]"); b.set(HX + 1, y + 1, HZ + 1, "minecraft:yellow_bed[facing=west,occupied=false,part=head]")
            b.set(HX, y - 1, HZ, HANG)
            b.set(HX - 3, y, HZ + 2, AIR)
        for y in range(1, 33):
            b.set(HX - 3, y, HZ + 2, ladder("north"))
        b.hip_roof(HX - 4, HZ - 3, HX + 4, HZ + 3, 33, GOLD_FAM, GOLD_BRICK, ov=1, cap="minecraft:gold_block")
        for mz in (CZ - 14, CZ + 14):
            b.box(66, 1, mz, 66, 22, mz, "minecraft:quartz_pillar[axis=y]")
            for y in range(4, 22, 3):
                b.set(65, y, mz, "minecraft:ochre_froglight[axis=y]"); b.set(67, y, mz, "minecraft:ochre_froglight[axis=y]")
            b.set(66, 23, mz, "minecraft:gold_block")
        # string lights from the masts to the dome
        for mz in (CZ - 14, CZ + 14):
            for x in range(38, 66):
                y = 20 - round(4 * math.sin(math.pi * (x - 38) / 28))
                b.set(x, y, mz, CHAIN_X)
                if x % 4 == 0:
                    b.set(x, y - 1, mz, HANG)

        # --- The golden statue of Tesoro (bow): the landmark, 40 high, arm thrown up at the sky.
        SX, SZ = 86, CZ
        b.box(SX - 5, 1, SZ - 5, SX + 5, 4, SZ + 5, "minecraft:quartz_bricks")
        b.box(SX - 6, 1, SZ - 6, SX + 6, 1, SZ + 6, GOLD_BRICK)
        b.box(SX - 5, 4, SZ - 5, SX + 5, 4, SZ + 5, GOLD_BRICK)
        for x in range(SX - 5, SX + 6):
            b.set(x, 2, SZ - 6, stair(GOLD_FAM, "south")); b.set(x, 2, SZ + 6, stair(GOLD_FAM, "north"))
        GOLD = ["minecraft:honeycomb_block"] * 3 + [GOLD_BRICK] * 3 + ["minecraft:yellow_concrete"]
        def lump(x0, y0, z0, x1, y1, z1):
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 1):
                    for z in range(z0, z1 + 1):
                        b.set(x, y, z, rnd.choice(GOLD))
        lump(SX - 1, 5, SZ - 4, SX + 1, 17, SZ - 2)              # legs
        lump(SX - 1, 5, SZ + 2, SX + 1, 17, SZ + 4)
        lump(SX - 2, 5, SZ - 5, SX + 2, 6, SZ - 2); lump(SX - 2, 5, SZ + 2, SX + 2, 6, SZ + 5)   # shoes
        lump(SX - 2, 18, SZ - 4, SX + 2, 22, SZ + 4)              # hips (white suit trousers in gold)
        lump(SX - 2, 23, SZ - 3, SX + 2, 31, SZ + 3)              # waist and chest
        lump(SX - 3, 30, SZ - 6, SX + 3, 33, SZ + 6)              # the fur stole
        lump(SX - 2, 34, SZ - 2, SX + 2, 38, SZ + 2)              # head
        lump(SX - 2, 39, SZ - 3, SX + 2, 42, SZ + 1)              # pompadour
        lump(SX - 4, 41, SZ - 2, SX - 3, 42, SZ + 1)
        b.set(SX - 3, 36, SZ - 1, "minecraft:red_concrete"); b.set(SX - 3, 36, SZ + 1, "minecraft:red_concrete")   # his red shades
        b.set(SX - 3, 36, SZ, "minecraft:black_concrete")
        lump(SX - 1, 26, SZ + 7, SX + 1, 32, SZ + 9)              # right arm down, hand on hip
        lump(SX - 1, 24, SZ + 5, SX + 1, 26, SZ + 7)
        for i in range(10):                                      # left arm thrown up
            lump(SX - 1, 32 + i, SZ - 7 - i // 3, SX + 1, 33 + i, SZ - 6 - i // 3)
        lump(SX - 2, 42, SZ - 11, SX + 2, 45, SZ - 9)             # the fist, with gold rings
        for z in range(SZ - 11, SZ - 8):
            b.set(SX - 3, 43, z, "minecraft:gold_block")
        b.set(SX, 46, SZ - 10, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
        for (fx, fz) in ((SX - 7, SZ - 7), (SX - 7, SZ + 7), (SX + 7, SZ - 7), (SX + 7, SZ + 7)):
            b.set(fx, 1, fz, GOLD_BRICK); b.set(fx, 2, fz, LAMP_POST_GOLD)
        # --- The bow: a golden figurehead and the wheelhouse.
        b.box(L - 6, 1, CZ - 1, L - 2, 3, CZ + 1, "minecraft:honeycomb_block")
        b.set(L - 1, 2, CZ, "minecraft:gold_block")
        b.hall(68, CZ + 14, 80, CZ + 21, 0, 5, "minecraft:quartz_bricks", GOLD_BRICK, "minecraft:quartz_pillar[axis=y]", floor="minecraft:dark_oak_planks",
               win=pane("yellow"), every=3, doors=[("north", 6, 2, 3)], proud=False)
        b.hip_roof(68, CZ + 14, 80, CZ + 21, 6, GOLD_FAM, GOLD_BRICK, ov=1)
        b.set(74, 1, CZ + 19, facing("ships_wheel", "south")); b.set(71, 1, CZ + 19, facing("chart_table", "north"))
        b.set(76, 1, CZ + 16, facing("captains_chair", "north")); b.set(74, 5, CZ + 17, HANG)
        # cargo, lifeboats and lamps on the open deck
        for (x, z) in ((40, 6), (78, 8), (42, 46), (58, 46)):
            b.crates(x, 1, z, rnd, n=4, spread=2)
        for x in range(42, 80, 9):
            for z in (CZ - 22, CZ + 22):
                if abs(z - CZ) < half(x, DECK) - 1 and b.get(x, 1, z) is None:
                    b.lamp_post(x, 1, z, "dark_oak", 3, LAMP_POST_GOLD)

        b.rogue(AX, 1, AZ, "gild_tesoro")
        b.crew("gran_tesoro_guard", ((AX - 9, AZ - 6), (AX + 9, AZ - 6), (AX - 9, AZ + 6), (AX + 9, AZ + 6), (20, 25), (30, 15), (SX - 8, SZ)))

    # ============================================================ Uta: the Elegia Concert Stage
    @lair("elegia_stage", "Uta's Elegia Stage", "uta_diva",
          ["minecraft:meadow", "minecraft:flower_forest", "minecraft:sunflower_plains", "minecraft:plains", "onepiece:dressrosa"], "land", group="film_lairs")
    def _(b):
        rnd = random.Random(12)
        W, D = 92, 86
        grass = ["minecraft:grass_block"] * 4 + ["minecraft:moss_block"]
        for x in range(0, W + 1):
            for z in range(0, D + 1):
                b.set(x, -1, z, "minecraft:dirt"); b.set(x, 0, z, rnd.choice(grass))
        CX = 46
        # --- The stage (the arena): a raised platform 39 wide under a great shell, with a runway into the crowd.
        SX0, SX1, SZ0, SZ1 = CX - 19, CX + 19, 12, 30
        b.box(SX0, 0, SZ0, SX1, 3, SZ1, "minecraft:white_concrete")
        b.box(SX0, 3, SZ0, SX1, 3, SZ1, "minecraft:smooth_quartz")
        for x in range(SX0, SX1 + 1):
            for z in range(SZ0, SZ1 + 1):
                if (x - CX) ** 2 + (z - 22) ** 2 < 49:
                    b.set(x, 3, z, "minecraft:pink_concrete" if math.hypot(x - CX, z - 22) > 5 else "minecraft:white_concrete")
            b.set(x, 3, SZ1, "minecraft:pearlescent_froglight[axis=y]" if x % 3 == 0 else "minecraft:smooth_quartz")
            b.set(x, 4, SZ1, carpet("pink")) if x % 3 else None
        for x in range(CX - 2, CX + 3):           # the runway
            for z in range(SZ1 + 1, SZ1 + 13):
                b.box(x, 0, z, x, 2, z, "minecraft:white_concrete"); b.set(x, 3, z, "minecraft:pink_concrete" if abs(x - CX) < 2 else "minecraft:smooth_quartz")
        b.disk(CX, 3, SZ1 + 14, 4, "minecraft:smooth_quartz"); b.cyl(CX, SZ1 + 14, 4, 0, 2, "minecraft:white_concrete")
        b.disk(CX, 3, SZ1 + 14, 2, "minecraft:pink_concrete")
        for side in (-1, 1):                      # stairs up each side of the stage
            for i in range(3):
                x = SX0 - 3 + i if side < 0 else SX1 + 3 - i
                for z in range(SZ1 - 6, SZ1 - 2):
                    b.box(x, 0, z, x, i, z, "minecraft:quartz_block")
                    b.set(x, 1 + i, z, stair("quartz", "east" if side < 0 else "west"))
        # the back wall and the shell roof: an arch curving out over the stage, white with pink glass ribs
        for x in range(SX0 - 2, SX1 + 3):
            b.box(x, 4, SZ0 - 1, x, 22, SZ0 - 1, "minecraft:white_concrete")
            for z in range(SZ0 - 1, SZ1 + 3):
                t = (z - (SZ0 - 1)) / (SZ1 + 3 - (SZ0 - 1))
                y = 4 + round(18 * math.sqrt(max(0.0, 1 - t * t)))
                rib = (x - CX) % 6 == 0
                b.set(x, y, z, "minecraft:pink_stained_glass" if rib and z < SZ1 else "minecraft:white_concrete")
                if z == SZ1 + 2:
                    b.set(x, y - 1, z, "minecraft:end_rod[facing=down]") if x % 2 == 0 else None
        for (ex) in (SX0 - 2, SX1 + 2):           # close the shell's ends
            for z in range(SZ0 - 1, SZ1 + 3):
                t = (z - (SZ0 - 1)) / (SZ1 + 3 - (SZ0 - 1))
                top = 4 + round(18 * math.sqrt(max(0.0, 1 - t * t)))
                for y in range(4, top):
                    if z < SZ1 - 7 or y > top - 3:
                        b.set(ex, y, z, "minecraft:white_concrete")
        # the backdrop: a big pink note on the back wall, and Uta's red-and-white split
        note = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (3, 7), (4, 6), (5, 5), (5, 4)]
        for (nx, ny) in note:
            for sx in (0, 1):
                for sy in (0, 1):
                    b.set(CX - 5 + nx * 2 + sx, 6 + ny * 2 + sy, SZ0, "minecraft:magenta_concrete")
        for y in range(5, 21):
            b.set(SX0 + 2, y, SZ0, "minecraft:red_concrete"); b.set(SX1 - 2, y, SZ0, "minecraft:white_wool")
        # spotlights hanging under the shell
        for x in range(SX0 + 3, SX1 - 2, 5):
            b.hang_from(x, 15, SZ0 + 8, "minecraft:pearlescent_froglight[axis=y]", up=8)
        # instruments on stage: a piano, drums (note blocks), mic stand
        b.set(SX0 + 5, 4, SZ0 + 3, facing("piano", "south")); b.set(SX0 + 6, 4, SZ0 + 3, facing("piano", "south"))
        for (dx, dz) in ((0, 0), (1, 0), (0, 1), (2, 1)):
            b.set(SX1 - 7 + dx, 4, SZ0 + 3 + dz, note_block())
        b.set(CX, 4, SZ1 - 2, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
        # --- The speaker stacks, twice as tall as the stage, either side of it.
        for (kx0) in (SX0 - 10, SX1 + 4):
            b.box(kx0, 1, SZ0 + 2, kx0 + 6, 18, SZ0 + 10, "minecraft:black_concrete")
            for y in range(2, 18, 4):
                for x in range(kx0 + 1, kx0 + 6, 2):
                    b.set(x, y, SZ0 + 10, note_block()); b.set(x, y + 1, SZ0 + 10, "minecraft:jukebox[has_record=false]")
                b.box(kx0, y + 3, SZ0 + 10, kx0 + 6, y + 3, SZ0 + 10, "minecraft:gray_concrete")
            b.box(kx0 - 1, 19, SZ0 + 1, kx0 + 7, 19, SZ0 + 11, "minecraft:smooth_quartz")
            b.set(kx0 + 3, 20, SZ0 + 6, "minecraft:pearlescent_froglight[axis=y]")
        # --- The amphitheatre: tiered rings of seats rising to the south, aisles every 30 degrees.
        AZ = SZ1 + 2
        for x in range(CX - 44, CX + 45):
            for z in range(AZ, D + 1):
                r = math.hypot(x - CX, z - AZ)
                if 18 <= r < 42 and 0 <= x <= W:
                    tier = int((r - 18) // 2)
                    ang = math.degrees(math.atan2(z - AZ, x - CX))
                    aisle = any(abs(ang - a) < 1.6 * 30 / max(r, 1) for a in (30, 60, 90, 120, 150))
                    top = 1 + tier
                    for y in range(0, top):
                        b.set(x, y, z, "minecraft:stone_bricks")
                    if aisle:
                        b.set(x, top - 1, z, "minecraft:polished_andesite")
                    elif int(r) % 2 == 0:
                        b.set(x, top - 1, z, "minecraft:smooth_quartz")   # the step
                    else:
                        b.set(x, top - 1, z, "minecraft:pink_concrete" if tier % 2 else "minecraft:white_concrete")   # the seat
                        b.set(x, top, z, carpet("pink" if tier % 2 else "magenta")) if rnd.random() < 0.3 else None
                elif 42 <= r < 43.5 and 0 <= x <= W:
                    b.box(x, 0, z, x, 13, z, "minecraft:stone_bricks")   # back wall of the bowl
                    b.set(x, 14, z, slab("stone_brick"))
                    if int(math.degrees(math.atan2(z - AZ, x - CX))) % 10 == 0:
                        b.set(x, 14, z, "minecraft:pearlescent_froglight[axis=y]")
        # the pit (flowers and glow sticks: fans have been waiting here for days)
        b.scatter(CX - 16, AZ, CX + 16, AZ + 17, 1, ["minecraft:pink_tulip", "minecraft:white_tulip", "minecraft:allium", "minecraft:short_grass", carpet("pink")], 0.12, rnd, only_on=grass)
        # --- Four light towers on the rim, with strings of lanterns to the shell.
        for (tx, tz) in ((CX - 30, AZ + 30), (CX + 30, AZ + 30), (CX - 40, AZ + 6), (CX + 40, AZ + 6)):
            if not (0 <= tx <= W and 0 <= tz <= D):
                continue
            base = b.get(tx, 0, tz)
            yb = 1
            while b.get(tx, yb, tz) not in (None, AIR):
                yb += 1
            for y in range(yb, yb + 16):
                for (dx, dz) in ((0, 0), (1, 0), (0, 1), (1, 1)):
                    b.set(tx + dx, y, tz + dz, "minecraft:iron_block" if (dx + dz) % 2 == 0 or y % 4 == 0 else "minecraft:iron_bars[east=false,north=false,south=false,west=false,waterlogged=false]")
            b.box(tx - 1, yb + 16, tz - 1, tx + 2, yb + 16, tz + 2, "minecraft:smooth_stone_slab[type=bottom,waterlogged=false]")
            for (dx, dz) in ((0, 0), (1, 0), (0, 1), (1, 1)):
                b.set(tx + dx, yb + 15, tz + dz, "minecraft:pearlescent_froglight[axis=y]")
        # --- Backstage: Uta's dressing room behind the shell, where the chest is.
        BX0, BX1, BZ0, BZ1 = CX - 12, CX + 12, 1, 10
        b.hall(BX0, BZ0, BX1, BZ1, 3, 6, "minecraft:white_concrete", "minecraft:pink_terracotta", "minecraft:quartz_pillar[axis=y]", trim="minecraft:pink_concrete",
               floor="minecraft:pink_wool", win=pane("pink"), every=4, doors=[("south", 12, 2, 3)], proud=False)
        b.support(BX0, BZ0, BX1, BZ1, 3, ["minecraft:white_concrete"], rnd, down_to=0)
        b.box(CX, 4, BZ1 + 1, CX + 1, 6, SZ0 - 1, AIR)   # backstage door through the shell wall
        b.hip_roof(BX0, BZ0, BX1, BZ1, 10, "quartz", "minecraft:quartz_block", ov=1)
        b.chest(CX, 4, BZ0 + 1, "elegia_stage", "south")
        for x in range(BX0 + 2, BX0 + 8):         # the vanity: a long mirror, bulbs round it
            b.set(x, 4, BZ0 + 1, "minecraft:white_concrete"); b.set(x, 5, BZ0 + 1, carpet("white"))
            b.set(x, 6, BZ0 + 1 - 0, pane()) if False else None
        b.box(BX0 + 2, 6, BZ0, BX0 + 7, 8, BZ0, "minecraft:glass")
        for x in (BX0 + 1, BX0 + 8):
            b.box(x, 6, BZ0 + 1, x, 8, BZ0 + 1, "minecraft:ochre_froglight[axis=y]")
        b.set(BX0 + 4, 4, BZ0 + 2, facing("bar_stool", "north"))
        b.set(BX1 - 2, 4, BZ0 + 2, "minecraft:pink_bed[facing=south,occupied=false,part=foot]") if False else None
        bed("pink", BX1 - 2, 4, BZ0 + 1, b, "south")
        bed("red", BX1 - 4, 4, BZ0 + 1, b, "south")
        for x in range(BX0 + 10, BX1 - 5, 2):    # costume racks
            b.set(x, 4, BZ1 - 1, "minecraft:dark_oak_fence[east=false,north=false,south=false,west=false,waterlogged=false]")
            b.set(x, 5, BZ1 - 1, "minecraft:white_banner[rotation=0]" if x % 4 else "minecraft:pink_banner[rotation=0]")
        for (fx, fz) in ((BX0 + 1, BZ1 - 1), (BX1 - 1, BZ1 - 1), (CX - 3, BZ0 + 1), (CX + 3, BZ0 + 1)):
            b.set(fx, 4, fz, "minecraft:potted_allium" if fx % 2 else "minecraft:potted_pink_tulip")
        b.set(CX + 2, 4, BZ0 + 1, facing("crate_stack", "south")); b.set(CX - 2, 4, BZ0 + 1, BARREL)
        b.set(CX, 9, BZ0 + 5, HANG); b.set(BX0 + 5, 9, BZ0 + 5, HANG); b.set(BX1 - 5, 9, BZ0 + 5, HANG)
        # --- Ruined Elegia (the landmark): the broken castle tower and the empty town, north-east and west.
        TX, TZ = W - 10, 12
        b.cyl(TX, TZ, 6, 0, 38, "minecraft:stone_bricks", hollow=True)
        b.disk(TX, 0, TZ, 5, "minecraft:mossy_stone_bricks")
        for y in range(4, 38, 6):
            b.disk(TX, y, TZ, 5, "minecraft:spruce_planks")
            b.set(TX, y, TZ - 4, AIR); b.set(TX, y + 1, TZ - 4, AIR)
        for y in range(1, 38):
            b.set(TX, y, TZ - 5, ladder("south"))
        for y in range(3, 38, 5):
            for (dx, dz) in ((6, 0), (-6, 0), (0, 6)):
                b.set(TX + dx, y, TZ + dz, pane("pink")); b.set(TX + dx, y + 1, TZ + dz, pane("pink"))
        for i in range(0, 360, 20):   # a jagged broken top
            a = math.radians(i)
            h = rnd.randint(0, 6)
            x, z = round(TX + 6 * math.cos(a)), round(TZ + 6 * math.sin(a))
            for y in range(38, 38 + h):
                b.set(x, y, z, rnd.choice(["minecraft:stone_bricks", "minecraft:cracked_stone_bricks", "minecraft:mossy_stone_bricks"]))
            for y in range(38 - rnd.randint(0, 5), 38):
                if i % 60 == 0:
                    b.set(x, y, z, AIR)
        for y in range(2, 30):
            for (dx, dz) in ((7, 0), (0, 7)):
                if rnd.random() < 0.5:
                    b.set(TX + dx, y, TZ + dz, "minecraft:vine[east=false,north=true,south=false,up=false,west=true]") if b.get(TX + dx, y, TZ + dz) is None else None
        b.set(TX, 39, TZ, "minecraft:bell[attachment=floor,facing=north,powered=false]") if False else None
        b.box(TX, 1, TZ + 6, TX, 2, TZ + 6, AIR)   # the tower's door
        for (hx, hz, hw, hd) in ((1, 2, 9, 8), (1, 16, 8, 9), (79, 72, 9, 8)):   # the empty town
            b.hall(hx, hz, hx + hw, hz + hd, 0, 5, "minecraft:stone_bricks", "minecraft:mossy_cobblestone", log("spruce"), floor="minecraft:spruce_planks",
                   win=pane(), every=3, doors=[("east", 3, 1, 2)], proud=False)
            b.gable_roof(hx, hz, hx + hw, hz + hd, 5, "spruce", "minecraft:spruce_planks", axis="x")
            for _ in range(14):   # it fell in
                x = rnd.randint(hx + 1, hx + hw - 1); z = rnd.randint(hz + 1, hz + hd - 1)
                for y in range(5, 11):
                    b.set(x, y, z, AIR) if b.get(x, y, z) not in (None,) and rnd.random() < 0.6 else None
            b.set(hx + 2, 1, hz + 2, "minecraft:cobweb"); b.set(hx + hw - 2, 3, hz + hd - 2, "minecraft:cobweb")
            b.set(hx + 2, 1, hz + hd - 2, facing("piano", "east") if hz == 16 else BARREL)
        # flowers, banners and the road in
        for z in range(SZ1 + 15, D + 1):
            for x in range(CX - 2, CX + 3):
                r = math.hypot(x - CX, z - AZ)
                if r > 43.5 or r < 17:
                    b.set(x, 0, z, "minecraft:gravel" if abs(x - CX) < 2 else "minecraft:polished_andesite")
        b.scatter(0, 0, W, D, 1, ["minecraft:poppy", "minecraft:azure_bluet", "minecraft:oxeye_daisy", "minecraft:pink_tulip", "minecraft:short_grass", "minecraft:short_grass"], 0.07, rnd, only_on=grass)
        for (x, z) in ((14, 4), (25, 4), (66, 4), (13, 28), (W - 3, 60)):
            b.tree(x, 1, z, 6, "birch", 2.6)

        b.rogue(CX, 4, 22, "uta_diva")
        b.crew("entranced_fan", ((CX - 10, 4, 24), (CX + 10, 4, 24), (CX, 1, AZ + 10), (CX - 8, 1, AZ + 6), (CX + 8, 1, AZ + 6), (CX - 2, 4, BZ0 + 5)))

    # ============================================================ Zephyr: the End Point
    @lair("end_point", "The End Point", "zephyr_z",
          ["#minecraft:is_badlands", "minecraft:savanna_plateau", "minecraft:windswept_savanna", "minecraft:stony_shore", "onepiece:punk_hazard_burning", "onepiece:marineford"],
          "land", group="film_lairs")
    def _(b):
        rnd = random.Random(13)
        W, D = 88, 84
        ground = ["minecraft:basalt[axis=y]", "minecraft:blackstone", "minecraft:tuff", "minecraft:gravel", "minecraft:smooth_basalt", "minecraft:coarse_dirt"]
        for x in range(0, W + 1):
            for z in range(0, D + 1):
                b.set(x, -1, z, "minecraft:blackstone"); b.set(x, 0, z, rnd.choice(ground))
        # --- The volcano (the landmark, north-west): 34 high with a glowing crater, and the Dyna Stone vault inside.
        VX, VZ, VR, VH = 22, 22, 21, 34
        for y in range(1, VH + 1):
            r = VR * (1 - (y / (VH + 8)) ** 0.9)
            for x in range(int(VX - r) - 2, int(VX + r) + 3):
                for z in range(int(VZ - r) - 2, int(VZ + r) + 3):
                    d = math.hypot(x - VX, z - VZ) + rnd.random() * 1.4
                    if d <= r:
                        inner = y > VH - 9 and d < r - 3 - (y - (VH - 9)) * 0.3 + 3
                        if y > VH - 9 and d < (y - (VH - 9)) * 0.9 + 1.5:
                            continue   # the crater
                        if d > r - 2.5 or y % 6 == 0 or inner or rnd.random() < 0.15:
                            b.set(x, y, z, rnd.choice(["minecraft:basalt[axis=y]", "minecraft:blackstone", "minecraft:tuff", "minecraft:blackstone", "minecraft:smooth_basalt"]))
                        else:
                            b.set(x, y, z, "minecraft:blackstone")
        b.disk(VX, VH - 9, VZ, 2.5, "minecraft:magma_block")
        b.disk(VX, VH - 10, VZ, 3.5, "minecraft:blackstone")
        b.set(VX, VH - 8, VZ, SMOKE); b.set(VX + 1, VH - 9, VZ + 1, "minecraft:magma_block")
        for i in range(0, 360, 50):   # magma streams down the slopes
            a = math.radians(i + rnd.randint(-10, 10))
            for t in range(4, VR):
                x, z = round(VX + t * math.cos(a)), round(VZ + t * math.sin(a))
                for y in range(VH, 0, -1):
                    if b.get(x, y, z) not in (None, AIR):
                        b.set(x, y, z, "minecraft:magma_block")
                        break
        # the vault: a tunnel in from the east, a domed chamber of Dyna Stones (purple crystal) behind iron bars
        for x in range(VX + 4, VX + VR + 3):
            for z in range(VZ - 2, VZ + 3):
                for y in range(1, 6):
                    b.set(x, y, z, AIR if abs(z - VZ) < 2 and y < 5 else "minecraft:polished_blackstone_bricks")
            if x % 4 == 0:
                b.set(x, 4, VZ, HANG)
        for x in range(VX + 4, VX + VR + 3):
            for z in range(VZ - 1, VZ + 2):
                b.set(x, 0, z, "minecraft:polished_blackstone_bricks" if x % 3 else "minecraft:rail[shape=east_west,waterlogged=false]") if z == VZ else b.set(x, 0, z, "minecraft:polished_blackstone_bricks")
        b.sphere(VX, 1, VZ, 7, "minecraft:polished_blackstone_bricks", hollow=True, upper=True, ry=7)
        b.disk(VX, 0, VZ, 6.5, "minecraft:polished_deepslate")
        for i in range(0, 360, 45):
            a = math.radians(i)
            x, z = round(VX + 4 * math.cos(a)), round(VZ + 4 * math.sin(a))
            b.set(x, 1, z, "minecraft:crying_obsidian"); b.set(x, 2, z, "minecraft:amethyst_block"); b.set(x, 3, z, "minecraft:amethyst_cluster[facing=up,waterlogged=false]")
            b.set(x, 2, z, "minecraft:purple_stained_glass") if i % 90 else None
        b.box(VX - 1, 1, VZ - 1, VX + 1, 1, VZ + 1, "minecraft:crying_obsidian")
        b.set(VX, 2, VZ, "minecraft:budding_amethyst") if False else b.set(VX, 2, VZ, "minecraft:amethyst_block")
        b.set(VX, 3, VZ, "minecraft:large_amethyst_bud[facing=up,waterlogged=false]")
        for z in range(VZ - 1, VZ + 2):
            for y in range(1, 4):
                b.set(VX + 7, y, z, "minecraft:iron_bars[east=false,north=true,south=true,west=false,waterlogged=false]")
        b.set(VX + 7, 1, VZ, AIR); b.set(VX + 7, 2, VZ, AIR)
        for (x, z) in ((VX - 5, VZ), (VX + 5, VZ - 3), (VX, VZ + 5)):
            b.set(x, 5, z, SOUL_HANG)
        # --- The Neo Marine HQ (east): three floors of grey concrete, a purple band, his flag on the roof.
        HX0, HZ0, HX1, HZ1 = 52, 6, 82, 32
        b.hall(HX0, HZ0, HX1, HZ1, 0, 14, "minecraft:gray_concrete", "minecraft:polished_deepslate", MARINE_BRICK, trim="minecraft:purple_concrete",
               floor="minecraft:polished_andesite", win=pane("gray"), every=5, win_h=2, doors=[("south", 13, 5, 4), ("west", 12, 3, 3)])
        for y in (5, 10):
            b.box(HX0 + 1, y, HZ0 + 1, HX1 - 1, y, HZ1 - 1, "minecraft:polished_andesite")
            for x in range(HX0 + 2, HX1 - 1, 5):
                b.box(x, y + 2, HZ0, x, y + 3, HZ0, pane("gray")); b.box(x, y + 2, HZ1, x, y + 3, HZ1, pane("gray"))
        for y in range(1, 14):
            b.set(HX0 + 1, y, HZ0 + 2, ladder("east"))
        b.set(HX0 + 1, 5, HZ0 + 2, ladder("east")); b.set(HX0 + 1, 10, HZ0 + 2, ladder("east"))
        b.box(HX0 + 1, 14, HZ0 + 1, HX1 - 1, 14, HZ1 - 1, "minecraft:gray_concrete")
        b.walls(HX0, 15, HZ0, HX1, 15, HZ1, "minecraft:polished_deepslate_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]")
        b.set(HX0 + 1, 14, HZ0 + 2, AIR); b.set(HX0 + 1, 14, HZ0 + 2, ladder("east"))
        # ground floor: the mess hall
        for x in range(HX0 + 4, HX1 - 3, 6):
            b.table(x, 1, HZ0 + 8, "spruce", carpet("light_gray"), w=8, axis="z")
            for z in range(HZ0 + 8, HZ0 + 16, 2):
                b.chair(x - 1, 1, z, "spruce", "east"); b.chair(x + 1, 1, z, "spruce", "west")
        for x in range(HX1 - 9, HX1 - 1):
            b.set(x, 1, HZ0 + 1, "minecraft:smoker[facing=south,lit=true]" if x % 3 == 0 else facing("crate_stack", "south") if x % 3 == 1 else BARREL)
        for x in range(HX0 + 4, HX1, 6):
            b.set(x, 4, HZ0 + 12, HANG)
        # first floor: the barracks
        for x in range(HX0 + 3, HX1 - 2, 3):
            bed("black", x, 6, HZ0 + 1, b, "south"); bed("purple", x, 6, HZ1 - 2, b, "north")
            b.set(x + 1, 6, HZ0 + 1, facing("weapon_rack", "south")) if x % 2 else None
        for x in range(HX0 + 5, HX1, 8):
            b.set(x, 9, HZ0 + 13, HANG)
        # top floor: Zephyr's office, where the chest is, and his old Admiral's things
        OX = (HX0 + HX1) // 2
        b.chest(OX, 11, HZ0 + 1, "end_point", "south")
        b.table(OX - 3, 11, HZ0 + 4, "dark_oak", carpet("purple"), w=7)
        b.set(OX, 11, HZ0 + 6, facing("captains_chair", "north")) if False else b.set(OX, 11, HZ0 + 5, facing("captains_chair", "north"))
        b.shelf(OX - 10, 11, HZ0 + 1, h=3, n=5); b.shelf(OX + 6, 11, HZ0 + 1, h=3, n=5)
        b.set(OX - 5, 11, HZ0 + 1, facing("chart_table", "south"))
        b.box(OX + 2, 11, HZ0 + 1, OX + 3, 13, HZ0 + 1, "minecraft:purple_concrete")   # a spare Battle Smasher on its rack
        b.set(OX + 2, 13, HZ0 + 1, "minecraft:iron_block"); b.set(OX + 3, 12, HZ0 + 1, "minecraft:amethyst_block")
        for x in range(HX0 + 2, HX1 - 1):
            for z in (HZ1 - 2, HZ1 - 1):
                b.set(x, 11, z, carpet("purple"))
        b.set(OX, 13, HZ0 + 8, HANG); b.set(OX - 8, 13, HZ0 + 14, HANG); b.set(OX + 8, 13, HZ0 + 14, HANG)
        # roof: the flag, a searchlight and a radio mast
        b.flag(HX1 - 3, 15, HZ0 + 4, h=10, colors=("minecraft:black_wool", "minecraft:purple_wool"), skull=False, length=6)
        b.box(HX0 + 4, 15, HZ1 - 4, HX0 + 4, 26, HZ1 - 4, "minecraft:iron_bars[east=false,north=false,south=false,west=false,waterlogged=false]")
        b.set(HX0 + 4, 27, HZ1 - 4, "minecraft:redstone_block") if False else b.set(HX0 + 4, 27, HZ1 - 4, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
        b.set(HX0 + 8, 15, HZ0 + 6, "minecraft:iron_block"); b.set(HX0 + 8, 16, HZ0 + 6, "minecraft:sea_lantern")
        # --- The training ground (the arena, south): a ring of sandbags, dummies and racks of practice weapons.
        AX, AZ, R = 62, 60, 13
        for x in range(AX - R - 3, AX + R + 4):
            for z in range(AZ - R - 3, AZ + R + 4):
                d = math.hypot(x - AX, z - AZ)
                if d <= R:
                    b.set(x, 0, z, "minecraft:polished_andesite" if (x // 3 + z // 3) % 2 else "minecraft:gray_concrete_powder")
                elif d <= R + 1.5:
                    gap = any(abs(math.degrees(math.atan2(z - AZ, x - AX)) - a) < 6 for a in (-90, 90, 0, 180, -180))
                    if not gap:
                        b.box(x, 1, z, x, 2, z, "minecraft:packed_mud" if (x + z) % 3 else "minecraft:mud_bricks")
                        b.set(x, 3, z, "minecraft:mud_brick_slab[type=bottom,waterlogged=false]")
        b.disk(AX, 0, AZ, 2.5, MARINE_TILE)
        for i in range(0, 360, 40):   # target dummies
            a = math.radians(i)
            x, z = round(AX + (R + 5) * math.cos(a)), round(AZ + (R + 5) * math.sin(a))
            if 1 < x < W - 1 and 1 < z < D - 1 and b.get(x, 1, z) is None:
                b.set(x, 1, z, "minecraft:dark_oak_fence[east=false,north=false,south=false,west=false,waterlogged=false]")
                b.set(x, 2, z, "minecraft:hay_block[axis=y]"); b.set(x, 3, z, "minecraft:carved_pumpkin[facing=south]")
        for x in range(AX - 6, AX + 7, 3):
            b.set(x, 1, AZ + R + 4, facing("weapon_rack", "north"))
        # --- The dry dock (south-west): a Neo Marine battleship up on its cradle.
        sy = 3
        deck = b.ship(4, sy, 64, 40, 13, hull="minecraft:black_concrete", deck="minecraft:dark_oak_planks", masts=((12, 16), (26, 18)),
                      sail="minecraft:purple_wool", flag=("minecraft:black_wool", "minecraft:purple_wool"), cabin=(8, 4, "minecraft:gray_concrete"))
        b.mast_yard(4, deck, 64, 13, ((12, 16), (26, 18)))
        b.support(0, 60, 48, 80, sy, ["minecraft:stone_bricks", "minecraft:polished_andesite"], rnd, down_to=1)
        for x in range(8, 42, 5):
            b.set(x, deck + 1, 66, facing("cannon", "north")); b.set(x, deck + 1, 76, facing("cannon", "south"))
        for (gx) in (6, 40):    # the gantry over the dock
            for gz in (61, 80):
                b.box(gx, 1, gz, gx, 20, gz, MARINE_BRICK)
            b.box(gx, 20, 61, gx, 20, 80, "minecraft:iron_block")
        # --- Two watchtowers, cannons on the cliff edge and a fuel dump.
        for (tx, tz) in ((84, 42), (6, 50)):
            b.tower(tx, tz, 3, 18, "minecraft:gray_concrete", roof=None, floors=[9])
            b.set(tx, 19, tz, "minecraft:sea_lantern"); b.set(tx, 20, tz, slab("smooth_stone"))
        for z in range(40, 80, 7):
            b.box(W - 2, 1, z - 1, W - 2, 1, z + 1, "minecraft:mud_bricks")
            b.set(W - 3, 1, z, facing("cannon", "east")); b.set(W - 4, 1, z, facing("cannonball_pile", "east"))
        for (x, z) in ((54, 38), (60, 40), (66, 38), (72, 40)):
            b.set(x, 1, z, BARREL); b.set(x, 2, z, "minecraft:tnt[unstable=false]") if False else b.set(x + 1, 1, z, facing("crate_stack", "north"))
        for (x, z) in ((48, 36), (78, 36), (60, 80), (30, 44)):
            b.lamp_post(x, 1, z, "dark_oak", 4, LANTERN, arm="south")

        b.rogue(AX, 1, AZ, "zephyr_z")
        b.crew("neo_marine", ((AX - 8, AZ - 7), (AX + 8, AZ - 7), (AX - 8, AZ + 7), (AX + 8, AZ + 7), (HX0 + 8, HZ1 + 3), (VX + VR + 4, VZ)))
        b.crew("neo_marine", ((OX + 4, HZ0 + 10),), y=11)

    # ============================================================ Douglas Bullet: the Ironclad Colosseum
    @lair("ironclad_colosseum", "The Ironclad Colosseum", "douglas_bullet",
          ["minecraft:desert", "minecraft:savanna", "minecraft:windswept_savanna", "minecraft:plains", "onepiece:alabasta"], "land", group="film_lairs")
    def _(b):
        rnd = random.Random(14)
        W, D = 92, 96
        ground = ["minecraft:coarse_dirt", "minecraft:sand", "minecraft:red_sand", "minecraft:gravel", "minecraft:coarse_dirt", "minecraft:packed_mud"]
        for x in range(0, W + 1):
            for z in range(0, D + 1):
                b.set(x, -1, z, "minecraft:dirt"); b.set(x, 0, z, rnd.choice(ground))
        SCRAP = ["minecraft:iron_block", "minecraft:waxed_exposed_cut_copper", "minecraft:waxed_oxidized_copper", "minecraft:waxed_weathered_copper",
                 "minecraft:polished_blackstone", "minecraft:stripped_dark_oak_wood[axis=y]", "minecraft:dark_oak_planks", "minecraft:iron_block",
                 "minecraft:waxed_weathered_cut_copper", "minecraft:heavy_core" if False else "minecraft:iron_block", "minecraft:deepslate_tiles"]
        # --- The colosseum (the arena): an oval of fused scrap 15 high, seats inside, a sand floor in the middle.
        CX, CZ, AXR, AZR = 46, 62, 30, 25
        for x in range(CX - AXR - 1, CX + AXR + 2):
            for z in range(CZ - AZR - 1, CZ + AZR + 2):
                e = math.hypot((x - CX) / AXR, (z - CZ) / AZR)
                ang = math.degrees(math.atan2((z - CZ) / AZR, (x - CX) / AXR)) % 360
                gate = min(abs(ang - g) for g in (0, 90, 180, 270, 360)) < 5.5
                if e <= 0.5:
                    b.set(x, 0, z, "minecraft:sand" if rnd.random() < 0.7 else "minecraft:coarse_dirt")
                elif e <= 0.86:
                    tier = int((e - 0.5) / 0.36 * 11)
                    if gate:
                        b.set(x, 0, z, "minecraft:polished_andesite")
                        continue
                    for y in range(0, tier + 1):
                        b.set(x, y, z, "minecraft:stone_bricks")
                    b.set(x, tier, z, "minecraft:polished_andesite" if tier % 2 else "minecraft:smooth_stone")
                    if tier == 0:
                        b.set(x, 1, z, "minecraft:iron_bars[east=false,north=false,south=false,west=false,waterlogged=false]")
                elif e <= 1.0:
                    arch = int(ang) % 12 < 4
                    for y in range(0, 16):
                        if gate and y < 7:
                            b.set(x, y, z, AIR if y > 0 else "minecraft:polished_andesite")
                            continue
                        if arch and 1 <= y <= 5 and e > 0.95:
                            continue
                        b.set(x, y, z, rnd.choice(SCRAP))
                    if int(ang) % 4 == 0:
                        b.set(x, 16, z, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
                    if int(ang) % 12 == 2 and e > 0.95:
                        b.set(x, 6, z, HANG)
        # the seats' inner rim gets railings, the arena a scatter of broken weapons and an iron plate in the middle
        b.disk(CX, 0, CZ, 2.5, "minecraft:iron_block")
        b.set(CX, 0, CZ, "minecraft:chiseled_polished_blackstone")
        b.scatter(CX - 14, CZ - 12, CX + 14, CZ + 12, 1, ["minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]", "minecraft:anvil[facing=north]",
                  "minecraft:chipped_anvil[facing=east]", wall_post("cobblestone"), "minecraft:skeleton_skull[rotation=4]"], 0.025, rnd)
        b.set(CX, 1, CZ, AIR)
        # a crow's nest of a box for the "host" above the south gate
        b.box(CX - 3, 16, CZ + AZR - 3, CX + 3, 16, CZ + AZR, "minecraft:dark_oak_planks")
        b.walls(CX - 3, 17, CZ + AZR - 3, CX + 3, 17, CZ + AZR, "minecraft:dark_oak_fence[east=false,north=false,south=false,west=false,waterlogged=false]")
        b.flag(CX, 17, CZ + AZR - 1, h=9, colors=("minecraft:red_wool", "minecraft:black_wool"), skull=True)
        # --- The Gashapon (the landmark): Bullet's dormant war machine, sitting with its back to the north wall.
        MX, MZ = CX, CZ - AZR - 4          # the back of the mech
        def scrap(x0, y0, z0, x1, y1, z1, p=1.0):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                for y in range(min(y0, y1), max(y0, y1) + 1):
                    for z in range(min(z0, z1), max(z0, z1) + 1):
                        if rnd.random() < p:
                            b.set(x, y, z, rnd.choice(SCRAP))
        scrap(MX - 9, 1, MZ - 12, MX + 9, 22, MZ + 1)          # the body, slumped on its seat
        scrap(MX - 10, 0, MZ - 12, MX + 10, 3, MZ + 2)
        scrap(MX - 8, 1, MZ - 26, MX - 3, 6, MZ - 12)          # legs stretched out north
        scrap(MX + 3, 1, MZ - 26, MX + 8, 6, MZ - 12)
        scrap(MX - 9, 1, MZ - 30, MX - 2, 9, MZ - 26)          # feet, toes up
        scrap(MX + 2, 1, MZ - 30, MX + 9, 9, MZ - 26)
        scrap(MX - 12, 18, MZ - 10, MX + 12, 24, MZ + 0)       # shoulders
        scrap(MX - 5, 25, MZ - 9, MX + 5, 33, MZ - 1)          # head
        for (ex) in (MX - 3, MX + 2):
            b.box(ex, 29, MZ - 10, ex + 1, 30, MZ - 10, "minecraft:shroomlight")   # its eyes, still glowing
        b.box(MX - 3, 26, MZ - 10, MX + 3, 26, MZ - 10, "minecraft:iron_bars[east=true,north=false,south=false,west=true,waterlogged=false]")   # grille jaw
        for i in range(3):   # horns of ship's ribs
            b.box(MX - 6 - i, 33 + i * 2, MZ - 5, MX - 6 - i, 34 + i * 2, MZ - 5, log("dark_oak"))
            b.box(MX + 6 + i, 33 + i * 2, MZ - 5, MX + 6 + i, 34 + i * 2, MZ - 5, log("dark_oak"))
        scrap(MX - 20, 0, MZ - 22, MX - 13, 7, MZ - 6)         # left arm resting on the ground, fist forward
        scrap(MX - 21, 0, MZ - 28, MX - 12, 8, MZ - 22)
        scrap(MX - 18, 8, MZ - 10, MX - 13, 20, MZ - 4)
        for t in range(0, 14):                                 # right arm draped over the colosseum wall
            z = MZ - 4 + t
            y = 22 - max(0, t - 6) // 2 + (2 if 5 < t < 10 else 0)
            scrap(MX + 13, y - 3, z, MX + 18, y, z)
        scrap(MX + 12, 12, MZ + 10, MX + 19, 18, MZ + 14)        # its hand, gripping the rim
        for (cx2, cz2, f) in ((MX - 11, MZ - 6, "north"), (MX + 11, MZ - 6, "north"), (MX, MZ - 11, "north")):
            b.set(cx2, 25 if cx2 != MX else 23, cz2, facing("cannon", f))
        b.set(MX - 2, 22, MZ - 13, facing("ships_wheel", "north"))
        for y in range(1, 22):   # a way up its back for the brave
            b.set(MX, y, MZ + 2, ladder("south"))
        # --- Bullet's camp (south-east, outside the walls): where he sleeps, trains and keeps the chest.
        KX, KZ = 80, 82
        for x in range(KX - 9, KX + 2):                         # a lean-to of hull plates
            for z in range(KZ - 7, KZ + 1):
                if z == KZ - 7 or x in (KX - 9, KX + 1):
                    for y in range(1, 6 - (0 if z == KZ - 7 else 0)):
                        b.set(x, y, z, rnd.choice(["minecraft:iron_block", "minecraft:stripped_dark_oak_wood[axis=y]", "minecraft:waxed_oxidized_cut_copper"]))
                b.set(x, 6 - (z - (KZ - 7)) // 3, z, "minecraft:waxed_oxidized_cut_copper_slab[type=bottom,waterlogged=false]")
        b.chest(KX - 4, 1, KZ - 6, "ironclad_colosseum", "south")
        for x in range(KX - 8, KX - 5):
            for z in range(KZ - 6, KZ - 3):
                b.set(x, 1, z, carpet("brown"))
        b.set(KX - 8, 1, KZ - 6, "minecraft:brown_wool")
        b.set(KX - 2, 1, KZ - 6, "minecraft:anvil[facing=north]"); b.set(KX - 1, 1, KZ - 6, "minecraft:iron_block")
        b.set(KX - 4, 1, KZ + 3, CAMPFIRE)
        for (dx, dz) in ((-1, 0), (1, 0), (0, 1)):
            b.set(KX - 4 + dx, 1, KZ + 3 + dz, "minecraft:polished_blackstone_slab[type=bottom,waterlogged=false]") if dz == 0 else None
        for (x, z) in ((KX - 12, KZ - 2), (KX - 12, KZ - 5)):   # his weights: iron blocks on chains between posts
            b.box(x, 1, z, x, 4, z, "minecraft:dark_oak_fence[east=false,north=false,south=false,west=false,waterlogged=false]")
        b.box(KX - 12, 5, KZ - 5, KX - 12, 5, KZ - 2, log("dark_oak", "z"))
        b.set(KX - 12, 4, KZ - 4, CHAIN); b.set(KX - 12, 3, KZ - 4, "minecraft:iron_block")
        b.set(KX - 12, 4, KZ - 3, CHAIN); b.set(KX - 12, 3, KZ - 3, "minecraft:iron_block")
        for i in range(5):   # trophies of the people he fought: weapons stuck in the ground
            b.set(KX - 9 + i * 2, 1, KZ + 6, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
            b.set(KX - 8 + i * 2, 1, KZ + 6, facing("weapon_rack", "north")) if i % 2 else None
        b.set(KX - 4, 5, KZ - 4, HANG)
        # --- Two wrecked ships he tore apart for scrap, half-buried east and west.
        for (sx, sz, L) in ((2, 38, 22), (W - 32, 8, 26)):
            deck = b.ship(sx, -3, sz, L, 11, hull="minecraft:dark_oak_planks", deck="minecraft:spruce_planks", masts=((L // 2, 12),),
                          sail="minecraft:light_gray_wool", cabin=None)
            for _ in range(70):
                x = rnd.randint(sx, sx + L - 1); z = rnd.randint(sz, sz + 10); y = rnd.randint(-1, deck + 6)
                b.set(x, y, z, AIR)
            b.mast_yard(sx, deck, sz, 11, ((L // 2, 12),))
        # --- Scrap heaps everywhere, and the road in from the south.
        for (x, z) in ((8, 60), (6, 78), (W - 8, 44), (W - 6, 62), (20, 90), (60, 3), (8, 26)):
            b.sphere(x, 0, z, 3.2, "minecraft:iron_block", ry=2.4, upper=True)
            b.scatter(x - 3, z - 3, x + 3, z + 3, 1, SCRAP[:5] + ["minecraft:anvil[facing=east]", BARREL], 0.35, rnd)
        for z in range(CZ + AZR, D + 1):
            for x in range(CX - 2, CX + 3):
                b.set(x, 0, z, "minecraft:gravel" if abs(x - CX) < 2 else "minecraft:cobblestone")
        for (x, z) in ((CX - 4, CZ + AZR + 4), (CX + 4, CZ + AZR + 4), (CX - 4, D - 2), (CX + 4, D - 2)):
            b.lamp_post(x, 1, z, "dark_oak", 4, LANTERN)

        b.rogue(CX, 1, CZ, "douglas_bullet")

    # ============================================================ Shiki: Merveille, the floating islands
    @lair("merveille", "Merveille", "shiki_golden_lion",
          ["#minecraft:is_jungle", "onepiece:little_garden"], "land", group="film_lairs")
    def _(b):
        rnd = random.Random(15)
        W, D = 90, 92
        grass = ["minecraft:grass_block"] * 3 + ["minecraft:moss_block", "minecraft:podzol"]
        ROCK = ["minecraft:stone", "minecraft:andesite", "minecraft:mossy_cobblestone", "minecraft:stone", "minecraft:tuff", "minecraft:cobblestone"]
        for x in range(0, W + 1):
            for z in range(0, D + 1):
                b.set(x, -1, z, "minecraft:dirt"); b.set(x, 0, z, rnd.choice(grass))
        # --- The Lion's Court (the arena, south): a round court of mossy stone ringed by stone lions with gold manes.
        AX, AZ, R = 45, 68, 12
        for x in range(AX - R - 1, AX + R + 2):
            for z in range(AZ - R - 1, AZ + R + 2):
                d = math.hypot(x - AX, z - AZ)
                if d <= R + 0.5:
                    b.set(x, 0, z, "minecraft:mossy_stone_bricks" if rnd.random() < 0.35 else "minecraft:stone_bricks" if d < R - 0.5 else "minecraft:chiseled_stone_bricks")
        b.disk(AX, 0, AZ, 3.5, GOLD_BRICK)
        b.disk(AX, 0, AZ, 1.5, "minecraft:gold_block")
        for i in range(0, 360, 45):   # stone lions on plinths, facing in
            a = math.radians(i)
            x, z = round(AX + (R + 3) * math.cos(a)), round(AZ + (R + 3) * math.sin(a))
            b.box(x - 1, 1, z - 1, x + 1, 2, z + 1, "minecraft:stone_bricks")
            b.box(x - 1, 3, z - 1, x + 1, 4, z + 1, "minecraft:smooth_stone")
            b.box(x - 1, 5, z - 1, x + 1, 7, z + 1, "minecraft:honeycomb_block")   # the mane
            b.set(x, 6, z, "minecraft:smooth_stone")
            b.set(x, 8, z, CAMPFIRE) if i % 90 == 0 else b.set(x, 8, z, slab(GOLD_FAM))
        for i in range(10, 360, 30):
            a = math.radians(i)
            b.stone_lantern(round(AX + (R + 1) * math.cos(a)), 1, round(AZ + (R + 1) * math.sin(a)), "stone_brick", LANTERN)
        # --- The beast pens (west of the court): iron cages of Shiki's mutated beasts.
        for k, (px, pz, beast) in enumerate(((10, 54, "onepiece:manticore"), (10, 66, "onepiece:basilisk"), (10, 78, "onepiece:humandrill"), (22, 84, "onepiece:manticore"))):
            b.box(px - 3, 0, pz - 3, px + 3, 0, pz + 3, "minecraft:mossy_stone_bricks")
            for x in range(px - 3, px + 4):
                for z in range(pz - 3, pz + 4):
                    if x in (px - 3, px + 3) or z in (pz - 3, pz + 3):
                        b.box(x, 1, z, x, 5, z, "minecraft:iron_bars[east=true,north=true,south=true,west=true,waterlogged=false]" if (x + z) % 3 else MARINE_BRICK if False else log("dark_oak"))
            b.box(px - 3, 6, pz - 3, px + 3, 6, pz + 3, "minecraft:dark_oak_planks")
            b.set(px, 5, pz, HANG)
            b.set(px + 2, 1, pz + 2, "minecraft:bone_block[axis=y]"); b.set(px - 2, 1, pz - 2, "minecraft:hay_block[axis=x]")
            b.beast(beast, ((px, pz),))
        # --- The tether spire (the way up): a rock pillar with a stair winding round it to the floating island.
        TX, TZ, TR = 45, 34, 5
        top = 34
        for y in range(0, top + 1):
            r = TR - 1.5 * math.sin(math.pi * y / top)
            b.cyl(TX, TZ, r, y, y, rnd.choice(ROCK))
        IY = 36                                  # the floating island's top
        steps = 0
        y = 1
        a = math.radians(90)
        stair_path = []
        while y <= IY:
            r = TR + 1.2
            x, z = round(TX + r * math.cos(a)), round(TZ + r * math.sin(a))
            b.set(x, y - 1, z, "minecraft:mossy_stone_bricks")
            b.set(x, y, z, slab("mossy_stone_brick")) if steps % 2 else None
            ox, oz = round(TX + (r + 1) * math.cos(a)), round(TZ + (r + 1) * math.sin(a))
            b.set(ox, y, oz, "minecraft:mossy_stone_brick_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]") if steps % 3 == 0 else None
            if steps % 10 == 5:
                b.set(ox, y + 1, oz, LANTERN)
            stair_path.append((x, y, z, steps))
            a += math.radians(11)
            steps += 1
            if steps % 2 == 0:
                y += 1
        # --- The floating island (the landmark): an upturned mountain hanging in the sky over the spire.
        for yy in range(IY - 16, IY + 1):
            depth = IY - yy
            r = 22 * (1 - (depth / 17) ** 1.4)
            for x in range(int(TX - r) - 1, int(TX + r) + 2):
                for z in range(int(TZ - r * 0.9) - 1, int(TZ + r * 0.9) + 2):
                    d = math.hypot(x - TX, (z - TZ) / 0.9) + rnd.random() * 1.8
                    if d <= r and 0 <= x <= W and 0 <= z <= D:
                        b.set(x, yy, z, rnd.choice(grass) if yy == IY else "minecraft:dirt" if yy > IY - 3 else rnd.choice(ROCK))
        for _ in range(60):   # roots and vines hanging off its underside
            x = rnd.randint(TX - 18, TX + 18); z = rnd.randint(TZ - 16, TZ + 16)
            yy = IY - 1
            while yy > IY - 18 and b.get(x, yy, z) not in (None, AIR):
                yy -= 1
            if b.get(x, yy + 1, z) not in (None, AIR):
                for k in range(rnd.randint(2, 7)):
                    b.set(x, yy - k, z, "minecraft:hanging_roots[waterlogged=false]" if k == 0 else "minecraft:cave_vines_plant[berries=false]")
                if b.get(x, yy - 1, z) == "minecraft:cave_vines_plant[berries=false]":
                    pass
        for (x, y, z, k) in stair_path:   # the stair climbs on through the island's rock and comes out on top
            if y >= IY - 17:
                for dy in range(1, 4):
                    if y + dy <= IY + 1 and b.get(x, y + dy, z) not in (None, AIR) and math.hypot(x - TX, z - TZ) > TR - 0.5:
                        b.set(x, y + dy, z, AIR)
                b.set(x, y - 1, z, "minecraft:mossy_stone_bricks")
                b.set(x, y, z, slab("mossy_stone_brick") if k % 2 else AIR)
        # Shiki's palace on the island: a black and gold hall with a lion's head for a gate, his throne and the chest.
        PX0, PZ0, PX1, PZ1 = TX - 13, TZ - 15, TX + 13, TZ + 3
        b.hall(PX0, PZ0, PX1, PZ1, IY, 9, "minecraft:polished_blackstone_bricks", "minecraft:polished_blackstone", log("dark_oak"), trim=GOLD_BRICK,
               floor="minecraft:dark_oak_planks", win=pane("yellow"), every=4, win_h=3, doors=[("south", 11, 5, 5)])
        b.pagoda_roof(PX0, PZ0, PX1, PZ1, IY + 9, "deepslate_tile", "minecraft:deepslate_tiles", ov=2)
        b.box(TX - 5, IY + 14, PZ0 + 4, TX + 5, IY + 18, PZ1 - 4, "minecraft:polished_blackstone_bricks")
        b.pagoda_roof(TX - 5, PZ0 + 4, TX + 5, PZ1 - 4, IY + 19, "deepslate_tile", "minecraft:deepslate_tiles", ov=2)
        b.set(TX, IY + 25, (PZ0 + PZ1) // 2, "minecraft:gold_block") if False else b.set(TX, IY + 24, (PZ0 + PZ1) // 2, GOLD_BRICK)
        # the lion's head on the south front, its open mouth the gate
        hz = PZ1 + 1
        for x in range(TX - 9, TX + 10):
            for y in range(IY + 1, IY + 18):
                d = math.hypot(x - TX, (y - (IY + 8)) * 1.0)
                if d <= 9:
                    s = rnd.choice(["minecraft:honeycomb_block", GOLD_BRICK, "minecraft:orange_terracotta"]) if d > 5.5 else "minecraft:yellow_terracotta"
                    b.set(x, y, hz, s)
        for (ex) in (TX - 3, TX + 3):
            b.set(ex, IY + 10, hz + 1, "minecraft:black_concrete"); b.set(ex, IY + 11, hz + 1, "minecraft:ochre_froglight[axis=y]")
        b.box(TX - 1, IY + 7, hz + 1, TX + 1, IY + 8, hz + 1, "minecraft:brown_terracotta")   # nose
        b.box(TX - 2, IY + 1, hz, TX + 2, IY + 5, hz + 1, AIR)   # mouth = the gate
        for x in (TX - 2, TX + 2):
            b.set(x, IY + 5, hz + 1, "minecraft:pointed_dripstone[thickness=tip,vertical_direction=down,waterlogged=false]")   # fangs
        b.box(TX - 2, IY + 1, PZ1, TX + 2, IY + 5, PZ1, AIR)
        # inside: the throne under a wheel, a war table, beds and the chest
        b.box(TX - 3, IY + 1, PZ0 + 1, TX + 3, IY + 1, PZ0 + 3, GOLD_BRICK)
        b.set(TX, IY + 2, PZ0 + 2, facing("throne", "south"))
        b.set(TX, IY + 5, PZ0 + 1, facing("ships_wheel", "south"))
        b.chest(TX + 3, IY + 2, PZ0 + 1, "merveille", "south")
        b.set(TX - 3, IY + 2, PZ0 + 1, facing("wine_rack", "south"))
        b.table(TX - 3, IY + 1, PZ0 + 7, "dark_oak", carpet("yellow"), w=7)
        b.set(TX, IY + 1, PZ0 + 9, facing("chart_table", "north"))
        for x in range(PX0 + 2, PX0 + 8, 2):
            bed("yellow", x, IY + 1, PZ1 - 3, b, "south")
        for x in range(PX1 - 7, PX1 - 1, 2):
            b.set(x, IY + 1, PZ1 - 2, facing("weapon_rack", "north"))
        for (lx, lz) in ((TX - 8, PZ0 + 8), (TX + 8, PZ0 + 8), (TX, PZ0 + 12)):
            b.hang_from(lx, IY + 7, lz, facing("chandelier", "north"), up=3)
        for x in range(TX - 2, TX + 3):   # a gold carpet from the gate to the throne
            for z in range(PZ0 + 4, PZ1):
                if b.get(x, IY + 1, z) is None:
                    b.set(x, IY + 1, z, carpet("yellow"))
        # jungle on the island, round the palace
        for (x, z) in ((TX - 17, TZ + 4), (TX + 16, TZ + 6), (TX - 14, TZ + 12), (TX + 12, TZ + 13), (TX - 18, TZ - 8), (TX + 18, TZ - 6)):
            if b.get(x, IY, z) in grass:
                b.tree(x, IY + 1, z, 7, "jungle", 3.0)
        b.scatter(TX - 20, TZ - 18, TX + 20, TZ + 18, IY + 1, ["minecraft:fern", "minecraft:short_grass", "minecraft:large_fern[half=lower]" if False else "minecraft:fern"], 0.1, rnd, only_on=grass)
        # --- Floating islets (Shiki's fruit at work): three small rocks hanging free in the air, one with a sky-shrine.
        for (ix, iy, iz, ir) in ((12, 26, 20, 5), (78, 30, 26, 6), (74, 22, 58, 4)):
            for yy in range(iy - ir, iy + 1):
                rr = ir * (1 - ((iy - yy) / (ir + 1)) ** 1.3)
                for x in range(int(ix - rr) - 1, int(ix + rr) + 2):
                    for z in range(int(iz - rr) - 1, int(iz + rr) + 2):
                        if math.hypot(x - ix, z - iz) + rnd.random() <= rr and 0 <= x <= W and 0 <= z <= D:
                            b.set(x, yy, z, "minecraft:grass_block" if yy == iy else rnd.choice(ROCK))
            b.tree(ix, iy + 1, iz, 5, "jungle", 2.2) if ir < 6 else b.stone_lantern(ix, iy + 1, iz, "stone_brick", LANTERN)
        # Shiki's flagship, floating beside the island with its sails set
        fdeck = b.ship(58, 24, 66, 30, 11, hull="minecraft:dark_oak_planks", deck="minecraft:spruce_planks", masts=((10, 14), (20, 15)),
                       sail="minecraft:yellow_wool", flag=("minecraft:black_wool", "minecraft:yellow_wool"), cabin=(6, 4, "minecraft:dark_oak_planks"))
        b.mast_yard(58, fdeck, 66, 11, ((10, 14), (20, 15)))
        b.set(58 + 26, fdeck + 1, 71, facing("ships_wheel", "west")) if False else None
        # --- The jungle floor: giant flowers and mushrooms grown wrong by Shiki's IQ plant, the road in.
        for (x, z, h, col) in ((70, 46, 9, "red"), (78, 80, 7, "magenta"), (30, 50, 8, "orange"), (64, 86, 10, "purple"), (6, 36, 7, "red"), (84, 10, 8, "orange")):
            b.box(x, 1, z, x, h, z, "minecraft:green_concrete")
            b.disk(x, h + 1, z, 2.6, f"minecraft:{col}_wool")
            b.set(x, h + 1, z, "minecraft:yellow_wool"); b.set(x, h + 2, z, "minecraft:yellow_wool")
            for (dx, dz) in ((1, 0), (-1, 0)):
                b.set(x + dx * 2, h // 2, z, "minecraft:moss_block")
        for (x, z, r) in ((58, 40, 4), (24, 72, 3.5), (82, 66, 3)):
            b.box(x, 1, z, x, 7, z, "minecraft:mushroom_stem[down=true,east=true,north=true,south=true,up=true,west=true]")
            b.sphere(x, 7, z, r, "minecraft:red_mushroom_block[down=true,east=true,north=true,south=true,up=true,west=true]", hollow=True, upper=True, ry=r * 0.7)
        for (x, z, h) in ((4, 8, 9), (24, 6, 10), (66, 8, 11), (86, 40, 9), (4, 90, 8), (40, 90, 9), (86, 90, 8), (66, 60, 8)):
            if b.get(x, 1, z) is None:
                b.tree(x, 1, z, h, "jungle", 3.4)
        for z in range(AZ + R + 1, D + 1):
            for x in range(AX - 2, AX + 3):
                b.set(x, 0, z, "minecraft:mossy_cobblestone" if abs(x - AX) == 2 else "minecraft:gravel")
        for z in range(TZ + TR + 1, AZ - R):
            for x in range(AX - 1, AX + 2):
                b.set(x, 0, z, "minecraft:gravel")
        b.scatter(0, 0, W, D, 1, ["minecraft:fern", "minecraft:short_grass", "minecraft:short_grass", "minecraft:bush" if False else "minecraft:fern"], 0.08, rnd, only_on=grass)

        b.rogue(AX, 1, AZ, "shiki_golden_lion")
        b.crew("golden_lion_pirate", ((AX - 8, AZ - 6), (AX + 8, AZ - 6), (AX - 8, AZ + 6), (AX + 8, AZ + 6), (22, 60)))
        b.crew("golden_lion_pirate", ((TX - 6, PZ1 + 4), (TX + 6, PZ1 + 4)), y=IY + 1)


def item(name, weight, lo=1, hi=1, extra=None):
    e = {"type": "minecraft:item", "name": name, "weight": weight}
    mods = []
    if hi > 1 or lo > 1:
        mods.append({"type": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}})
    if extra:
        mods.append(extra)
    if mods:
        e["modifier"] = mods
    return e


def table(*pools):
    return {"type": "minecraft:chest", "pools": [{"rolls": {"type": "minecraft:uniform", "min": lo, "max": hi}, "entries": es} for lo, hi, es in pools]}


BERRY = "onepiece:berry"
ENCHANT = {"type": "minecraft:enchant_randomly"}


def rumor(boss):
    return (1, 1, [item(f"opbosses:rumor_{boss}", 1)])


LOOT = {
    "gran_tesoro": table((6, 10, [item(BERRY, 12, 40, 64), item("minecraft:gold_block", 6, 1, 4), item("minecraft:gold_ingot", 10, 4, 16),
                                  item("minecraft:emerald", 6, 2, 8), item("minecraft:diamond", 5, 1, 4), item("minecraft:golden_apple", 5, 1, 3),
                                  item("minecraft:enchanted_golden_apple", 1), item("minecraft:golden_sword", 2, 1, 1, ENCHANT),
                                  item("onepiece:berry_block", 3, 1, 2)]), rumor("gild_tesoro")),
    "elegia_stage": table((6, 10, [item(BERRY, 10, 24, 48), item("minecraft:music_disc_pigstep", 2), item("minecraft:music_disc_otherside", 2),
                                   item("minecraft:music_disc_cat", 3), item("minecraft:music_disc_chirp", 3), item("minecraft:jukebox", 3),
                                   item("minecraft:note_block", 6, 2, 6), item("minecraft:amethyst_shard", 6, 2, 8), item("minecraft:diamond", 5, 1, 3),
                                   item("minecraft:enchanted_golden_apple", 1), item("minecraft:golden_apple", 4, 1, 2)]),
                         (1, 1, [item("minecraft:enchanted_book", 1, 1, 1, ENCHANT)]), rumor("uta_diva")),
    "end_point": table((6, 10, [item(BERRY, 10, 32, 64), item("onepiece:seastone_ingot", 8, 2, 5), item("onepiece:seastone_cuffs", 4),
                                item("minecraft:amethyst_shard", 8, 4, 12), item("minecraft:diamond", 6, 2, 5), item("minecraft:netherite_scrap", 4, 1, 2),
                                item("minecraft:netherite_ingot", 1), item("minecraft:enchanted_golden_apple", 2), item("minecraft:gunpowder", 6, 4, 10)]),
                       rumor("zephyr_z")),
    "ironclad_colosseum": table((6, 10, [item(BERRY, 10, 32, 64), item("minecraft:iron_block", 8, 2, 5), item("minecraft:netherite_scrap", 5, 1, 3),
                                         item("minecraft:netherite_ingot", 2), item("minecraft:diamond", 6, 2, 6), item("minecraft:anvil", 3),
                                         item("minecraft:mace", 2, 1, 1, ENCHANT), item("minecraft:heavy_core", 1), item("minecraft:totem_of_undying", 2),
                                         item("minecraft:enchanted_golden_apple", 2)]), rumor("douglas_bullet")),
    "merveille": table((6, 10, [item(BERRY, 10, 32, 64), item("minecraft:gold_ingot", 8, 4, 12), item("minecraft:diamond", 6, 2, 6),
                                item("minecraft:netherite_ingot", 2), item("minecraft:elytra", 1), item("minecraft:phantom_membrane", 5, 2, 6),
                                item("minecraft:feather", 6, 4, 12), item("minecraft:enchanted_golden_apple", 2), item("minecraft:totem_of_undying", 2),
                                item("minecraft:diamond_sword", 3, 1, 1, ENCHANT)]),
                       (2, 2, [item("minecraft:enchanted_book", 1, 1, 1, ENCHANT)]), rumor("shiki_golden_lion")),
}
