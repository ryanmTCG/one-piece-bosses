#!/usr/bin/env python3
"""Builds each rogue's lair: the structure (.nbt), how and where it generates, and its chest loot.

    python3 tools/lairs/gen_lairs.py .

Writes into src/main/resources/data/opbosses/: structure/, worldgen/structure, worldgen/template_pool,
worldgen/structure_set, tags/worldgen/biome/has_structure and loot_table/chests. Change a lair here and run it
again; it rewrites all of those folders. Builds with the One Piece Mod's building kit (kit.py), so they work the
same way as its lairs: the boss and its crew appear when the chunk is first made, and only then.
Coordinates: x east, y up, z south; y = 0 is the ground. A "sea" lair sets waterline, the level that sits at the sea's surface;
its blocks below y = 0 reach down toward the sea floor.
"""
import json
import math
import os
import random
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kit import *   # noqa: E402,F401  (B, AIR, FENCE, LANTERN, HANG, ... and NEW_CHAR_TAG, GUARD_TAG)
from nbt import Byte  # noqa: E402

KIT_TAG_PREFIX = "onepiece_kit_"   # the main mod's GuardKit.KIT_TAG_PREFIX


class Lair(B):
    """The main mod's canvas, plus this mod's boss, crews and chests."""

    def rogue(self, x, y, z, boss_id):
        # The main mod sets up any of its boss mobs carrying this tag when the chunk loads; rogues are those mobs too.
        self.entities.append(("opbosses:rogue_boss", x, y, z,
                              {"Character": boss_id, "Boss": Byte(1), "PersistenceRequired": Byte(1), "Tags": [NEW_CHAR_TAG]}))

    def crew(self, kit, spots, y=1):
        # The main mod turns a pirate NPC with these tags into a guard from that kit (our kits are in its list).
        for (x, z) in spots:
            self.entities.append(("onepiece:sea_pirate", x, y, z,
                                  {"PersistenceRequired": Byte(1), "Tags": [GUARD_TAG, KIT_TAG_PREFIX + kit]}))

    def chest(self, x, y, z, loot, facing="south"):
        self.set(x, y, z, f"minecraft:chest[facing={facing},type=single,waterlogged=false]",
                 {"id": "minecraft:chest", "LootTable": f"opbosses:chests/{loot}"})

    def scatter(self, x0, z0, x1, z1, y, blocks, chance, rnd, only_on=None, replace=False):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if rnd.random() < chance and (replace or self.get(x, y, z) in (None, AIR)) and (only_on is None or self.get(x, y - 1, z) in only_on):
                    self.set(x, y, z, rnd.choice(blocks))

    def support(self, x0, z0, x1, z1, y, blocks, rnd, down_to=0):
        """Fills the empty space under every block at level y down to the ground, so nothing floats."""
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if self.get(x, y, z) in (None, AIR):
                    continue
                yy = y - 1
                while yy >= down_to and self.get(x, yy, z) in (None, AIR):
                    self.set(x, yy, z, rnd.choice(blocks))
                    yy -= 1

    def skirt(self, cx, cz, r, y0, y1, blocks, rnd, spread=0.35, sz=1.0):
        """A pile under a sea lair from y1 down to y0, widening as it goes down, so it reaches the sea floor."""
        for y in range(y1, y0 - 1, -1):
            rr = r + (y1 - y) * spread
            for x in range(int(cx - rr) - 2, int(cx + rr) + 3):
                for z in range(int(cz - rr) - 2, int(cz + rr) + 3):
                    d = math.hypot(x - cx, (z - cz) * sz) + rnd.random() * 1.6
                    if rr - 3 < d <= rr or (y == y1 and d <= rr):   # a shell: nobody sees the inside
                        self.set(x, y, z, rnd.choice(blocks))


LAIRS = []


def lair(name, title, boss, biomes, place):
    def deco(fn):
        LAIRS.append(dict(name=name, title=title, boss=boss, biomes=biomes, place=place, build=fn))
        return fn
    return deco


