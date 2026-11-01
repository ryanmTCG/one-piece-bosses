"""More film villains' lairs: El Drago (One Piece: The Movie), Gasparde (Dead End Adventure), Baron Omatsuri (Baron
Omatsuri and the Secret Island), Dr. Ratchet (The Giant Mechanical Soldier of Karakuri Castle) and Byrnndi World (3D2Y).
gen_lairs.py calls add() to register them in the film_lairs structure set, like film_lairs.py.
Same rules as every lair here: a compound 80-110 blocks across, an approach, an arena at the heart, the boss's own
quarters with the chest, crew quarters, props everywhere, several levels and a landmark you can see from far off."""
import math
import random

from kit import AIR, FENCE, LANTERN, HANG, BARREL, CHAIN, PANE, CAMPFIRE, log, leaves, pane, ladder, bed  # noqa: F401
from parts import (stair, slab, trap, wall_post, fence, candle, carpet, CHAIN_X, CHAIN_Z, SOUL_HANG, SOUL_LANTERN,  # noqa: F401
                   SMOKE, SOUL_FIRE, WATER)
from film_lairs import GOLD_BRICK, GOLD_FAM, MARINE_BRICK, facing, note_block, item, table, rumor, BERRY, ENCHANT  # noqa: F401

BARS = "minecraft:iron_bars[east=false,north=false,south=false,west=false,waterlogged=false]"
BARS_X = "minecraft:iron_bars[east=true,north=false,south=false,west=true,waterlogged=false]"
BARS_Z = "minecraft:iron_bars[east=false,north=true,south=true,west=false,waterlogged=false]"
ROD = "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]"
PAPER_LANTERN = "onepiece:paper_lantern[hanging=false]"
PAPER_HANG = "onepiece:paper_lantern[hanging=true]"


def clear_spawns(b):
    """Natural terrain stays wherever a lair has no block of its own, so a hill can poke up through it: make sure every
    spawn has a clear 3x3 column round it (three blocks high, five for the boss), whatever the ground was."""
    for (eid, x, y, z, _data) in b.entities:
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                for yy in range(y, y + (5 if eid == "opbosses:rogue_boss" else 3)):   # the bosses are big
                    if b.get(x + dx, yy, z + dz) is None:
                        b.set(x + dx, yy, z + dz, AIR)