WALL = "minecraft:{}_wall[east=none,north=none,south=none,west=none,up=true,waterlogged=false]"
STAIRS = "minecraft:{}_stairs[facing={},half=bottom,shape=straight,waterlogged=false]"
SLAB = "minecraft:{}_slab[type=bottom,waterlogged=false]"
COBWEB = "minecraft:cobweb"
OCEANS = ["minecraft:ocean", "minecraft:lukewarm_ocean", "minecraft:warm_ocean", "minecraft:cold_ocean", "onepiece:east_blue"]
DEEP = ["minecraft:deep_ocean", "minecraft:deep_lukewarm_ocean", "minecraft:deep_cold_ocean", "onepiece:fishman_reef"]


# ============================================================ Saltjaw Rourke: the Scrapheap Reef
@lair("scrapheap_reef", "The Scrapheap Reef", "saltjaw_rourke", ["#minecraft:is_beach"] + OCEANS, "sea")
def _(b):
    rnd = random.Random(1)
    scrap = ["minecraft:iron_block", "minecraft:oxidized_copper", "minecraft:weathered_cut_copper", "minecraft:dark_oak_planks",
             "minecraft:stripped_spruce_log[axis=x]", "minecraft:gravel", "minecraft:exposed_copper", "minecraft:spruce_planks",
             "minecraft:rooted_dirt", "minecraft:mossy_cobblestone"]
    for y in range(0, 5):
        r = 15 - y * 0.8
        for x in range(-16, 17):
            for z in range(-16, 17):
                d = math.hypot(x * 1.0, z * 1.25) + rnd.random() * 1.6
                if d <= r:
                    b.set(x + 16, y, z + 16, rnd.choice(scrap))
    # Under the water, the heap goes on down to the sea floor (no gravel: it would fall into the gaps).
    rubble = ["minecraft:cobblestone", "minecraft:mossy_cobblestone", "minecraft:oxidized_copper", "minecraft:dark_oak_planks", "minecraft:iron_block"]
    b.skirt(16, 16, 15, -14, -1, rubble, rnd, sz=1.25)
    # The yard: a deck of salvaged planks in the middle, where Rourke fights.
    b.disk(16, 4, 16, 7.5, "minecraft:spruce_planks")
    b.disk(16, 4, 16, 3, "minecraft:stripped_dark_oak_wood[axis=y]")
    b.cyl(16, 16, 9, 5, 9, AIR)
    # Two wrecks dragged ashore: one on its side, one broken in half.
    dy = b.ship(1, 2, 1, 16, 9, hull="minecraft:dark_oak_planks", deck="minecraft:spruce_planks", masts=((8, 6),),
                sail="minecraft:gray_wool", flag=None, depth=3)
    b.box(13, 3, 1, 17, 9, 10, AIR)   # snapped off at the middle
    dy2 = b.ship(18, 2, 22, 14, 8, hull="minecraft:spruce_planks", deck="minecraft:oak_planks", masts=(), flag=None, depth=3)
    b.box(18, 3, 22, 21, 8, 30, AIR)
    b.waterline = 3   # y = 3 sits at the sea's surface; the island is piled up out of the water (set after ship(), which sets it too)
    # The crane Rourke hauls wrecks in with, his spare anchor still hanging from the chain.
    for y in range(5, 19):
        b.set(28, y, 8, log("spruce"))
    b.support(28, 8, 28, 8, 5, [log("spruce")], rnd, down_to=-14)   # the crane stands off the shore, on a pile driven into the sea floor
    b.box(18, 18, 8, 28, 18, 8, log("spruce", "x"))
    for y in range(11, 18):
        b.set(19, y, 8, CHAIN)
    b.box(19, 9, 8, 19, 10, 8, "minecraft:iron_block")          # shank
    b.box(17, 8, 8, 21, 8, 8, "minecraft:iron_block")          # arms
    b.set(17, 9, 8, "minecraft:iron_block"); b.set(21, 9, 8, "minecraft:iron_block")   # flukes
    b.set(19, 11, 8, "minecraft:iron_bars[east=true,north=false,south=false,west=true,waterlogged=false]")
    # Scrap piles and salvage around the yard.
    for x, z in ((7, 20), (24, 18), (10, 26), (25, 25)):
        b.sphere(x, 5, z, 2.2, rnd.choice(scrap), ry=1.6, upper=True)
        b.support(x - 3, z - 3, x + 3, z + 3, 5, rubble, rnd, down_to=-14)   # piles past the shore stand on rubble, not on nothing
    for x, z, s in ((9, 12, "minecraft:anvil[facing=north]"), (23, 13, "minecraft:chipped_anvil[facing=east]"), (12, 22, BARREL),
                    (21, 21, BARREL), (22, 20, "minecraft:cauldron"), (11, 11, "minecraft:damaged_anvil[facing=south]")):
        b.set(x, 5, z, s)
    for x, z in ((8, 16), (24, 16), (16, 8), (16, 24)):
        b.box(x, 5, z, x, 6, z, FENCE.format("spruce")); b.set(x, 7, z, LANTERN)
    b.flag(10, 5, 21, h=9, colors=("minecraft:brown_wool", "minecraft:white_wool"))
    b.chest(13, 5, 19, "scrapheap_reef", "east")
    b.rogue(16, 5, 16, "saltjaw_rourke")
    b.crew("scrapdeck_raider", ((11, 14), (21, 15), (16, 22)), y=5)


# ============================================================ Corvina: the Lantern House
@lair("lantern_house", "The Widow's Lantern House", "corvina_fog_widow",
      ["minecraft:swamp", "minecraft:mangrove_swamp", "onepiece:thriller_bark"], "land")
def _(b):
    rnd = random.Random(2)
    W, D = 26, 30
    # Stilts out of the bog, and a platform of dark wood on them.
    b.box(0, 0, 0, W, 0, D, "minecraft:mud")
    for x in range(1, W, 4):
        for z in range(1, D - 8, 4):
            b.box(x, 1, z, x, 3, z, log("dark_oak"))
    b.box(0, 4, 0, W, 4, D - 8, "minecraft:dark_oak_planks")
    # The manor at the back: black wood and deepslate, tall and narrow, lanterns in every window.
    b.room(4, 4, 1, 22, 13, 11, "minecraft:deepslate_bricks", floor="minecraft:dark_oak_planks")
    for x in (4, 22):
        for z in (1, 11):
            b.box(x, 5, z, x, 13, z, log("dark_oak"))
    b.gable(3, 0, 23, 12, 14, "minecraft:deepslate_tiles")
    b.tower(13, 6, 2, 22, "minecraft:polished_blackstone_bricks", "minecraft:deepslate_tiles", y=4, ladder_side=False)
    for x in range(6, 21, 3):
        b.set(x, 8, 11, pane("purple")); b.set(x, 11, 11, pane("purple"))
    b.door(13, 5, 11, h=3, w=1)
    b.box(5, 5, 2, 21, 12, 10, AIR)
    for x in range(6, 21, 3):
        b.set(x, 12, 9, HANG); b.set(x, 12, 4, HANG)
    b.chest(6, 5, 3, "lantern_house", "south")
    for x, z in ((8, 3), (18, 3), (20, 8)):
        b.set(x, 5, z, BARREL)
    for y in range(5, 12):
        b.scatter(5, 2, 21, 10, y, [COBWEB], 0.01, rnd)
    b.scatter(5, 2, 21, 10, 12, [COBWEB], 0.15, rnd)
    # The terrace in front, ringed with lantern posts: the fight is here.
    for x in range(0, W + 1, 3):
        for z in (12, D - 8):
            b.box(x, 5, z, x, 6, z, FENCE.format("dark_oak")); b.set(x, 7, z, rnd.choice([LANTERN, SOUL_LANTERN]))
    for z in range(15, D - 8, 3):
        for x in (0, W):
            b.box(x, 5, z, x, 6, z, FENCE.format("dark_oak")); b.set(x, 7, z, rnd.choice([LANTERN, SOUL_LANTERN]))
    # A pier running out into the bog, more lanterns along it: follow the lights.
    b.box(12, 4, D - 8, 14, 4, D, "minecraft:dark_oak_planks")
    for z in range(D - 7, D + 1, 3):
        b.box(12, 1, z, 12, 3, z, log("dark_oak")); b.box(14, 1, z, 14, 3, z, log("dark_oak"))
        b.set(12, 5, z, FENCE.format("dark_oak")); b.set(12, 6, z, LANTERN)
        b.set(14, 5, z, FENCE.format("dark_oak")); b.set(14, 6, z, LANTERN)
    for x, z in ((3, 16), (23, 19), (5, 20)):
        b.tree(x, 5, z, 5, "dark_oak", 1.6)
        b.set(x + 1, 9, z, HANG)   # under the leaves
    b.rogue(13, 5, 17, "corvina_fog_widow")
    b.crew("lantern_smuggler", ((7, 15), (19, 15), (9, 20), (17, 20)), y=5)