def add(lair, OCEANS, DEEP):
    """Registers the five lairs with gen_lairs's @lair decorator."""

    # ============================================================ El Drago: Gold Island
    @lair("gold_island", "Gold Island", "el_drago",
          ["#minecraft:is_beach", "minecraft:stony_shore", "minecraft:jungle", "minecraft:sparse_jungle"], "land", group="film_lairs")
    def _(b):
        rnd = random.Random(21)
        W, D = 96, 92
        sand = ["minecraft:sand"] * 3 + ["minecraft:suspicious_sand" if False else "minecraft:sand", "minecraft:gravel"]
        grass = ["minecraft:grass_block"] * 4 + ["minecraft:coarse_dirt", "minecraft:podzol"]
        ROCK = ["minecraft:stone", "minecraft:andesite", "minecraft:stone", "minecraft:tuff", "minecraft:granite"]
        GOLDS = ["minecraft:gold_ore", "minecraft:raw_gold_block", GOLD_BRICK]
        for x in range(0, W + 1):
            for z in range(0, D + 1):
                b.set(x, -1, z, "minecraft:dirt")
                b.set(x, 0, z, rnd.choice(sand if z > D - 22 else grass))
        # --- The gold mountain (the landmark, north-east): a rocky peak streaked with gold, with Woonan's hut on top.
        MX, MZ, MR, MH = 70, 24, 22, 32
        for y in range(1, MH + 1):
            r = MR * (1 - (y / (MH + 4)) ** 0.85)
            for x in range(int(MX - r) - 2, int(MX + r) + 3):
                for z in range(int(MZ - r) - 2, int(MZ + r) + 3):
                    d = math.hypot(x - MX, z - MZ) + rnd.random() * 1.6
                    if d <= r and 0 <= x <= W and 0 <= z <= D:
                        s = rnd.choice(ROCK)
                        if rnd.random() < 0.07 or (math.sin(x * 0.4 + y * 0.6) > 0.93):
                            s = rnd.choice(GOLDS)   # gold veins
                        b.set(x, y, z, s)
        TOP = MH
        b.disk(MX, TOP, MZ, 6.5, "minecraft:coarse_dirt")
        for y in range(TOP + 1, TOP + 6):   # clear the summit for the hut
            b.disk(MX, y, MZ, 7, AIR)
        # A path spiralling up the mountain, cut into the rock: it climbs one block every few steps round the peak.
        ang, y = math.radians(100), 1
        while y < TOP:
            r = MR * (1 - (y / (MH + 4)) ** 0.85) - 1.2
            for w in (-1, 0, 1):
                x = round(MX + (r + w * 0.9) * math.cos(ang)); z = round(MZ + (r + w * 0.9) * math.sin(ang))
                b.set(x, y - 1, z, "minecraft:cobblestone"); b.set(x, y, z, "minecraft:gravel" if w == 0 else "minecraft:cobblestone")
                for yy in range(y + 1, y + 4):
                    b.set(x, yy, z, AIR)
            if rnd.random() < 0.08:
                b.set(round(MX + (r + 1.8) * math.cos(ang)), y + 1, round(MZ + (r + 1.8) * math.sin(ang)), LANTERN)
            step = 1.1 / max(r, 3)
            ang += step
            if int((ang - step) / (step * 3)) != int(ang / (step * 3)):
                y += 1
        # Woonan's hut on the summit: an old hermit's shack of driftwood, with the chest he left behind.
        HX0, HZ0, HX1, HZ1 = MX - 4, MZ - 4, MX + 4, MZ + 3
        b.hall(HX0, HZ0, HX1, HZ1, TOP, 4, "minecraft:spruce_planks", "minecraft:mossy_cobblestone", log("spruce"), floor="minecraft:spruce_planks",
               win=pane(), every=4, doors=[("south", 4, 1, 2)], proud=False)
        b.gable_roof(HX0, HZ0, HX1, HZ1, TOP + 5, "spruce", "minecraft:spruce_planks", axis="x")
        b.chest(MX, TOP + 1, HZ0 + 1, "gold_island", "south")
        b.set(MX - 2, TOP + 1, HZ0 + 1, facing("writing_desk", "south")); b.set(MX + 2, TOP + 1, HZ0 + 1, BARREL)
        bed("brown", HX0 + 1, TOP + 1, HZ1 - 2, b, "north") if False else b.set(HX0 + 1, TOP + 1, HZ1 - 1, "minecraft:brown_wool")
        b.set(HX1 - 1, TOP + 1, HZ1 - 1, facing("book_stack", "north"))
        b.set(MX, TOP + 4, MZ, HANG)
        b.set(HX0 + 1, TOP + 1, HZ0 + 1, facing("treasure_pile", "south"))
        # a telescope and a weathered flag on the summit
        b.set(MX + 6, TOP + 1, MZ + 4, facing("telescope", "south")) if b.get(MX + 6, TOP, MZ + 4) else None
        b.flag(MX - 6, TOP + 1, MZ - 4, h=7, colors=("minecraft:white_wool", "minecraft:black_wool"), skull=True, length=4)
        # --- The dig: El Drago's crew strip-mining the mountain's foot for gold. Pits, scaffolds, rails and spoil heaps.
        for (px, pz, pr) in ((50, 32, 5), (84, 46, 4.5), (60, 46, 4)):
            for x in range(int(px - pr) - 1, int(px + pr) + 2):
                for z in range(int(pz - pr) - 1, int(pz + pr) + 2):
                    d = math.hypot(x - px, z - pz)
                    if d <= pr:
                        depth = 3 if d < pr - 1.5 else 1
                        for yy in range(0, 6):
                            b.set(x, yy, z, AIR) if yy > -depth else None
                        for yy in range(-depth, 1):
                            b.set(x, yy, z, AIR)
                        b.set(x, -depth - 1, z, rnd.choice(["minecraft:gravel", "minecraft:raw_gold_block", "minecraft:coarse_dirt", "minecraft:gold_ore"]))
            for i in range(4):   # scaffold poles and a ladder down
                a = math.radians(i * 90 + 45)
                sx, sz = round(px + (pr + 1) * math.cos(a)), round(pz + (pr + 1) * math.sin(a))
                b.box(sx, 1, sz, sx, 4, sz, fence("spruce"))
            b.box(round(px - pr - 1), 5, round(pz - pr - 1), round(px + pr + 1), 5, round(pz - pr - 1), "minecraft:spruce_slab[type=bottom,waterlogged=false]")
            b.hanging(px, 4, pz, 2)
        for (hx, hz) in ((44, 40), (90, 36), (66, 52)):   # spoil heaps of rock and gold
            b.sphere(hx, 0, hz, 2.5, "minecraft:gravel", upper=True, ry=2)
            b.set(hx, 3, hz, "minecraft:raw_gold_block")
        for x in range(44, 88):   # a mine-cart line along the mountain's foot
            z = 40 + round(3 * math.sin(x / 7))
            b.set(x, 0, z, "minecraft:gravel")
            b.set(x, 1, z, "minecraft:rail[shape=east_west,waterlogged=false]") if b.get(x, 1, z) in (None, AIR) and b.get(x, 1, z - 1) != b.get(x, 1, z + 1) or True else None
        for (x, z) in ((52, 41), (70, 43), (80, 39)):
            b.set(x, 1, z, "minecraft:chest_minecart" if False else facing("crate_stack", "north"))
        # --- Woonan's castle, blasted open by El Drago's voice (centre-west): the crew lives in its broken halls.
        CX0, CZ0, CX1, CZ1 = 6, 18, 42, 54
        wall = ["minecraft:stone_bricks"] * 4 + ["minecraft:cracked_stone_bricks", "minecraft:mossy_stone_bricks"]
        for x in range(CX0, CX1 + 1):
            for z in range(CZ0, CZ1 + 1):
                if x in (CX0, CX1) or z in (CZ0, CZ1):
                    for y in range(1, 11):
                        b.set(x, y, z, rnd.choice(wall))
                    if (x + z) % 2 == 0:
                        b.set(x, 11, z, rnd.choice(wall))
        for (tx, tz) in ((CX0, CZ0), (CX1, CZ0), (CX0, CZ1), (CX1, CZ1)):
            b.tower(tx, tz, 3, 15, "minecraft:stone_bricks", roof=None, floors=[7])
            b.set(tx, 16, tz, "minecraft:gold_block")
        # the round holes the Goe Goe blasts punched through the walls
        for (hx, hy, hz, r) in ((CX1, 5, 30, 3.2), (CX0, 6, 44, 2.6), (24, 6, CZ0, 3.0), (34, 4, CZ1, 2.5)):
            for x in range(int(hx - r) - 1, int(hx + r) + 2):
                for y in range(int(hy - r) - 1, int(hy + r) + 2):
                    for z in range(int(hz - r) - 1, int(hz + r) + 2):
                        if math.sqrt((x - hx) ** 2 + (y - hy) ** 2 + (z - hz) ** 2) <= r and y >= 1:
                            b.set(x, y, z, AIR)
        b.box(CX1, 1, 34, CX1, 4, 38, AIR)   # the gate
        b.box(CX1 + 1, 0, 34, CX1 + 8, 0, 38, "minecraft:cobblestone")
        # The keep's broken hall (north half of the castle), the crew's quarters
        b.hall(CX0 + 3, CZ0 + 3, CX1 - 3, CZ0 + 13, 0, 7, "minecraft:stone_bricks", "minecraft:mossy_cobblestone", "minecraft:polished_andesite",
               floor="minecraft:dark_oak_planks", win=pane(), every=5, doors=[("south", 8, 3, 3), ("south", 26, 3, 3)], proud=False)
        b.gable_roof(CX0 + 3, CZ0 + 3, CX1 - 3, CZ0 + 13, 8, "dark_oak", "minecraft:dark_oak_planks", axis="x")
        for x in range(CX0 + 10, CX0 + 18):   # the roof caved in where a blast came through
            for y in range(8, 15):
                for z in range(CZ0 + 3, CZ0 + 14):
                    if math.hypot(x - (CX0 + 14), z - (CZ0 + 8)) < 4.2:
                        b.set(x, y, z, AIR)
        for x in range(CX0 + 5, CX1 - 4, 3):
            bed("red", x, 1, CZ0 + 4, b, "south")
        b.table(CX0 + 22, 1, CZ0 + 9, "dark_oak", carpet("yellow"), w=8)
        for x in range(CX0 + 22, CX0 + 30, 2):
            b.chair(x, 1, CZ0 + 8, "dark_oak", "south"); b.chair(x, 1, CZ0 + 10, "dark_oak", "north")
        b.set(CX0 + 26, 2, CZ0 + 9, facing("treasure_pile", "north")); b.set(CX0 + 24, 2, CZ0 + 9, facing("beer_mugs", "north"))
        for x in (CX0 + 8, CX0 + 20, CX0 + 30):
            b.set(x, 6, CZ0 + 8, HANG)
        b.set(CX1 - 5, 1, CZ0 + 4, facing("weapon_rack", "south")); b.set(CX1 - 6, 1, CZ0 + 4, facing("powder_keg", "south"))
        # --- The courtyard (the arena): gold-paved where El Drago tore up the flagstones, a broken fountain in the middle.
        AX, AZ = 24, 40
        for x in range(CX0 + 1, CX1):
            for z in range(CZ0 + 15, CZ1):
                b.set(x, 0, z, rnd.choice(["minecraft:stone_bricks", "minecraft:cracked_stone_bricks", "minecraft:mossy_stone_bricks"]))
                if math.hypot(x - AX, z - AZ) < 9 and rnd.random() < 0.55:
                    b.set(x, 0, z, rnd.choice([GOLD_BRICK, "minecraft:raw_gold_block", "minecraft:gold_block" if rnd.random() < 0.1 else GOLD_BRICK]))
        b.cyl(AX, AZ, 3, 1, 1, "minecraft:stone_bricks", hollow=True)
        b.disk(AX, 0, AZ, 2, "minecraft:water[level=0]")
        b.set(AX, 1, AZ, AIR)
        b.set(AX + 3, 2, AZ, "minecraft:cracked_stone_bricks"); b.set(AX - 3, 2, AZ + 1, "minecraft:stone_brick_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]")
        for (x, z) in ((CX0 + 3, CZ1 - 3), (CX1 - 3, CZ1 - 3), (CX0 + 3, CZ0 + 17), (CX1 - 3, CZ0 + 17)):
            b.lamp_post(x, 1, z, "dark_oak", 3, LANTERN)
        b.scatter(CX0 + 2, CZ0 + 15, CX1 - 2, CZ1 - 2, 1, ["minecraft:cobblestone_slab[type=bottom,waterlogged=false]", "minecraft:stone_button[face=floor,facing=north,powered=false]",
                  "minecraft:gold_nugget" if False else "minecraft:cobblestone_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]"], 0.03, rnd)
        b.set(AX, 1, AZ, AIR)
        # --- El Drago's golden ship, run up on the beach (south-east), with its lion figurehead.
        sx, sz, L, SW = 52, D - 18, 34, 13
        deck = b.ship(sx, -3, sz, L, SW, hull="minecraft:yellow_terracotta", deck="minecraft:spruce_planks", masts=((10, 14), (20, 16)),
                      sail="minecraft:yellow_wool", flag=("minecraft:black_wool", "minecraft:yellow_wool"), cabin=(7, 4, "minecraft:dark_oak_planks"))
        b.mast_yard(sx, deck, sz, SW, ((10, 14), (20, 16)))
        cz = sz + SW // 2
        for x in range(sx + 2, sx + L - 4, 3):   # gold plating along the hull
            for z in (sz + 1, sz + SW - 2):
                for y in range(-1, deck):
                    if b.get(x, y, z) == "minecraft:yellow_terracotta":
                        b.set(x, y, z, GOLD_BRICK)
        # lion figurehead at the bow (+x)
        fx = sx + L
        b.box(fx, deck - 2, cz - 1, fx + 2, deck + 1, cz + 1, "minecraft:honeycomb_block")
        b.box(fx - 1, deck - 1, cz - 2, fx - 1, deck + 2, cz + 2, "minecraft:orange_terracotta")   # the mane
        b.set(fx + 2, deck, cz - 1, "minecraft:black_concrete"); b.set(fx + 2, deck, cz + 1, "minecraft:black_concrete")
        b.set(fx + 3, deck - 1, cz, "minecraft:honeycomb_block")
        for x in range(sx + 12, sx + 28, 4):
            b.set(x, deck + 1, sz + 2, facing("cannon", "north")); b.set(x, deck + 1, sz + SW - 3, facing("cannon", "south"))
        b.support(sx, sz, sx + L + 4, sz + SW, -3, ["minecraft:sand"], rnd, down_to=-6)
        # --- Palms, rocks and the path up from the beach.
        for (x, z) in ((4, 70), (12, 78), (26, 84), (40, 74), (90, 68), (92, 82), (6, 6), (24, 8), (46, 4), (94, 6)):
            if b.get(x, 1, z) in (None, AIR):
                b.palm(x, 1, z, rnd.randint(5, 8))
        for z in range(CZ1 + 1, D - 18):
            for x in range(AX + 18 - 2, AX + 18 + 3):
                b.set(x, 0, z, "minecraft:gravel" if abs(x - AX - 18) < 2 else "minecraft:cobblestone")
        b.scatter(0, 0, W, D, 1, ["minecraft:short_grass", "minecraft:fern", "minecraft:dead_bush"], 0.06, rnd, only_on=grass + sand)

        b.rogue(AX, 1, AZ - 6, "el_drago")
        b.crew("el_drago_pirate", ((AX - 8, AZ - 4), (AX + 8, AZ - 4), (AX - 7, AZ + 8), (AX + 7, AZ + 8), (CX0 + 14, CZ0 + 6), (48, 38), (sx + 16, deck + 1, cz)))
        clear_spawns(b)

    # ============================================================ Gasparde: the Salamander
    @lair("salamander", "The Salamander", "gasparde", OCEANS, "sea", group="film_lairs")
    def _(b):
        rnd = random.Random(22)
        L, W = 98, 36               # x 0..97 (bow at +x), z 0..35
        CZ = W // 2
        KEEL, DECK = -10, 0
        HULL = ["minecraft:black_concrete"] * 3 + ["minecraft:gray_concrete"]
        HULL_HI = ["minecraft:green_terracotta", "minecraft:green_terracotta", "minecraft:waxed_oxidized_copper"]
        RIVET = "minecraft:iron_block"

        def half(x, y):
            f = x / (L - 1)
            t = (y - KEEL) / (DECK - KEEL)
            taper = 1.0 - max(0.0, (f - 0.7) / 0.3) ** 1.5 * 0.93 - max(0.0, (0.06 - f) / 0.06) * 0.3
            return max(0, round((W / 2 - 1) * (0.55 + 0.45 * t) * taper))

        # --- The ironclad hull: a shell (the lounge is inside), green above the waterline, rivet bands, portholes.
        for x in range(L):
            for y in range(KEEL, DECK + 1):
                h = half(x, y)
                for z in range(CZ - h, CZ + h + 1):
                    k = abs(z - CZ)
                    edge = (y == KEEL or k >= h or x in (0, L - 1) or k > half(x, y - 1)
                            or k > half(min(x + 1, L - 1), y) or k > half(max(x - 1, 0), y))
                    if y == DECK:
                        b.set(x, y, z, "minecraft:dark_oak_planks" if k < h else RIVET)
                    elif edge:
                        s = rnd.choice(HULL_HI) if y >= -3 else rnd.choice(HULL)
                        if y == -2:
                            s = RIVET
                        b.set(x, y, z, s)
                    else:
                        b.set(x, y, z, AIR)
            h = half(x, DECK)
            for z in (CZ - h, CZ + h):
                b.set(x, 1, z, RIVET if x % 5 == 0 else BARS_X)
            if x % 5 == 2 and 6 < x < L - 10:
                for z in (CZ - half(x, -5), CZ + half(x, -5)):
                    b.set(x, -5, z, "minecraft:glass")
        b.waterline = -4
        # deck planking runs fore and aft, a black line along each side
        for x in range(3, L - 6):
            for z in (CZ - 10, CZ + 10):
                if b.get(x, 0, z) == "minecraft:dark_oak_planks":
                    b.set(x, 0, z, "minecraft:spruce_planks")
        # --- The paddle wheels, one each side amidships (the Salamander is a steam racer).
        PX = 62
        for side in (-1, 1):
            zw = CZ + side * (half(PX, 0) + 2)
            for a in range(0, 360, 6):
                for r in (6, 7):
                    x = round(PX + r * math.cos(math.radians(a))); y = round(-2 + r * math.sin(math.radians(a)))
                    b.set(x, y, zw, "minecraft:dark_oak_planks" if r == 7 else RIVET)
            for a in range(0, 360, 30):   # paddles
                for r in range(1, 8):
                    x = round(PX + r * math.cos(math.radians(a))); y = round(-2 + r * math.sin(math.radians(a)))
                    b.set(x, y, zw, "minecraft:spruce_planks")
            b.set(PX, -2, zw, RIVET)
            for x in range(PX - 8, PX + 9):   # the wheel box over it
                for y in range(-1, 7):
                    if abs(x - PX) == 8 or y == 6:
                        b.set(x, y, zw + side, "minecraft:green_terracotta")
                b.set(x, 6, zw, "minecraft:green_terracotta")
            b.box(PX - 1, -2, zw - side if side > 0 else zw + 1, PX + 1, -2, zw - side if side > 0 else zw + 1, RIVET)
        # --- Three funnels (the landmark), striped with the race's colours and smoking.
        for (fx, fh) in ((58, 26), (66, 30), (74, 26)):
            b.cyl(fx, CZ, 2.2, 1, fh, "minecraft:black_concrete", hollow=True)
            for y in range(fh - 6, fh - 3):
                b.cyl(fx, CZ, 2.2, y, y, "minecraft:red_concrete", hollow=True)
            b.cyl(fx, CZ, 2.6, fh + 1, fh + 1, RIVET, hollow=True)
            b.set(fx, fh - 1, CZ, SMOKE)
            b.box(fx - 1, fh - 2, CZ - 1, fx + 1, fh - 2, CZ + 1, "minecraft:polished_blackstone")
            b.set(fx, fh - 1, CZ, SMOKE)
        # --- The racing deck (the arena, foredeck): open planks in a ring of rails, the Dead End's chequered finish line.
        AX, AZ = 40, CZ
        for x in range(AX - 9, AX + 10):
            for z in range(AZ - 9, AZ + 10):
                if b.get(x, 0, z) in ("minecraft:dark_oak_planks", "minecraft:spruce_planks"):
                    if abs(x - AX) <= 1:
                        b.set(x, 0, z, "minecraft:white_concrete" if (x + z) % 2 else "minecraft:black_concrete")
        for (cx2, cz2) in ((AX - 8, AZ - 9), (AX + 6, AZ - 8), (AX - 8, AZ + 9), (AX + 6, AZ + 8)):
            if b.get(cx2, 0, cz2) is not None:
                b.set(cx2, 1, cz2, facing("cannon", "north" if cz2 < AZ else "south")); b.set(cx2 + 1, 1, cz2, facing("cannonball_pile", "north"))
        b.set(L - 3, 1, CZ, facing("capstan", "west")); b.set(L - 6, 1, CZ - 2, facing("anchor", "north")); b.set(L - 6, 1, CZ + 2, facing("rope_coil", "north"))
        # foremast with the Dead End flag
        MAST = 88
        b.box(MAST, 1, CZ, MAST, 22, CZ, log("spruce"))
        b.box(MAST, 18, CZ + 1, MAST, 21, CZ + 6, "minecraft:white_wool")
        for z in range(CZ + 1, CZ + 7):
            for y in range(18, 22):
                if (y + z) % 2 == 0:
                    b.set(MAST, y, z, "minecraft:black_wool")
        b.set(MAST, 14, CZ, log("spruce", "z")); b.set(MAST, 14, CZ - 1, log("spruce", "z")); b.set(MAST, 14, CZ + 1, log("spruce", "z"))
        # --- The bridge and Gasparde's cabin (stern, two decks): the chest is in his cabin.
        SX0, SX1, SZ0, SZ1 = 6, 28, CZ - 9, CZ + 9
        b.hall(SX0, SZ0, SX1, SZ1, 0, 6, "minecraft:green_terracotta", RIVET, "minecraft:polished_deepslate", trim="minecraft:gold_block" if False else GOLD_BRICK,
               floor="minecraft:dark_oak_planks", win=pane("black"), every=4, doors=[("east", 8, 3, 3)], proud=False)
        b.hall(SX0 + 4, SZ0 + 3, SX1 - 4, SZ1 - 3, 6, 5, "minecraft:green_terracotta", RIVET, "minecraft:polished_deepslate", trim=GOLD_BRICK,
               floor="minecraft:dark_oak_planks", win=pane(), every=3, win_h=2, doors=[("east", 5, 2, 3)], proud=False)
        b.box(SX0 + 4, 11, SZ0 + 3, SX1 - 4, 11, SZ1 - 3, RIVET)
        b.walls(SX0, 7, SZ0, SX1, 7, SZ1, BARS_X)
        b.set(SX1 - 5, 7, CZ, facing("ships_wheel", "east")); b.set(SX1 - 6, 7, CZ - 3, facing("chart_table", "east")); b.set(SX1 - 6, 7, CZ + 3, facing("telescope", "east"))
        for i in range(6):   # stair up to the bridge deck, outside on the north side
            b.set(SX1 + 1 + 0, 1 + i, SZ0 + 1 + i, stair("dark_oak", "south")) if False else None
        for i in range(6):
            b.set(SX1 + 1, 1 + i, SZ1 - 7 + i, stair("dark_oak", "south"))
            for yy in range(1, 1 + i):
                b.set(SX1 + 1, yy, SZ1 - 7 + i, RIVET)
        b.box(SX1 + 1, 7, SZ1 - 1, SX1 + 1, 7, SZ1, "minecraft:dark_oak_planks")
        # his cabin, ground deck: desk, map of the race, the safe, his coat on a stand
        b.chest(SX0 + 2, 1, CZ, "salamander", "east")
        b.set(SX0 + 4, 1, CZ, facing("captains_chair", "east")) if False else b.set(SX0 + 6, 1, CZ, facing("navigators_desk", "west"))
        b.set(SX0 + 5, 1, CZ, facing("captains_chair", "east"))
        b.set(SX0 + 1, 2, CZ - 3, facing("wall_wanted_poster", "east")) if False else None
        b.shelf(SX0 + 1, 1, SZ0 + 1, h=3, n=1); b.shelf(SX0 + 1, 1, SZ1 - 1, h=3, n=1)
        b.set(SX0 + 3, 1, SZ0 + 1, facing("wine_rack", "south")); b.set(SX0 + 3, 1, SZ1 - 1, facing("globe", "north"))
        b.set(SX0 + 2, 1, SZ0 + 3, "minecraft:armor_stand" if False else "minecraft:honey_block")   # a jar of his syrup, hardened
        for z in range(SZ0 + 2, SZ1 - 1):
            b.set(SX0 + 9, 1, z, carpet("purple"))
        b.set(SX0 + 7, 5, CZ, facing("iron_chandelier", "north"))
        # the crew's mess, the rest of the ground deck
        for x in range(SX0 + 12, SX1 - 1, 4):
            b.table(x, 1, CZ - 5, "dark_oak", carpet("green"), w=3, axis="z"); b.table(x, 1, CZ + 3, "dark_oak", carpet("green"), w=3, axis="z")
        b.set(SX1 - 2, 5, CZ - 5, HANG); b.set(SX1 - 2, 5, CZ + 5, HANG)
        # --- The betting lounge, down in the hull under the funnels (the crew's quarters and the Dead End's bookmakers).
        LX0, LX1 = 34, 72
        for x in range(LX0, LX1 + 1):
            h = half(x, -7) - 1
            for z in range(CZ - h, CZ + h + 1):
                b.set(x, -8, z, "minecraft:red_concrete" if (x + z) % 2 else "minecraft:black_concrete")
                for y in range(-7, 0):
                    if abs(z - CZ) < half(x, y):
                        b.set(x, y, z, AIR)
        for x in range(LX0 + 2, LX1 - 1, 6):   # card tables
            for zc in (CZ - 6, CZ + 6):
                b.set(x, -7, zc, facing("red_tablecloth_table", "north")) if False else b.table(x, -7, zc, "dark_oak", carpet("green"), w=2)
                b.set(x - 1, -7, zc, facing("bar_stool", "east")); b.set(x + 2, -7, zc, facing("bar_stool", "west"))
        for z in range(CZ - 4, CZ + 5):   # the bar at the aft end, the odds board above it
            b.set(LX0 + 1, -7, z, "minecraft:polished_blackstone_bricks"); b.set(LX0 + 1, -6, z, slab("dark_oak"))
            b.set(LX0, -5, z, "minecraft:black_concrete" if z % 2 else "minecraft:white_concrete")
        b.set(LX0 + 1, -6, CZ, facing("beer_mugs", "east"))
        for x in range(LX0 + 4, LX1 - 2, 5):
            b.set(x, -1, CZ, HANG)
            bed("green", x, -7, CZ + half(x, -7) - 2, b, "north") if x % 2 else None
        for i in range(8):   # the hatch and stair down from the deck
            b.set(LX1 - 2 - i, -i, CZ + 3, stair("dark_oak", "east"))
            b.set(LX1 - 2 - i, -i, CZ + 4, stair("dark_oak", "east"))
            b.box(LX1 - 2 - i, 1 - i, CZ + 3, LX1 - 2 - i, 3 - i, CZ + 4, AIR)
        b.box(LX1 - 10, -8, CZ + 3, LX1 - 9, -8, CZ + 4, "minecraft:dark_oak_planks")
        # --- The finish-line buoy tower (off the bow, in the sea): a rock with a lighthouse that reads the race's end.
        RX, RZ = L + 8, CZ - 12
        b.skirt(RX, RZ, 4, -14, 0, ["minecraft:stone", "minecraft:andesite", "minecraft:cobblestone"], rnd)
        b.tower(RX, RZ, 3, 16, "minecraft:white_concrete", roof="minecraft:red_concrete", y=1, floors=[8])
        b.set(RX, 16, RZ, "minecraft:sea_lantern")
        for y in range(4, 16, 4):
            b.cyl(RX, RZ, 3, y, y, "minecraft:red_concrete", hollow=True)
        b.box(L - 1, 0, RZ, RX - 3, 0, RZ, "minecraft:spruce_planks")   # a gangway to it
        b.box(L - 1, 1, RZ - 1, RX - 3, 1, RZ - 1, fence("spruce")); b.box(L - 1, 1, RZ + 1, RX - 3, 1, RZ + 1, fence("spruce"))
        for x in range(L - 1, RX - 2):
            b.set(x, -1, RZ, "minecraft:spruce_planks")
            b.box(x, -14, RZ, x, -2, RZ, log("spruce")) if x % 4 == 0 else None
        # Clear the air over the deck, so nothing the sea already had there pokes through it.
        for x in range(L):
            h = half(x, DECK)
            for z in range(CZ - h + 1, CZ + h):
                for y in range(1, 6):
                    if b.get(x, y, z) is None:
                        b.set(x, y, z, AIR)

        b.rogue(AX, 1, AZ, "gasparde")
        b.crew("gasparde_pirate", ((AX - 6, AZ - 5), (AX - 6, AZ + 5), (AX + 4, AZ - 6), (AX + 4, AZ + 6), (SX0 + 14, CZ), (LX0 + 10, -7, CZ), (LX0 + 22, -7, CZ)))
        clear_spawns(b)

    # ============================================================ Baron Omatsuri: Omatsuri Island
    @lair("omatsuri_island", "Omatsuri Island", "baron_omatsuri",
          ["minecraft:beach", "minecraft:sparse_jungle", "minecraft:bamboo_jungle", "minecraft:savanna", "minecraft:cherry_grove"], "land", group="film_lairs")
    def _(b):
        rnd = random.Random(23)
        W, D = 96, 96
        grass = ["minecraft:grass_block"] * 5 + ["minecraft:moss_block"]
        for x in range(0, W + 1):
            for z in range(0, D + 1):
                b.set(x, -1, z, "minecraft:dirt"); b.set(x, 0, z, rnd.choice(grass))
        RED, WHITE = "minecraft:red_concrete", "minecraft:white_concrete"
        CX = 48
        # --- The Trials of Hell ring (the arena, centre-south): a raised square ring with red and white posts and ropes,
        # festival lanterns strung over it, and a judge's tower.
        AX, AZ, R = CX, 62, 11
        b.box(AX - R, 0, AZ - R, AX + R, 1, AZ + R, "minecraft:spruce_planks")
        for x in range(AX - R, AX + R + 1):
            for z in range(AZ - R, AZ + R + 1):
                if (x + z) % 2 == 0 and abs(x - AX) < R and abs(z - AZ) < R:
                    b.set(x, 1, z, "minecraft:stripped_spruce_wood[axis=x]")
        b.box(AX - R, 1, AZ - R, AX + R, 1, AZ - R, RED); b.box(AX - R, 1, AZ + R, AX + R, 1, AZ + R, RED)
        b.box(AX - R, 1, AZ - R, AX - R, 1, AZ + R, WHITE); b.box(AX + R, 1, AZ - R, AX + R, 1, AZ + R, WHITE)
        for (px, pz) in ((AX - R, AZ - R), (AX + R, AZ - R), (AX - R, AZ + R), (AX + R, AZ + R)):
            b.box(px, 2, pz, px, 5, pz, RED if (px + pz) % 4 else WHITE)
            b.set(px, 6, pz, PAPER_LANTERN)
        for y in (3, 4):   # the ropes
            for x in range(AX - R + 1, AX + R):
                b.set(x, y, AZ - R, fence("crimson") if y == 3 else fence("birch")); b.set(x, y, AZ + R, fence("crimson") if y == 3 else fence("birch"))
            for z in range(AZ - R + 1, AZ + R):
                b.set(AX - R, y, z, fence("crimson") if y == 3 else fence("birch")); b.set(AX + R, y, z, fence("crimson") if y == 3 else fence("birch"))
        b.box(AX - 1, 3, AZ + R, AX + 1, 4, AZ + R, AIR)   # the way in
        for i in range(2):
            b.box(AX - 1, 1 - i, AZ + R + 1 + i, AX + 1, 1 - i, AZ + R + 1 + i, stair("spruce", "north"))
        b.disk(AX, 1, AZ, 2.5, "minecraft:red_wool")
        b.set(AX, 1, AZ, "minecraft:gold_block")
        # lantern strings across the ring from four tall poles
        poles = [(AX - R - 3, AZ - R - 3), (AX + R + 3, AZ - R - 3), (AX - R - 3, AZ + R + 3), (AX + R + 3, AZ + R + 3)]
        for (px, pz) in poles:
            b.box(px, 1, pz, px, 12, pz, log("dark_oak"))
            b.set(px, 13, pz, PAPER_LANTERN)
        for (p0, p1) in ((poles[0], poles[3]), (poles[1], poles[2])):
            n = abs(p1[0] - p0[0])
            for i in range(1, n):
                x = p0[0] + (i if p1[0] > p0[0] else -i)
                z = p0[1] + round((p1[1] - p0[1]) * i / n)
                y = 12 - round(3 * math.sin(math.pi * i / n))
                b.set(x, y, z, CHAIN_X if True else CHAIN)
                if i % 3 == 0:
                    b.set(x, y - 1, z, PAPER_HANG)
        # the judge's tower beside the ring, where Omatsuri watches
        JX, JZ = AX + R + 7, AZ - 2
        b.box(JX - 2, 1, JZ - 2, JX + 2, 7, JZ + 2, "minecraft:dark_oak_planks")
        b.box(JX - 1, 1, JZ - 1, JX + 1, 6, JZ + 1, AIR)
        b.box(JX - 3, 8, JZ - 3, JX + 3, 8, JZ + 3, "minecraft:spruce_planks")
        b.walls(JX - 3, 9, JZ - 3, JX + 3, 9, JZ + 3, fence("dark_oak"))
        b.hip_roof(JX - 3, JZ - 3, JX + 3, JZ + 3, 12, "deepslate_tile", "minecraft:deepslate_tiles", ov=1)
        for (x, z) in ((JX - 3, JZ - 3), (JX + 3, JZ - 3), (JX - 3, JZ + 3), (JX + 3, JZ + 3)):
            b.box(x, 9, z, x, 11, z, log("dark_oak"))
        for y in range(1, 9):
            b.set(JX, y, JZ - 1, ladder("south")) if False else b.set(JX, y, JZ + 1, ladder("north"))
        b.box(JX, 1, JZ + 2, JX, 2, JZ + 2, AIR)
        b.set(JX, 9, JZ - 2, facing("captains_chair", "west")) if False else b.set(JX - 1, 9, JZ, "minecraft:bell[attachment=floor,facing=west,powered=false]")
        # --- The festival street (east and west of the ring): stalls, games and lantern posts.
        stall_cols = ["red", "white", "orange", "pink", "red", "yellow"]
        for k, sx in enumerate(range(8, 34, 6)):
            b.stall(sx, 0, 76, stall_cols[k % len(stall_cols)]); b.stall(sx, 0, 86, stall_cols[(k + 2) % len(stall_cols)])
            b.set(sx + 1, 4, 76 + 1, PAPER_LANTERN); b.set(sx + 1, 4, 86 + 1, PAPER_LANTERN)
        for k, sx in enumerate(range(64, 90, 6)):
            b.stall(sx, 0, 76, stall_cols[(k + 1) % len(stall_cols)]); b.stall(sx, 0, 86, stall_cols[(k + 3) % len(stall_cols)])
            b.set(sx + 1, 4, 77, PAPER_LANTERN); b.set(sx + 1, 4, 87, PAPER_LANTERN)
        for x in range(4, W - 3):   # the street between the stalls
            for z in range(80, 85):
                b.set(x, 0, z, "minecraft:gravel" if z in (80, 84) else "minecraft:packed_mud")
        # goldfish scooping: a wide shallow tub with orange "goldfish"
        b.box(8, 0, 66, 20, 1, 72, "minecraft:spruce_planks")
        b.box(9, 1, 67, 19, 1, 71, WATER)
        b.box(9, 0, 67, 19, 0, 71, "minecraft:light_blue_concrete")
        for (x, z) in ((10, 68), (13, 70), (16, 68), (18, 70), (12, 69)):
            b.set(x, 0, z, "minecraft:orange_concrete")
        # ring toss: posts on a board
        for x in range(76, 90, 3):
            for z in range(64, 72, 3):
                b.set(x, 1, z, fence("birch")); b.set(x, 2, z, "minecraft:white_carpet" if False else fence("birch"))
            b.set(x, 1, 63, "minecraft:red_carpet")
        # the shooting gallery: targets on a wall, a counter to shoot from
        b.box(64, 1, 66, 72, 4, 66, "minecraft:dark_oak_planks")
        for x in range(65, 72, 2):
            b.set(x, 3, 67, "minecraft:target[power=0]")
        b.box(64, 1, 71, 72, 1, 71, "minecraft:spruce_planks"); b.box(64, 2, 71, 72, 2, 71, slab("spruce"))
        # --- The guest hotel (west): two floors, wide eaves, where the pirates who came for the trials stay.
        HX0, HZ0, HX1, HZ1 = 4, 22, 30, 44
        b.hall(HX0, HZ0, HX1, HZ1, 0, 5, "minecraft:white_terracotta", "minecraft:stone_bricks", log("dark_oak"), trim="minecraft:red_terracotta",
               floor="minecraft:spruce_planks", win=pane(), every=4, doors=[("east", 9, 3, 3)])
        b.hall(HX0 + 2, HZ0 + 2, HX1 - 2, HZ1 - 2, 5, 5, "minecraft:white_terracotta", "minecraft:white_terracotta", log("dark_oak"), trim="minecraft:red_terracotta",
               floor="minecraft:spruce_planks", win=pane(), every=4, proud=False)
        b.pagoda_roof(HX0 + 2, HZ0 + 2, HX1 - 2, HZ1 - 2, 11, "deepslate_tile", "minecraft:deepslate_tiles", ov=2)
        b.box(HX0 - 1, 6, HZ0 - 1, HX1 + 1, 6, HZ1 + 1, slab("deepslate_tile"))
        b.box(HX0 + 2, 6, HZ0 + 2, HX1 - 2, 6, HZ1 - 2, "minecraft:spruce_planks")
        for y in range(1, 7):
            b.set(HX0 + 1, y, HZ0 + 3, ladder("east"))
        b.set(HX0 + 1, 6, HZ0 + 3, ladder("east")); b.set(HX0 + 3, 6, HZ0 + 3, AIR); b.set(HX0 + 2, 6, HZ0 + 3, AIR)
        for z in range(HZ0 + 2, HZ1 - 1, 3):
            bed("red", HX0 + 2, 1, z, b, "east") if False else bed("white", HX0 + 3, 7, z, b, "south") if z < HZ1 - 3 else None
        for x in range(HX0 + 6, HX1 - 2, 5):
            b.table(x, 1, HZ0 + 6, "spruce", carpet("red"), w=1)
            b.set(x - 1, 1, HZ0 + 6, facing("red_floor_cushion", "east")); b.set(x + 1, 1, HZ0 + 6, facing("red_floor_cushion", "west"))
            b.table(x, 1, HZ1 - 6, "spruce", carpet("red"), w=1)
            b.set(x, 2, HZ0 + 6, facing("sake_set", "north")); b.set(x, 2, HZ1 - 6, facing("tea_set", "north"))
        for z in range(HZ0 + 3, HZ1 - 2, 6):
            b.set(HX1 - 1, 1, z, "onepiece:sake_barrel[axis=y]")
        for (lx, lz) in ((HX0 + 8, HZ0 + 10), (HX1 - 8, HZ1 - 10)):
            b.set(lx, 4, lz, PAPER_HANG); b.set(lx, 10, lz, PAPER_HANG)
        # --- Lily Carnation (the landmark, north): the flower grown huge on its hill, roots writhing out of the ground.
        LX, LZ = CX + 8, 18
        for y in range(1, 9):   # the hill
            b.disk(LX, y, LZ, 15 - y * 1.4, rnd.choice(["minecraft:grass_block", "minecraft:moss_block"]) if y == 8 else "minecraft:dirt")
        for y in range(1, 9):
            r = 15 - y * 1.4
            for a in range(0, 360, 4):
                x, z = round(LX + r * math.cos(math.radians(a))), round(LZ + r * math.sin(math.radians(a)))
                if b.get(x, y + 1, z) in (None, AIR):
                    b.set(x, y, z, "minecraft:grass_block")
        HT = 9
        for y in range(HT, HT + 22):   # the stem
            r = 2.2 - (y - HT) * 0.04
            b.cyl(LX + round(1.5 * math.sin((y - HT) / 6)), LZ, r, y, y, "minecraft:green_concrete")
        top = HT + 22
        fx = LX + round(1.5 * math.sin(22 / 6))
        for (lx, ly, lz2, rr) in ((fx - 5, HT + 10, LZ, 3.2), (fx + 5, HT + 14, LZ, 3.0)):   # two leaves
            for x in range(int(lx - rr) - 1, int(lx + rr) + 2):
                for z in range(int(lz2 - rr / 2) - 1, int(lz2 + rr / 2) + 2):
                    if math.hypot((x - lx) / rr, (z - lz2) / (rr / 2)) <= 1:
                        b.set(x, ly + round(abs(x - lx) * 0.3), z, "minecraft:lime_concrete")
            b.box(min(lx, fx), ly, LZ, max(lx, fx), ly, LZ, "minecraft:green_concrete")
        # the face: a yellow disc facing south, two eyes and a smile, then five petals round it with red joints
        for x in range(fx - 4, fx + 5):
            for y in range(top - 4, top + 5):
                if math.hypot(x - fx, y - top) <= 4.3:
                    b.set(x, y, LZ, "minecraft:yellow_concrete")
                    b.set(x, y, LZ - 1, "minecraft:yellow_concrete") if math.hypot(x - fx, y - top) <= 3.2 else None
        b.set(fx - 2, top + 1, LZ + 1, "minecraft:black_concrete"); b.set(fx + 2, top + 1, LZ + 1, "minecraft:black_concrete")
        for x in range(fx - 2, fx + 3):
            b.set(x, top - 2 + (1 if abs(x - fx) == 2 else 0), LZ + 1, "minecraft:red_concrete")
        for i in range(5):
            a = math.radians(90 + i * 72)
            for t in range(4, 11):
                w = 3.4 * math.sin(math.pi * (t - 4) / 7) + 0.6
                for s in range(-int(w), int(w) + 1):
                    x = round(fx + t * math.cos(a) - s * math.sin(a))
                    y = round(top + t * math.sin(a) + s * math.cos(a))
                    b.set(x, y, LZ, "minecraft:red_concrete" if t == 4 else "minecraft:yellow_concrete")
                    if t in (7, 8) and s in (-1, 1):
                        b.set(x, y, LZ + 1, "minecraft:red_concrete")   # the red dots on each petal
        # the roots: tentacles writhing out of the hill and down across the garden
        for i in range(9):
            a = math.radians(i * 40 + rnd.randint(-10, 10))
            for t in range(0, 26):
                r = 3 + t
                x, z = round(LX + r * math.cos(a + 0.25 * math.sin(t / 3))), round(LZ + r * math.sin(a + 0.25 * math.sin(t / 3)))
                if not (0 <= x <= W and 0 <= z <= D):
                    break
                yy = HT
                while yy > 0 and b.get(x, yy, z) in (None, AIR):
                    yy -= 1
                b.set(x, yy + 1, z, "minecraft:mangrove_roots[waterlogged=false]" if t % 3 else "minecraft:muddy_mangrove_roots[axis=y]")
                if t % 7 == 3 and t < 20:
                    b.set(x, yy + 2, z, "minecraft:mangrove_roots[waterlogged=false]")
        # Omatsuri's shrine at the flower's foot (his quarters, where the chest is): a little hall under a sweeping roof
        QX0, QZ0, QX1, QZ1 = LX - 6, LZ + 10, LX + 6, LZ + 18
        for x in range(QX0 - 1, QX1 + 2):
            for z in range(QZ0 - 1, QZ1 + 2):
                for y in range(1, 12):
                    b.set(x, y, z, AIR)
                b.set(x, 0, z, "minecraft:stone_bricks")
        b.hall(QX0, QZ0, QX1, QZ1, 0, 5, "minecraft:red_terracotta", "minecraft:stone_bricks", log("dark_oak"), trim=GOLD_BRICK,
               floor="minecraft:dark_oak_planks", win=pane("orange"), every=3, doors=[("south", 5, 3, 3)], proud=False)
        b.pagoda_roof(QX0, QZ0, QX1, QZ1, 6, "deepslate_tile", "minecraft:deepslate_tiles", ov=2)
        b.chest(LX, 1, QZ0 + 1, "omatsuri_island", "south")
        b.set(LX - 2, 1, QZ0 + 1, facing("candelabra", "south")) if False else b.set(LX - 2, 1, QZ0 + 1, candle(3, "red"))
        b.set(LX + 2, 1, QZ0 + 1, candle(3, "yellow"))
        b.set(LX, 1, QZ0 + 3, facing("throne", "north")) if False else b.set(LX, 1, QZ0 + 4, facing("purple_floor_cushion", "north"))
        for x in (QX0 + 1, QX1 - 1):
            b.set(x, 1, QZ0 + 1, "minecraft:potted_poppy"); b.set(x, 1, QZ1 - 1, facing("katana_stand", "north")) if False else b.set(x, 1, QZ1 - 1, BARREL)
        b.set(QX0 + 2, 1, QZ0 + 1, "minecraft:target[power=0]"); b.set(QX1 - 2, 1, QZ0 + 1, facing("weapon_rack", "south"))
        b.set(LX, 4, (QZ0 + QZ1) // 2, PAPER_HANG)
        b.set(LX - 1, 1, QZ0 + 2, carpet("purple")); b.set(LX, 1, QZ0 + 2, carpet("purple")); b.set(LX + 1, 1, QZ0 + 2, carpet("purple"))
        # the Red Arrows' graves: Lily raised them, and their headstones stand empty along the garden path
        for i, gx in enumerate(range(LX - 18, LX - 6, 3)):
            for gz in (LZ + 8, LZ + 12):
                b.set(gx, 1, gz, "minecraft:mossy_stone_brick_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]")
                b.set(gx, 2, gz, slab("mossy_stone_brick"))
                b.set(gx, 1, gz + 1, "minecraft:poppy") if i % 2 else None
        # a torii-like red gate where the path from the ring meets the hill
        GZ = LZ + 24
        for gx in (CX - 1, CX + 5):
            b.box(gx, 1, GZ, gx, 8, GZ, RED)
        b.box(CX - 3, 9, GZ, CX + 7, 9, GZ, "minecraft:black_concrete"); b.box(CX - 1, 7, GZ, CX + 5, 7, GZ, RED)
        for z in range(GZ - 4, AZ - R - 1):
            for x in range(CX + 1, CX + 4):
                b.set(x, 0, z, "minecraft:gravel" if x == CX + 2 else "minecraft:stone_bricks")
        for z in range(GZ - 4, GZ + 2, 3):
            b.stone_lantern(CX - 1, 1, z, "stone_brick", PAPER_LANTERN) if z != GZ else None
        # --- The beach and the pier where guests land (south), palms and flowers everywhere.
        for x in range(0, W + 1):
            for z in range(D - 6, D + 1):
                b.set(x, 0, z, "minecraft:sand")
        b.box(CX - 1, 0, D - 6, CX + 1, 0, D + 6, "minecraft:spruce_planks")
        for z in range(D - 6, D + 7, 3):
            b.set(CX - 2, 1, z, fence("spruce")); b.set(CX + 2, 1, z, fence("spruce"))
            b.box(CX - 2, -6, z, CX - 2, -1, z, log("spruce")); b.box(CX + 2, -6, z, CX + 2, -1, z, log("spruce"))
        b.set(CX - 2, 2, D + 6, PAPER_LANTERN); b.set(CX + 2, 2, D + 6, PAPER_LANTERN)
        for z in range(AZ + R + 2, D - 6):
            for x in range(CX - 1, CX + 2):
                b.set(x, 0, z, "minecraft:gravel")
        for (x, z) in ((4, 92), (20, 94), (74, 93), (92, 90), (90, 54), (94, 30), (40, 6), (4, 6), (90, 6), (36, 30), (66, 44), (6, 56)):
            if b.get(x, 1, z) in (None, AIR):
                b.palm(x, 1, z, rnd.randint(5, 8))
        b.scatter(0, 0, W, D, 1, ["minecraft:poppy", "minecraft:dandelion", "minecraft:short_grass", "minecraft:short_grass", "minecraft:red_tulip"], 0.07, rnd, only_on=grass)

        b.rogue(AX, 2, AZ - 3, "baron_omatsuri")
        b.crew("red_arrows_pirate", ((AX - 6, 2, AZ - 6), (AX + 6, 2, AZ - 6), (AX - 6, 2, AZ + 6), (AX + 6, 2, AZ + 6), (JX, 9, JZ + 2), (LX - 4, 1, QZ1 + 3), (16, 1, 82)))
        clear_spawns(b)

    # ============================================================ Dr. Ratchet: Karakuri Castle on Mecha Island
    @lair("karakuri_castle", "Karakuri Castle", "ratchet", OCEANS + DEEP, "sea", group="film_lairs")
    def _(b):
        rnd = random.Random(24)
        CX, CZ = 52, 44
        RX, RZ, RY, CY = 42, 34, 14, -10       # the shell: an ellipsoid whose top is cut flat at y = 0
        SHELL = ["minecraft:green_terracotta"] * 3 + ["minecraft:moss_block", "minecraft:mossy_cobblestone"]
        SCUTE = "minecraft:brown_terracotta"
        # --- Mecha Island itself: a giant sea turtle. The shell, plated in scutes, rises out of the sea; its top is the island.
        for x in range(CX - RX - 1, CX + RX + 2):
            for z in range(CZ - RZ - 1, CZ + RZ + 2):
                e = ((x - CX) / RX) ** 2 + ((z - CZ) / RZ) ** 2
                if e > 1:
                    continue
                ytop = CY + RY * math.sqrt(1 - e)
                yt = min(0, int(round(ytop)))
                for y in range(-16, yt + 1):
                    shell = y >= yt - 2 or y < -14
                    if not shell:
                        b.set(x, y, z, AIR)
                        continue
                    if y == 0:
                        s = "minecraft:mossy_stone_bricks" if rnd.random() < 0.3 else "minecraft:stone_bricks"
                    else:
                        # scute seams: hexagon-ish plates outlined in brown
                        u, v = (x - CX) / 7.0, (z - CZ) / 6.0
                        seam = abs(u - round(u)) < 0.09 or abs(v + 0.5 * (round(u) % 2) - round(v + 0.5 * (round(u) % 2))) < 0.1
                        s = SCUTE if seam else rnd.choice(SHELL)
                    b.set(x, y, z, s)
        b.waterline = -4
        # the shell's rim at the island's edge: a low wall with cannon ports
        for a in range(0, 360, 2):
            t = math.radians(a)
            # where the flat top meets the slope
            k = math.sqrt(1 - (CY / RY) ** 2) if abs(CY) < RY else 0.0
            x, z = round(CX + RX * k * math.cos(t)), round(CZ + RZ * k * math.sin(t))
            b.set(x, 1, z, "minecraft:stone_brick_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]" if a % 10 else "minecraft:stone_bricks")
        # --- The head (east), neck rising out of the sea, two glowing red eyes, and four great flippers.
        HX = CX + RX + 6
        for i in range(10):   # neck
            b.cyl(CX + RX - 2 + i, CZ, 5 - i * 0.15, -6 + i // 2, -2 + i // 2, "minecraft:lime_terracotta")
        b.sphere(HX + 6, 3, CZ, 6.5, "minecraft:lime_terracotta", ry=5.5)
        b.box(HX + 9, 1, CZ - 4, HX + 12, 2, CZ + 4, "minecraft:green_terracotta")   # the jaw line
        for side in (-1, 1):
            b.box(HX + 9, 5, CZ + side * 3, HX + 11, 6, CZ + side * 3, "minecraft:redstone_lamp[lit=true]" if False else "minecraft:shroomlight")
            b.set(HX + 12, 5, CZ + side * 3, "minecraft:red_stained_glass")
        b.set(HX + 13, 3, CZ - 1, "minecraft:black_concrete"); b.set(HX + 13, 3, CZ + 1, "minecraft:black_concrete")
        for (fx, fz, dz) in ((CX + 24, CZ - RZ, -1), (CX + 24, CZ + RZ, 1), (CX - 24, CZ - RZ + 2, -1), (CX - 24, CZ + RZ - 2, 1)):
            for t in range(0, 12):
                for w in range(-3 + t // 4, 4 - t // 4):
                    b.box(fx + w + (t // 3 if fx > CX else -t // 3), -6, fz + dz * t, fx + w + (t // 3 if fx > CX else -t // 3), -4, fz + dz * t, "minecraft:lime_terracotta")
        for t in range(0, 8):   # the tail
            b.box(CX - RX - t, -5, CZ - 1 + t // 4, CX - RX - t, -4, CZ + 1 - t // 4, "minecraft:lime_terracotta")
        # --- Karakuri Castle (west on the shell): a stone base, three white storeys, sweeping dark roofs, gold on the ridge.
        KX, KZ = CX - 16, CZ
        b.box(KX - 10, 1, KZ - 10, KX + 10, 4, KZ + 10, "minecraft:stone_bricks")   # the battered stone base
        for y in range(1, 5):
            for x in range(KX - 11 + y // 2, KX + 12 - y // 2):
                for z in (KZ - 11 + y // 2, KZ + 11 - y // 2):
                    b.set(x, y, z, "minecraft:cobblestone") if y < 4 else None
        b.box(KX - 9, 1, KZ - 9, KX + 9, 4, KZ + 9, AIR)
        b.box(KX - 9, 1, KZ - 9, KX + 9, 1, KZ + 9, "minecraft:stone_bricks")   # floor of the machine hall
        b.box(KX - 9, 4, KZ - 9, KX + 9, 4, KZ + 9, "minecraft:spruce_planks")
        b.box(KX + 10, 2, KZ - 1, KX + 10, 3, KZ + 1, AIR)   # its gate, onto the courtyard
        b.box(KX + 11, 1, KZ - 1, KX + 11, 1, KZ + 1, "minecraft:stone_bricks")
        # storeys: 1st y 5..10 (16 x 16), 2nd y 11..15 (12 x 12), 3rd y 16..20 (8 x 8): Ratchet's workshop
        storeys = ((8, 5, 5), (6, 11, 4), (4, 16, 4))
        for (hw, y0, h) in storeys:
            b.hall(KX - hw, KZ - hw, KX + hw, KZ + hw, y0, h, "minecraft:white_concrete", "minecraft:white_concrete", log("dark_oak"),
                   trim="minecraft:black_concrete", floor="minecraft:spruce_planks", win=pane("black"), every=2, win_h=1, proud=False)
            b.pagoda_roof(KX - hw, KZ - hw, KX + hw, KZ + hw, y0 + h + 1, "deepslate_tile", "minecraft:deepslate_tiles", ov=2)
            b.box(KX - hw + 1, y0 + h + 1, KZ - hw + 1, KX + hw - 1, y0 + h + 1, KZ + hw - 1, "minecraft:spruce_planks")
        b.box(KX - 3, 21, KZ - 3, KX + 3, 21, KZ + 3, "minecraft:spruce_planks")
        top = 26
        b.set(KX - 4, top, KZ, GOLD_BRICK); b.set(KX + 4, top, KZ, GOLD_BRICK)   # golden shachihoko on the ridge
        b.set(KX - 4, top + 1, KZ, "minecraft:gold_block"); b.set(KX + 4, top + 1, KZ, "minecraft:gold_block")
        b.box(KX - 3, top - 1, KZ, KX + 3, top - 1, KZ, "minecraft:deepslate_tiles")
        # ladders up through the storeys (south-west corner), with holes through each floor
        for y in range(2, 21):
            b.set(KX - 7 if y < 11 else KX - 5 if y < 16 else KX - 3, y, KZ + (7 if y < 11 else 5 if y < 16 else 3) - 1, ladder("north"))
        for (hx, hz, yy) in ((KX - 7, KZ + 6, 4), (KX - 7, KZ + 6, 5), (KX - 5, KZ + 4, 11), (KX - 5, KZ + 4, 10), (KX - 3, KZ + 2, 16), (KX - 3, KZ + 2, 15)):
            b.set(hx, yy, hz, AIR)
        for y in range(5, 11):
            b.set(KX - 7, y, KZ + 6, ladder("north"))
        for y in range(10, 16):
            b.set(KX - 5, y, KZ + 4, ladder("north"))
        for y in range(15, 21):
            b.set(KX - 3, y, KZ + 2, ladder("north"))
        for y in range(2, 5):
            b.set(KX - 7, y, KZ + 6, ladder("north"))
        # the machine hall (base): half-built mechs, gears on the walls, a forge
        for x in range(KX - 8, KX + 9, 4):
            b.set(x, 2, KZ - 9 + 1, facing("tool_bench", "south")) if x % 8 else b.set(x, 2, KZ - 8, "minecraft:anvil[facing=east]")
            b.set(x, 2, KZ + 8, facing("crate_stack", "north"))
        b.box(KX - 2, 2, KZ - 3, KX + 2, 3, KZ + 1, "minecraft:iron_block")   # a Tetsujin-kun 32 hull on the stocks
        b.set(KX, 3, KZ - 4, facing("cannon", "north")); b.set(KX + 3, 2, KZ - 1, "minecraft:piston[extended=false,facing=east]")
        b.set(KX - 6, 2, KZ, "minecraft:blast_furnace[facing=east,lit=true]"); b.set(KX - 6, 2, KZ + 1, "minecraft:smithing_table")
        b.set(KX - 4, 3, KZ - 6, HANG) if False else b.set(KX - 4, 3, KZ - 6, "minecraft:lantern[hanging=true,waterlogged=false]")
        b.set(KX + 4, 3, KZ + 5, "minecraft:lantern[hanging=true,waterlogged=false]")
        # first storey: the guards' barracks
        for x in range(KX - 6, KX + 7, 3):
            bed("yellow", x, 6, KZ - 7, b, "south")
        b.set(KX + 6, 6, KZ + 6, facing("weapon_rack", "north")); b.set(KX + 4, 6, KZ + 6, BARREL)
        b.set(KX, 10, KZ, HANG)
        # second storey: the throne room of the lord of Mecha Island
        b.box(KX - 2, 12, KZ - 5, KX + 2, 12, KZ - 4, GOLD_BRICK)
        b.set(KX, 13, KZ - 5, facing("throne", "south"))
        for z in range(KZ - 3, KZ + 5):
            b.set(KX, 12, z, carpet("yellow"))
        b.set(KX, 15, KZ, facing("iron_chandelier", "north"))
        # third storey: Ratchet's workshop, where the chest is: blueprints, clocks, a drafting table
        b.chest(KX, 17, KZ - 3, "karakuri_castle", "south")
        b.set(KX - 2, 17, KZ - 3, facing("drafting_table", "south")); b.set(KX + 2, 17, KZ - 3, facing("tool_bench", "south"))
        b.set(KX + 3, 17, KZ, "minecraft:lectern[facing=west,has_book=false,powered=false]")
        b.set(KX - 3, 17, KZ, facing("globe", "east")) if False else b.set(KX + 3, 17, KZ + 2, facing("small_crate", "west"))
        b.set(KX, 20, KZ, "minecraft:lantern[hanging=true,waterlogged=false]")
        # --- The courtyard (the arena, east on the shell) with the clockwork giant Tetsujin-kun 28 standing guard.
        AX, AZ = CX + 12, CZ
        for x in range(AX - 13, AX + 14):
            for z in range(AZ - 13, AZ + 14):
                d = math.hypot(x - AX, z - AZ)
                if d <= 13 and b.get(x, 0, z) is not None:
                    b.set(x, 0, z, "minecraft:polished_andesite" if d < 12 else "minecraft:stone_bricks")
                    if d < 3:
                        b.set(x, 0, z, "minecraft:iron_block")
        # a giant cog set in the floor
        for a in range(0, 360, 8):
            r = 9 if (a // 8) % 3 else 10
            b.set(round(AX + r * math.cos(math.radians(a))), 0, round(AZ + r * math.sin(math.radians(a))), "minecraft:waxed_copper_block")
        for a in range(0, 360, 45):
            for r in range(3, 9):
                b.set(round(AX + r * math.cos(math.radians(a))), 0, round(AZ + r * math.sin(math.radians(a))), "minecraft:waxed_copper_block")
        # Tetsujin-kun 28, wound down at the north edge of the courtyard: a blocky mech with a drill and a claw
        TX, TZ = AX, AZ - 15
        b.box(TX - 3, 1, TZ - 1, TX - 1, 6, TZ + 1, "minecraft:iron_block"); b.box(TX + 1, 1, TZ - 1, TX + 3, 6, TZ + 1, "minecraft:iron_block")   # legs
        b.box(TX - 4, 1, TZ - 2, TX - 1, 1, TZ + 2, "minecraft:polished_deepslate"); b.box(TX + 1, 1, TZ - 2, TX + 4, 1, TZ + 2, "minecraft:polished_deepslate")   # magnetic feet
        b.box(TX - 4, 7, TZ - 2, TX + 4, 14, TZ + 2, "minecraft:yellow_terracotta")   # body
        b.box(TX - 2, 9, TZ + 3, TX + 2, 12, TZ + 3, "minecraft:glass")   # cockpit window, facing the arena
        b.box(TX - 2, 15, TZ - 1, TX + 2, 17, TZ + 1, "minecraft:iron_block")   # head
        b.set(TX - 1, 16, TZ + 2, "minecraft:shroomlight"); b.set(TX + 1, 16, TZ + 2, "minecraft:shroomlight")
        b.box(TX - 7, 9, TZ - 1, TX - 5, 14, TZ + 1, "minecraft:iron_block")   # drill arm
        for i in range(5):
            b.box(TX - 6 - 0, 8 - i, TZ, TX - 6, 8 - i, TZ, ROD if i == 4 else "minecraft:iron_block")
        b.box(TX + 5, 9, TZ - 1, TX + 7, 14, TZ + 1, "minecraft:iron_block")   # claw arm on a cable
        b.box(TX + 6, 4, TZ, TX + 6, 8, TZ, CHAIN)
        b.box(TX + 5, 3, TZ - 1, TX + 7, 3, TZ + 1, "minecraft:polished_blackstone"); b.set(TX + 5, 2, TZ, "minecraft:pointed_dripstone[thickness=tip,vertical_direction=down,waterlogged=false]") if False else None
        b.box(TX - 1, 9, TZ - 3, TX + 1, 12, TZ - 3, GOLD_BRICK)   # the wind-up key in its back
        b.box(TX, 10, TZ - 4, TX, 11, TZ - 4, GOLD_BRICK); b.box(TX, 8, TZ - 5, TX, 13, TZ - 5, GOLD_BRICK)
        b.set(TX + 6, 2, TZ, "minecraft:iron_block")
        # the shell cannons: four turrets on the rim (Super Zogame-kun's guns)
        for (gx, gz, f) in ((CX + 26, CZ - 18, "north"), (CX + 26, CZ + 18, "south"), (CX - 2, CZ - 24, "north"), (CX - 2, CZ + 24, "south")):
            b.cyl(gx, gz, 2.5, 1, 2, "minecraft:iron_block")
            b.disk(gx, 3, gz, 2.5, "minecraft:polished_deepslate")
            b.set(gx, 4, gz, facing("cannon", f)); b.set(gx + 1, 4, gz, facing("cannonball_pile", f))
        # a clock tower of gears on the castle's south-east corner
        GX, GZ = KX + 12, KZ + 12
        b.box(GX - 1, 1, GZ - 1, GX + 1, 18, GZ + 1, "minecraft:polished_andesite")
        for y in range(4, 18, 5):
            b.box(GX - 1, y, GZ - 1, GX + 1, y, GZ + 1, "minecraft:waxed_copper_block")
        b.box(GX - 2, 18, GZ - 2, GX + 2, 18, GZ + 2, "minecraft:stone_bricks")
        for a in range(0, 360, 30):   # the clock face, facing south
            b.set(round(GX + 3 * math.cos(math.radians(a))), round(14 + 3 * math.sin(math.radians(a))), GZ + 2, GOLD_BRICK)
        b.set(GX, 14, GZ + 2, "minecraft:gold_block"); b.box(GX, 15, GZ + 2, GX, 16, GZ + 2, "minecraft:black_concrete"); b.set(GX + 1, 14, GZ + 2, "minecraft:black_concrete")
        b.hip_roof(GX - 2, GZ - 2, GX + 2, GZ + 2, 19, "deepslate_tile", "minecraft:deepslate_tiles", ov=1, cap=GOLD_BRICK)
        # lamps and crates around the island top; a jetty off the south side
        for a in range(20, 360, 40):
            t = math.radians(a)
            x, z = round(CX + RX * 0.62 * math.cos(t)), round(CZ + RZ * 0.62 * math.sin(t))
            if b.get(x, 1, z) in (None, AIR) and b.get(x, 0, z) is not None:
                b.lamp_post(x, 1, z, "dark_oak", 3, LANTERN)
        for (x, z) in ((CX + 4, CZ - 16), (CX + 2, CZ + 16), (CX + 20, CZ + 14)):
            b.crates(x, 1, z, rnd, n=4, spread=2)
        # Clear the air over the shell's top, so nothing the sea had there pokes through.
        for x in range(CX - RX, CX + RX + 1):
            for z in range(CZ - RZ, CZ + RZ + 1):
                if b.get(x, 0, z) is not None:
                    for y in range(1, 6):
                        if b.get(x, y, z) is None:
                            b.set(x, y, z, AIR)

        b.rogue(AX, 1, AZ, "ratchet")
        b.crew("karakuri_soldier", ((AX - 7, AZ - 6), (AX + 7, AZ - 6), (AX - 7, AZ + 6), (AX + 7, AZ + 6), (KX + 12, KZ - 4)))
        b.crew("karakuri_soldier", ((KX + 3, KZ + 3),), y=6)
        clear_spawns(b)

    # ============================================================ Byrnndi World: the Groseade
    @lair("groseade", "The Groseade", "byrnndi_world",
          ["minecraft:stony_shore", "minecraft:snowy_beach", "minecraft:beach", "minecraft:snowy_plains", "minecraft:plains"],
          "land", group="film_lairs")
    def _(b):
        rnd = random.Random(25)
        W, D = 100, 92
        ground = ["minecraft:gravel", "minecraft:stone", "minecraft:andesite", "minecraft:coarse_dirt", "minecraft:gravel", "minecraft:tuff"]
        for x in range(0, W + 1):
            for z in range(0, D + 1):
                b.set(x, -1, z, "minecraft:stone"); b.set(x, 0, z, rnd.choice(ground))
        SCORCH = ["minecraft:blackstone", "minecraft:basalt[axis=y]", "minecraft:smooth_basalt", "minecraft:magma_block", "minecraft:blackstone", "minecraft:coal_block"]
        # --- The Groseade (the landmark, north): the World Pirates' warship hauled up on a stone slipway, its bow cannon
        # (the gun that can sink an island) raised at the sky.
        sx, sz, L, SW = 10, 6, 58, 17
        b.box(sx - 2, 0, sz - 1, sx + L + 2, 2, sz + SW, "minecraft:stone_bricks")   # the slipway
        for x in range(sx, sx + L, 6):
            b.box(x, 3, sz + 2, x, 4, sz + SW - 3, "minecraft:polished_deepslate")   # cradle beams
        deck = b.ship(sx, 3, sz, L, SW, hull="minecraft:black_concrete", deck="minecraft:dark_oak_planks", masts=((14, 20), (28, 24), (42, 20)),
                      sail="minecraft:purple_wool", flag=("minecraft:black_wool", "minecraft:purple_wool"), cabin=(10, 5, "minecraft:polished_blackstone_bricks"), depth=6)
        b.mast_yard(sx, deck, sz, SW, ((14, 20), (28, 24), (42, 20)))
        b.support(sx - 2, sz - 1, sx + L + 2, sz + SW, 3, ["minecraft:stone_bricks"], rnd, down_to=1)
        cz = sz + SW // 2
        for x in range(sx + 2, sx + L - 6):   # a purple stripe along the hull
            for z in range(sz, sz + SW):
                if b.get(x, deck - 2, z) == "minecraft:black_concrete" and (b.get(x, deck - 2, z - 1) in (None, AIR) or b.get(x, deck - 2, z + 1) in (None, AIR)):
                    b.set(x, deck - 2, z, "minecraft:purple_concrete")
        for x in range(sx + 14, sx + 46, 4):
            b.set(x, deck + 1, sz + 2, facing("cannon", "north")); b.set(x, deck + 1, sz + SW - 3, facing("cannon", "south"))
        # the great bow cannon, mounted on a turret at the bow and aimed up over the sea
        GX, GY = sx + L - 6, deck + 1
        b.cyl(GX, cz, 3.5, GY, GY + 2, "minecraft:polished_blackstone")
        b.disk(GX, GY + 3, cz, 3.5, "minecraft:iron_block")
        for t in range(0, 26):
            x = GX + round(t * 0.75); y = GY + 4 + round(t * 0.62)
            r = 2.4 if t < 22 else 2.9
            for dz in range(-3, 4):
                for dy in range(-3, 4):
                    d = math.hypot(dz, dy)
                    if d <= r:
                        b.set(x, y + dy, cz + dz, "minecraft:black_concrete" if d > r - 1 else (AIR if t > 18 else "minecraft:black_concrete"))
            if t in (6, 14, 21):
                for dz in range(-3, 4):
                    for dy in range(-3, 4):
                        if 2.4 < math.hypot(dz, dy) <= 3.2:
                            b.set(x, y + dy, cz + dz, "minecraft:purple_concrete")
        b.support(GX - 1, cz - 3, GX + 21, cz + 3, GY + 4, ["minecraft:polished_blackstone"], rnd, down_to=GY + 3) if False else None
        b.box(GX - 1, GY + 3, cz - 1, GX + 4, GY + 9, cz + 1, "minecraft:polished_blackstone")   # the gun's mount
        # World's cabin in the stern (where the chest is), with the captain's things
        cab_x0, cab_z0, cab_z1 = sx + 1, sz + 2, sz + SW - 3
        b.chest(sx + 3, deck + 1, cz, "groseade", "east")
        b.set(sx + 6, deck + 1, cz, facing("captains_chair", "west")) if False else b.set(sx + 5, deck + 1, cz - 2, facing("chart_table", "east"))
        b.set(sx + 5, deck + 1, cz + 2, facing("wine_rack", "east")); b.set(sx + 8, deck + 1, cz - 3, facing("weapon_rack", "south"))
        b.set(sx + 8, deck + 1, cz + 3, "minecraft:white_bed[facing=west,occupied=false,part=head]" if False else facing("treasure_pile", "north"))
        b.set(sx + 6, deck + 4, cz, HANG)
        for z in range(cz - 1, cz + 2):
            b.set(sx + 3, deck + 1, z, carpet("purple")) if z != cz else None
        # gangway down from the deck to the slipway (south side)
        for i in range(deck - 2):
            b.set(sx + 32 + i, deck - i, sz + SW, stair("dark_oak", "west"))
            b.box(sx + 32 + i, deck - i + 1, sz + SW, sx + 32 + i, deck - i + 3, sz + SW, AIR)
            for yy in range(1, deck - i):
                b.set(sx + 32 + i, yy, sz + SW, "minecraft:stone_bricks")
        b.box(sx + 31, deck + 1, sz + SW - 1, sx + 31, deck + 2, sz + SW - 1, AIR)
        # --- The crater (the arena, centre-south): where World tried out a pebble at a hundred times the speed.
        AX, AZ, R = 50, 60, 15
        for x in range(AX - R - 4, AX + R + 5):
            for z in range(AZ - R - 4, AZ + R + 5):
                d = math.hypot(x - AX, z - AZ) + rnd.random() * 0.8
                if d <= R:
                    b.set(x, 0, z, rnd.choice(SCORCH) if d > 3 else "minecraft:magma_block")
                    b.set(x, -1, z, "minecraft:blackstone")
                elif d <= R + 3.5:
                    h = round(3 * (1 - abs(d - (R + 1.2)) / 2.4))
                    for y in range(1, h + 1):
                        b.set(x, y, z, rnd.choice(["minecraft:cobblestone", "minecraft:gravel", "minecraft:tuff", "minecraft:blackstone"]))
        for (bx2, bz2, br) in ((AX - 11, AZ + 1, 1.8), (AX + 3, AZ - 11, 2.0), (AX + 2, AZ + 11, 1.5)):   # thrown boulders
            b.sphere(bx2, 1, bz2, br, "minecraft:tuff", ry=br)
        b.set(AX, 1, AZ, AIR)
        for i in range(0, 360, 60):   # the openings in the rim
            a = math.radians(i + 30)
            for r in range(R - 1, R + 5):
                x, z = round(AX + r * math.cos(a)), round(AZ + r * math.sin(a))
                for dx in (-1, 0, 1):
                    for y in range(1, 5):
                        b.set(x + dx, y, z, AIR)
        # --- The camp (east): tents of sailcloth, a mess fire, and the ammunition dump of giant shells.
        for (tx, tz, col) in ((80, 30, "purple"), (88, 40, "black"), (78, 48, "purple"), (90, 56, "black")):
            for i in range(4):
                b.box(tx - 3 + i, 1 + i, tz - 3, tx - 3 + i, 1 + i, tz + 3, f"minecraft:{col}_wool")
                b.box(tx + 3 - i, 1 + i, tz - 3, tx + 3 - i, 1 + i, tz + 3, f"minecraft:{col}_wool")
            b.box(tx - 2, 1, tz - 2, tx + 2, 3, tz + 2, AIR) if False else None
            for i in range(1, 3):
                b.box(tx - 3 + i, 1, tz - 3, tx + 3 - i, i, tz - 3, AIR)
            bed("purple", tx - 1, 1, tz, b, "south"); b.set(tx + 1, 1, tz + 2, BARREL)
        b.set(84, 1, 46, CAMPFIRE)
        for (dx, dz) in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            b.set(84 + dx, 1, 46 + dz, facing("oak_stool", "north")) if False else b.set(84 + dx, 1, 46 + dz, "minecraft:spruce_slab[type=bottom,waterlogged=false]")
        for k, (x, z) in enumerate(((70, 68), (73, 70), (76, 67), (71, 73), (75, 74))):   # cannon shells taller than a man
            b.box(x, 1, z, x, 3, z, "minecraft:waxed_copper_block" if k % 2 else "minecraft:gold_block" if False else GOLD_BRICK)
            b.set(x, 4, z, "minecraft:polished_blackstone")
            b.set(x, 5, z, ROD)
        for (x, z) in ((66, 70), (80, 72), (68, 76)):
            b.set(x, 1, z, facing("powder_keg", "north")); b.set(x + 1, 1, z, facing("cannonball_pile", "north"))
        # --- The broken Marine outpost (west): a fort he tore through, holes punched clean through its walls.
        FX0, FZ0, FX1, FZ1 = 4, 40, 28, 78
        for x in range(FX0, FX1 + 1):
            for z in range(FZ0, FZ1 + 1):
                if x in (FX0, FX1) or z in (FZ0, FZ1):
                    for y in range(1, 9):
                        b.set(x, y, z, MARINE_BRICK if rnd.random() < 0.8 else "minecraft:cracked_stone_bricks")
                    if (x + z) % 2 == 0:
                        b.set(x, 9, z, MARINE_BRICK)
        for (hx, hy, hz, r) in ((FX1, 4, 50, 3.4), (FX1, 5, 66, 2.8), (16, 4, FZ0, 3.0), (FX0, 3, 60, 2.2), (22, 6, FZ1, 3.6)):
            for x in range(int(hx - r) - 1, int(hx + r) + 2):
                for y in range(int(hy - r) - 1, int(hy + r) + 2):
                    for z in range(int(hz - r) - 1, int(hz + r) + 2):
                        if math.sqrt((x - hx) ** 2 + (y - hy) ** 2 + (z - hz) ** 2) <= r and y >= 1:
                            b.set(x, y, z, AIR)
        b.hall(FX0 + 3, FZ0 + 3, FX1 - 3, FZ0 + 14, 0, 6, "minecraft:white_concrete", MARINE_BRICK, "minecraft:polished_andesite", trim="minecraft:light_blue_concrete",
               floor="minecraft:polished_andesite", win=pane("light_blue"), every=4, doors=[("south", 9, 3, 3)], proud=False)
        b.box(FX0 + 4, 6, FZ0 + 4, FX1 - 4, 6, FZ0 + 13, "minecraft:white_concrete")
        for x in range(FX0 + 8, FX0 + 14):   # its roof caved in
            for z in range(FZ0 + 5, FZ0 + 11):
                if rnd.random() < 0.7:
                    b.set(x, 6, z, AIR)
                    b.set(x, 1, z, rnd.choice(["minecraft:cobblestone", "minecraft:gravel", AIR]))
        for x in range(FX0 + 5, FX1 - 4, 3):
            b.set(x, 1, FZ0 + 4, "onepiece:prison_bars" if False else BARS_X)
            b.set(x, 2, FZ0 + 4, BARS_X)
        b.set(FX1 - 5, 1, FZ0 + 12, facing("filing_cabinet", "north")); b.set(FX1 - 6, 1, FZ0 + 12, facing("notice_board", "north"))
        b.set(FX0 + 5, 5, FZ0 + 9, HANG)
        b.flag(FX0 + 2, 1, FZ1 - 3, h=10, colors=("minecraft:white_wool", "minecraft:light_blue_wool"), skull=False, length=4)
        for x in range(FX0 + 2, FX0 + 6):   # the Marine flag torn down
            b.set(x, 1, FZ1 - 6, "minecraft:white_carpet")
        # --- A lookout of piled scrap and timber on the crater's rim, and the road down to the shore.
        LX, LZ = AX + 20, AZ - 18
        for y in range(1, 15):
            for (dx, dz) in ((0, 0), (2, 0), (0, 2), (2, 2)):
                b.set(LX + dx, y, LZ + dz, log("dark_oak") if y % 4 else "minecraft:iron_block")
        b.box(LX - 1, 15, LZ - 1, LX + 3, 15, LZ + 3, "minecraft:dark_oak_planks")
        b.walls(LX - 1, 16, LZ - 1, LX + 3, 16, LZ + 3, fence("dark_oak"))
        for y in range(1, 16):
            b.set(LX + 1, y, LZ + 1, ladder("south")) if False else b.set(LX + 1, y, LZ - 1, ladder("north"))
        b.set(LX + 1, 17, LZ + 1, LANTERN)
        for z in range(AZ + R + 3, D + 1):
            for x in range(AX - 2, AX + 3):
                b.set(x, 0, z, "minecraft:gravel" if abs(x - AX) < 2 else "minecraft:cobblestone")
        for (x, z) in ((AX - 4, AZ + R + 6), (AX + 4, AZ + R + 6), (AX - 4, D - 3), (AX + 4, D - 3)):
            b.lamp_post(x, 1, z, "dark_oak", 4, LANTERN)
        for (x, z) in ((96, 10), (94, 84), (40, 86), (4, 88), (60, 32)):
            b.sphere(x, 0, z, 2.6, "minecraft:andesite", upper=True, ry=2.2)

        b.rogue(AX, 1, AZ, "byrnndi_world")
        b.crew("world_pirate", ((AX - 8, AZ - 7), (AX + 8, AZ - 7), (AX - 8, AZ + 7), (AX + 8, AZ + 7), (84, 43), (sx + 24, deck + 1, cz)))
        clear_spawns(b)


LOOT = {
    "gold_island": table((5, 8, [item(BERRY, 10, 16, 40), item("minecraft:gold_ingot", 12, 4, 16), item("minecraft:raw_gold", 8, 4, 12),
                                 item("minecraft:gold_block", 4, 1, 3), item("minecraft:diamond", 4, 1, 3), item("minecraft:golden_apple", 5, 1, 2),
                                 item("minecraft:golden_pickaxe", 3, 1, 1, ENCHANT), item("minecraft:map", 3), item("minecraft:spyglass", 2),
                                 item("onepiece:berry_block", 2, 1, 1)]), rumor("el_drago")),
    "salamander": table((6, 9, [item(BERRY, 10, 24, 56), item("minecraft:honey_bottle", 8, 2, 6), item("minecraft:sugar", 8, 4, 16),
                                item("minecraft:diamond", 5, 1, 4), item("minecraft:iron_block", 5, 1, 3), item("minecraft:netherite_scrap", 3, 1, 2),
                                item("minecraft:golden_apple", 5, 1, 3), item("minecraft:enchanted_golden_apple", 1), item("minecraft:wheat", 4, 4, 12),
                                item("minecraft:iron_sword", 2, 1, 1, ENCHANT)]), rumor("gasparde")),
    "omatsuri_island": table((6, 9, [item(BERRY, 10, 24, 56), item("minecraft:bow", 4, 1, 1, ENCHANT), item("minecraft:spectral_arrow", 6, 8, 24),
                                     item("minecraft:arrow", 8, 16, 32), item("minecraft:firework_rocket", 6, 4, 12), item("minecraft:diamond", 5, 1, 4),
                                     item("minecraft:golden_apple", 5, 1, 3), item("minecraft:enchanted_golden_apple", 1), item("minecraft:spore_blossom", 3, 1, 2),
                                     item("minecraft:lily_of_the_valley", 4, 2, 6)]),
                             (1, 1, [item("minecraft:enchanted_book", 1, 1, 1, ENCHANT)]), rumor("baron_omatsuri")),
    "karakuri_castle": table((6, 9, [item(BERRY, 10, 24, 56), item("minecraft:redstone", 10, 8, 24), item("minecraft:clock", 5), item("minecraft:piston", 5, 1, 4),
                                     item("minecraft:copper_ingot", 8, 4, 16), item("minecraft:diamond", 5, 1, 4), item("minecraft:netherite_scrap", 3, 1, 2),
                                     item("minecraft:golden_apple", 5, 1, 3), item("minecraft:enchanted_golden_apple", 1), item("minecraft:crossbow", 2, 1, 1, ENCHANT),
                                     item("minecraft:tnt", 3, 1, 4)]), rumor("ratchet")),
    "groseade": table((6, 10, [item(BERRY, 10, 32, 64), item("minecraft:gunpowder", 8, 6, 16), item("minecraft:fire_charge", 6, 2, 8),
                               item("minecraft:diamond", 6, 2, 6), item("minecraft:netherite_scrap", 4, 1, 3), item("minecraft:netherite_ingot", 2),
                               item("minecraft:enchanted_golden_apple", 2), item("minecraft:totem_of_undying", 2), item("minecraft:mace", 1, 1, 1, ENCHANT),
                               item("minecraft:wind_charge", 6, 4, 12)]),
                      (1, 2, [item("minecraft:enchanted_book", 1, 1, 1, ENCHANT)]), rumor("byrnndi_world")),
}