# ============================================================ Graves: Fort Iron Tide
@lair("fort_iron_tide", "Fort Iron Tide", "iron_tide_graves",
      ["#minecraft:is_beach", "minecraft:plains", "minecraft:savanna", "minecraft:stony_shore", "onepiece:east_blue", "onepiece:jaya"], "land")
def _(b):
    N = 30
    b.box(0, 0, 0, N, 0, N, "minecraft:stone_bricks")
    b.box(4, 0, 4, N - 4, 0, N - 4, "minecraft:polished_andesite")
    b.box(10, 0, 10, N - 10, 0, N - 10, "minecraft:smooth_stone")   # the parade ground: the fight is here
    # Curtain walls with a walkway and battlements.
    b.walls(0, 1, 0, N, 6, N, "minecraft:stone_bricks")
    b.walls(1, 1, 1, N - 1, 6, N - 1, "minecraft:stone_bricks")
    b.walls(1, 6, 1, N - 1, 6, N - 1, "minecraft:polished_andesite")
    for i in range(0, N + 1, 2):
        for (x, z) in ((i, 0), (i, N), (0, i), (N, i)):
            b.set(x, 7, z, "minecraft:stone_bricks")
    b.door(14, 1, 0, h=4, w=3); b.door(14, 1, 1, h=4, w=3)   # the gate
    b.box(13, 5, 0, 17, 5, 0, "minecraft:white_concrete")
    # Navy-white corner towers with blue roofs (blue terracotta reads as purple): the paint is peeling.
    for cx, cz in ((2, 2), (N - 2, 2), (2, N - 2), (N - 2, N - 2)):
        b.tower(cx, cz, 3, 11, "minecraft:white_concrete", "minecraft:blue_concrete")
        b.set(cx, 6, cz + (3 if cz < N // 2 else -3), "minecraft:cracked_stone_bricks")
    # Cannons on the walls, pointing out to sea.
    for x in range(6, N - 5, 6):
        b.set(x, 7, 1, "minecraft:dispenser[facing=north,triggered=false]")
        b.set(x, 7, N - 1, "minecraft:dispenser[facing=south,triggered=false]")
    # The commandant's office (Graves's) and the barracks.
    b.house(19, 20, 8, 7, 4, "minecraft:white_concrete", "minecraft:blue_concrete", floor="minecraft:spruce_planks", door="north")
    b.house(4, 20, 8, 7, 4, "minecraft:stone_bricks", "minecraft:gray_terracotta", door="north")
    for x in range(5, 11, 2):
        bed("blue", x, 1, 22, b)
    b.chest(24, 1, 24, "fort_iron_tide", "north")
    # The Navy's flag, with "Justice" torn out and his own mark sewn over it.
    for y in range(1, 15):
        b.set(15, y, 26, FENCE.format("dark_oak"))
    b.box(15, 10, 27, 15, 14, 27, "minecraft:white_wool")
    b.box(15, 10, 28, 15, 13, 29, "minecraft:white_wool")
    b.set(15, 12, 28, "minecraft:black_wool"); b.set(15, 11, 29, "minecraft:black_wool"); b.set(15, 13, 29, AIR)
    b.box(15, 14, 28, 15, 14, 30, "minecraft:gray_wool")
    for x, z in ((8, 8), (22, 8)):
        b.box(x, 1, z, x + 1, 1, z, "minecraft:blackstone"); b.set(x + 2, 1, z, "minecraft:anvil[facing=east]")   # spare cannon barrels
    b.rogue(15, 1, 15, "iron_tide_graves")
    b.crew("deserter_marine", ((10, 10), (20, 10), (10, 18), (20, 18), (15, 6)))


# ============================================================ Tsurugi: the Hollow Shrine
@lair("hollow_shrine", "The Hollow Shrine", "hollow_ronin_tsurugi",
      ["minecraft:cherry_grove", "minecraft:meadow", "minecraft:windswept_hills", "minecraft:taiga", "onepiece:wano"], "land")
def _(b):
    rnd = random.Random(4)
    b.box(0, 0, 0, 28, 0, 34, "minecraft:moss_block")
    b.box(10, 0, 0, 18, 0, 34, "minecraft:gravel")
    # The dueling ring: a stone circle with a white sand floor.
    b.disk(14, 0, 16, 10, "minecraft:stone_bricks")
    b.disk(14, 0, 16, 8.5, "minecraft:white_concrete_powder")
    b.disk(14, 0, 16, 1.2, "minecraft:chiseled_stone_bricks")
    for i in range(0, 360, 30):   # stone lanterns around it
        a = math.radians(i); x = round(14 + 10 * math.cos(a)); z = round(16 + 10 * math.sin(a))
        b.set(x, 1, z, WALL.format("stone_brick")); b.set(x, 2, z, SOUL_LANTERN)
    # A red torii at the entrance.
    for x in (10, 18):
        b.box(x, 1, 3, x, 8, 3, "minecraft:red_concrete")
    b.box(8, 9, 3, 20, 9, 3, "minecraft:black_concrete")
    b.box(9, 7, 3, 19, 7, 3, "minecraft:red_concrete")
    b.set(14, 8, 3, "minecraft:black_concrete")
    # The shrine behind the ring, cherry wood under a dark roof, its doors broken open.
    b.room(9, 0, 27, 19, 6, 33, "minecraft:cherry_planks", floor="minecraft:spruce_planks")
    for x in (9, 19):
        for z in (27, 33):
            b.box(x, 1, z, x, 6, z, log("dark_oak"))
    b.roof(7, 25, 21, 35, 7, "minecraft:deepslate_tiles", top="minecraft:deepslate_tiles")
    b.door(13, 1, 27, h=3, w=3)
    b.chest(14, 1, 32, "hollow_shrine", "north")
    b.set(12, 1, 32, CAMPFIRE.replace("campfire", "soul_campfire")); b.set(16, 1, 32, CAMPFIRE.replace("campfire", "soul_campfire"))
    # The swords of everyone who lost to him, stuck in the ground around the ring.
    for _ in range(26):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(10.8, 13)
        x = round(14 + r * math.cos(a)); z = round(16 + r * math.sin(a))
        if 0 < x < 28 and 0 < z < 26 and b.get(x, 1, z) is None:
            b.set(x, 1, z, "minecraft:lightning_rod[facing=up,powered=false,waterlogged=false]")
    for x, z in ((3, 6), (25, 8), (3, 26), (25, 24), (4, 15)):
        b.tree(x, 1, z, 5, "cherry", 2.6)
    b.rogue(14, 1, 16, "hollow_ronin_tsurugi")


# ============================================================ Gantz: the Shipbreakers' Foundry
@lair("shipbreakers_foundry", "The Shipbreakers' Foundry", "boilerheart_gantz",
      ["minecraft:stony_shore", "minecraft:badlands", "minecraft:desert", "minecraft:windswept_gravelly_hills", "onepiece:onigashima", "onepiece:punk_hazard_burning"], "land")
def _(b):
    rnd = random.Random(5)
    W, D = 36, 30
    b.box(0, 0, 0, W, 0, D, "minecraft:blackstone")
    b.scatter(0, 0, W, D, 0, ["minecraft:polished_blackstone", "minecraft:cracked_polished_blackstone_bricks", "minecraft:gravel"], 0.35, rnd, replace=True)
    # The furnace hall at the back: brick and iron, three smokestacks pouring smoke.
    b.room(4, 0, 18, 32, 9, 29, "minecraft:bricks", floor="minecraft:polished_blackstone")
    for x in range(4, 33, 4):
        b.box(x, 1, 18, x, 9, 18, "minecraft:iron_block")
    b.box(5, 1, 18, 31, 7, 18, AIR)   # open front so the forges glow out into the yard
    for x in range(8, 30, 6):
        b.box(x, 1, 25, x + 2, 3, 27, "minecraft:blast_furnace[facing=north,lit=true]")
        b.box(x, 0, 21, x + 2, 0, 22, "minecraft:magma_block")
    for cx in (9, 18, 27):
        b.cyl(cx, 24, 1.6, 10, 22, "minecraft:bricks", hollow=True)
        b.set(cx, 22, 24, CAMPFIRE)
    b.gable(3, 17, 33, 30, 10, "minecraft:iron_block")
    # The yard: a warship being torn apart, ribs showing.
    for x in range(4, 30, 3):
        for z in range(3, 13):
            if z in (3, 12) or (z in (4, 11) and x % 2 == 0):
                for y in range(1, 5 + (1 if z in (3, 12) else 0)):
                    b.set(x, y, z, log("dark_oak"))
        b.set(x, 1, 7, log("dark_oak", "x"))
    b.box(4, 1, 7, 30, 1, 8, log("spruce", "x"))   # keel
    for x, z in ((2, 15), (33, 3), (34, 14)):
        b.sphere(x, 1, z, 2, "minecraft:iron_block", ry=1.5, upper=True)
    for x, z, s in ((32, 16, "minecraft:anvil[facing=west]"), (3, 3, "minecraft:coal_block"), (3, 4, "minecraft:coal_block"),
                    (4, 3, "minecraft:coal_block"), (33, 10, "minecraft:smithing_table")):
        b.set(x, 1, z, s)
    b.chest(30, 1, 20, "shipbreakers_foundry", "south")
    b.rogue(18, 1, 14, "boilerheart_gantz")
    b.crew("boiler_stoker", ((10, 15), (26, 15), (14, 21), (22, 21)))


# ============================================================ Nereus: the Abyssal Temple
@lair("abyssal_temple", "The Abyssal Temple", "nereus_vane", OCEANS + DEEP, "sea")
def _(b):
    rnd = random.Random(6)
    C, R = 18, 13
    b.waterline = 9   # the platform rises out of the sea at y = 10
    # Pillars from the sea floor up, then a round altar-platform open to the sky.
    for i in range(0, 360, 30):
        a = math.radians(i); x = round(C + (R - 1) * math.cos(a)); z = round(C + (R - 1) * math.sin(a))
        b.box(x, -22, z, x + 1, 9, z + 1, "minecraft:prismarine_bricks")
    b.cyl(C, C, 3, -22, 9, "minecraft:dark_prismarine")
    b.disk(C, 10, C, R, "minecraft:prismarine_bricks")
    b.disk(C, 10, C, R - 2, "minecraft:dark_prismarine")
    b.disk(C, 10, C, 4, "minecraft:prismarine")
    b.set(C, 10, C, "minecraft:sea_lantern")
    # A ring of tall pillars, each crowned with light, and coral growing over everything.
    for i in range(15, 360, 30):
        a = math.radians(i); x = round(C + R * math.cos(a)); z = round(C + R * math.sin(a))
        h = 6 + (i // 30) % 3
        b.box(x, 11, z, x, 10 + h, z, "minecraft:prismarine_bricks")
        b.set(x, 11 + h, z, "minecraft:sea_lantern")
    corals = ["minecraft:tube_coral_block", "minecraft:brain_coral_block", "minecraft:fire_coral_block", "minecraft:horn_coral_block", "minecraft:bubble_coral_block"]
    for _ in range(40):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(R - 1, R + 2)
        b.set(round(C + r * math.cos(a)), rnd.randint(4, 9), round(C + r * math.sin(a)), rnd.choice(corals))
    # The shrine at the back: a half dome over the altar where he preaches, the conduit at its heart.
    b.sphere(C, 10, C + 9, 5, "minecraft:dark_prismarine", hollow=True, upper=True)
    b.box(C - 5, 11, C + 4, C + 5, 16, C + 8, AIR)
    b.box(C - 1, 11, C + 9, C + 1, 11, C + 11, "minecraft:prismarine_bricks")
    b.set(C, 12, C + 10, "minecraft:conduit[waterlogged=false]")
    b.chest(C + 2, 11, C + 10, "abyssal_temple", "north")
    b.rogue(C, 11, C, "nereus_vane")
    b.crew("abyssal_cultist", ((C - 6, C - 4), (C + 6, C - 4), (C - 6, C + 4), (C + 6, C + 4)), y=11)


# ============================================================ loot

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
    # The boss's own Rumor Poster, so you can call them out again for a rematch.
    return (1, 1, [item(f"opbosses:rumor_{boss}", 1)])


LOOT = {
    "scrapheap_reef": table((4, 7, [item(BERRY, 10, 4, 14), item("minecraft:iron_ingot", 10, 2, 6), item("minecraft:copper_ingot", 10, 4, 12),
                                    item("minecraft:iron_chain", 6, 1, 4), item("minecraft:gunpowder", 5, 1, 4), item("minecraft:golden_apple", 1),
                                    item("minecraft:compass", 2), item("minecraft:iron_axe", 3)]), rumor("saltjaw_rourke")),
    "lantern_house": table((4, 7, [item(BERRY, 10, 8, 20), item("minecraft:lantern", 8, 2, 6), item("minecraft:emerald", 6, 1, 4),
                                   item("minecraft:gold_ingot", 6, 1, 4), item("minecraft:potion", 4, 1, 2, {"type": "minecraft:set_potion", "id": "minecraft:invisibility"}),
                                   item("minecraft:ender_pearl", 3, 1, 2), item("minecraft:golden_apple", 2), item("minecraft:map", 3)]), rumor("corvina_fog_widow")),
    "fort_iron_tide": table((5, 8, [item(BERRY, 10, 10, 30), item("onepiece:seastone_ingot", 6, 1, 3), item("onepiece:seastone_cuffs", 3, 1, 1),
                                    item("minecraft:diamond", 5, 1, 3), item("minecraft:iron_ingot", 8, 2, 6), item("minecraft:gunpowder", 8, 2, 6),
                                    item("minecraft:golden_apple", 4, 1, 2), item("minecraft:diamond_sword", 2, 1, 1, ENCHANT)]), rumor("iron_tide_graves")),
    "hollow_shrine": table((5, 8, [item(BERRY, 10, 10, 30), item("minecraft:diamond_sword", 4, 1, 1, ENCHANT), item("minecraft:netherite_scrap", 3, 1, 1),
                                   item("minecraft:diamond", 5, 1, 3), item("minecraft:experience_bottle", 8, 2, 8), item("minecraft:cherry_sapling", 6, 1, 3),
                                   item("minecraft:golden_apple", 4, 1, 2)]), (1, 1, [item("minecraft:enchanted_book", 1, 1, 1, ENCHANT)]), rumor("hollow_ronin_tsurugi")),
    "shipbreakers_foundry": table((6, 10, [item(BERRY, 10, 24, 60), item("minecraft:iron_block", 6, 1, 3), item("minecraft:netherite_scrap", 4, 1, 2),
                                           item("minecraft:diamond", 6, 2, 5), item("minecraft:coal_block", 8, 2, 6), item("minecraft:netherite_ingot", 1),
                                           item("minecraft:enchanted_golden_apple", 1), item("minecraft:golden_apple", 5, 1, 3)]), rumor("boilerheart_gantz")),
    "abyssal_temple": table((6, 10, [item(BERRY, 10, 32, 64), item("minecraft:heart_of_the_sea", 3), item("minecraft:nautilus_shell", 6, 1, 4),
                                     item("minecraft:trident", 2, 1, 1, ENCHANT), item("minecraft:diamond", 6, 2, 6), item("minecraft:netherite_ingot", 2),
                                     item("minecraft:enchanted_golden_apple", 2), item("minecraft:totem_of_undying", 2), item("minecraft:prismarine_crystals", 6, 2, 8)]),
                            (2, 2, [item("minecraft:enchanted_book", 1, 1, 1, ENCHANT)]), rumor("nereus_vane")),
}

# One rogue lair per this many chunks on average (the main mod's hard lairs are 40 / 14).
SPACING, SEPARATION, SALT = 44, 16, 1408172101


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def main(root):
    D = os.path.join(root, 'src/main/resources/data/opbosses')
    for p in ('structure', 'worldgen/template_pool', 'worldgen/structure', 'worldgen/structure_set', 'tags/worldgen/biome/has_structure', 'loot_table/chests'):
        shutil.rmtree(f'{D}/{p}', ignore_errors=True)
    bosses = {b['id'] for b in json.load(open(os.path.join(root, 'src/main/resources/opbosses/bosses.json')))['bosses']}
    kits = {k['id'] for k in json.load(open(os.path.join(root, 'src/main/resources/opbosses/crews.json')))['kits']}
    rows = []
    for l in LAIRS:
        b = Lair()
        l['build'](b)
        for (eid, *_r, data) in b.entities:
            if eid == "opbosses:rogue_boss":
                assert data["Character"] in bosses, (l['name'], data["Character"])
            else:
                kit = [t for t in data["Tags"] if t.startswith(KIT_TAG_PREFIX)][0][len(KIT_TAG_PREFIX):]
                assert kit in kits, (l['name'], kit)
        name = l['name']
        size, my = b.save(f'{D}/structure/{name}.nbt')
        st = {"type": "minecraft:jigsaw", "biomes": f"#opbosses:has_structure/{name}", "step": "surface_structures",
              "spawn_overrides": {"monster": {"bounding_box": "piece", "spawns": []}, "ambient": {"bounding_box": "piece", "spawns": []}},
              "terrain_adaptation": "beard_thin", "start_pool": f"opbosses:{name}", "size": 1, "max_distance_from_center": 80, "use_expansion_hack": False}
        # The jigsaw puts a piece's lowest level 1 below surface + start_height (a single element's ground level delta is 1),
        # so start_height 0 puts y = 0 on the top block of the ground, or of the sea for a sea lair's waterline.
        if l['place'] == "land":
            st["project_start_to_heightmap"] = "WORLD_SURFACE_WG"; st["start_height"] = {"absolute": my}
        else:   # "sea": the waterline level sits at the sea's surface
            st["project_start_to_heightmap"] = "WORLD_SURFACE_WG"; st["start_height"] = {"absolute": -b.waterline + my}; st["terrain_adaptation"] = "none"
        write(f'{D}/worldgen/structure/{name}.json', st)
        write(f'{D}/worldgen/template_pool/{name}.json', {"fallback": "minecraft:empty", "elements": [{"weight": 1, "element": {
            "element_type": "minecraft:single_pool_element", "location": f"opbosses:{name}", "processors": {"processors": []}, "projection": "rigid"}}]})
        write(f'{D}/tags/worldgen/biome/has_structure/{name}.json', {"replace": False, "values": [
            v if v.startswith('#') or v.startswith('minecraft:') else {"id": v, "required": False} for v in l['biomes']]})
        write(f'{D}/loot_table/chests/{name}.json', LOOT[name])
        rows.append((name, l['title'], l['boss'], size, len(b.entities) - 1))
    write(f'{D}/worldgen/structure_set/rogue_lairs.json', {
        "structures": [{"structure": f"opbosses:{l['name']}", "weight": 1} for l in LAIRS],
        "placement": {"type": "minecraft:random_spread", "spacing": SPACING, "separation": SEPARATION, "salt": SALT}})
    for r in rows:
        print('%-22s %-28s boss %-22s size %-14s crew %d' % (r[0], r[1], r[2], r[3], r[4]))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')
