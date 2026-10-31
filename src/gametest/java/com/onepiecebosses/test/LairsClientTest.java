package com.onepiecebosses.test;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;

import com.mojang.datafixers.util.Pair;

import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.commands.PlaceCommand;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.AABB;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

import com.onepiecebosses.BossItems;
import com.onepiecebosses.boss.RogueBossEntity;
import com.onepiecemod.npc.HumanNpc;
import com.onepiecemod.world.GuardKit;
import com.onepiecemod.world.WorldFeature;

/**
 * In-world check of every rogue lair in a default world: /locate distance from spawn, then /place in a biome the lair
 * spawns in, the boss and crew it sets up, the chest's loot and a screenshot from above. Results are "LT" lines in the
 * log; anything wrong says FAIL. Screenshots go to build/run/clientGameTest/screenshots (lair_<name>.png).
 */
public class LairsClientTest implements FabricClientGameTest {
	private static final Logger LOG = LoggerFactory.getLogger("lairs-test");
	private static final List<String> FAILURES = new java.util.concurrent.CopyOnWriteArrayList<>();

	private record Lair(String name, String boss, String kit, int crew, boolean sea) {}

	private static final List<Lair> LAIRS = List.of(
			new Lair("scrapheap_reef", "saltjaw_rourke", "scrapdeck_raider", 3, true),
			new Lair("lantern_house", "corvina_fog_widow", "lantern_smuggler", 4, false),
			new Lair("fort_iron_tide", "iron_tide_graves", "deserter_marine", 5, false),
			new Lair("hollow_shrine", "hollow_ronin_tsurugi", "", 0, false),
			new Lair("shipbreakers_foundry", "boilerheart_gantz", "boiler_stoker", 4, false),
			new Lair("abyssal_temple", "nereus_vane", "abyssal_cultist", 4, true));

	@Override
	public void runTest(ClientGameTestContext context) {
		try {
			run(context);
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	private void run(ClientGameTestContext context) throws Exception {
		try (TestSingleplayerContext sp = context.worldBuilder().adjustSettings(LairsClientTest::defaultWorld).create()) {
			sp.getConnection().waitForChunksRender();
			cmd(sp, "race set @p human");
			cmd(sp, "gamemode spectator @a");
			cmd(sp, "time set noon");
			cmd(sp, "weather clear");
			context.waitTicks(10);
			context.setScreen(() -> null);
			context.runOnClient(client -> {
				try {
					Field visible = Class.forName("com.onepiecemod.questtree.client.QuestTreePanel").getDeclaredField("visible");
					visible.setAccessible(true);
					visible.set(null, false);
				} catch (ReflectiveOperationException e) {
					LOG.info("LT could not hide quest panel: {}", e.toString());
				}
				try {
					Field hidden = client.gui.getClass().getDeclaredField("isHidden");
					hidden.setAccessible(true);
					hidden.set(client.gui, true);
				} catch (ReflectiveOperationException e) {
					LOG.info("LT could not hide the HUD: {}", e.toString());
				}
			});

			server(sp, s -> {
				for (Lair lair : LAIRS) {
					locate(s, lair);
				}
			});

			List<BlockPos> used = new ArrayList<>();
			for (int i = 0; i < LAIRS.size(); i++) {
				lairTest(context, sp, LAIRS.get(i), i, used);
			}
			LOG.info("LT DONE, {} failures", FAILURES.size());
		}
		if (!FAILURES.isEmpty()) {
			throw new AssertionError("One Piece Bosses lair test failures:\n" + String.join("\n", FAILURES));
		}
	}

	/** A normal world (the test default is superflat with no structures), so /locate means something. */
	private static void defaultWorld(WorldCreationUiState creator) {
		creator.setWorldType(new WorldCreationUiState.WorldTypeEntry(
				creator.getSettings().worldgenLoadContext().lookupOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.NORMAL)));
		creator.setGenerateStructures(true);
		creator.setAllowCommands(true);
		creator.setSeed("rogue-lairs");
	}

	private static void check(boolean ok, String what) {
		if (!ok) {
			LOG.info("LT FAIL {}", what);
			FAILURES.add(what);
		}
	}

	private static Holder.Reference<Structure> structure(MinecraftServer s, String name) {
		return s.registryAccess().lookupOrThrow(Registries.STRUCTURE)
				.getOrThrow(ResourceKey.create(Registries.STRUCTURE, Identifier.fromNamespaceAndPath("opbosses", name)));
	}

	/** What /locate structure does, from the world's centre. */
	private static void locate(MinecraftServer s, Lair lair) {
		ServerLevel level = s.overworld();
		BlockPos from = new BlockPos(0, 64, 0);
		long start = System.currentTimeMillis();
		Pair<BlockPos, Holder<Structure>> found = level.getChunkSource().getGenerator()
				.findNearestMapStructure(level, HolderSet.direct(structure(s, lair.name)), from, 100, false);
		long ms = System.currentTimeMillis() - start;
		if (found == null) {
			LOG.info("LT LOCATE {} not found within 100 regions ({} ms)", lair.name, ms);
		} else {
			BlockPos p = found.getFirst();
			LOG.info("LT LOCATE {} at {} {} distance {} ({} ms)", lair.name, p.getX(), p.getZ(),
					(int) Math.sqrt(p.distSqr(new BlockPos(0, p.getY(), 0))), ms);
		}
	}

	private void lairTest(ClientGameTestContext context, TestSingleplayerContext sp, Lair lair, int i, List<BlockPos> used) throws Exception {
		BlockPos[] target = new BlockPos[1];
		server(sp, s -> {
			ServerLevel level = s.overworld();
			TagKey<Biome> tag = TagKey.create(Registries.BIOME, Identifier.fromNamespaceAndPath("opbosses", "has_structure/" + lair.name));
			// Start each search somewhere else, and skip spots within 200 blocks of an earlier lair.
			for (int tries = 0; tries < 8 && target[0] == null; tries++) {
				BlockPos from = new BlockPos(600 * i + 300 * tries, level.getSeaLevel(), -400 * tries);
				Pair<BlockPos, Holder<Biome>> biome = level.findClosestBiome3d(h -> h.is(tag), from, 4000, 32, 64);
				if (biome == null) {
					continue;
				}
				BlockPos p = biome.getFirst();
				if (used.stream().noneMatch(u -> u.distSqr(p) < 200 * 200)) {
					target[0] = p;
					LOG.info("LT {} placing in {} at {} {}", lair.name, biome.getSecond().getRegisteredName(), p.getX(), p.getZ());
				}
			}
		});
		if (target[0] == null) {
			check(false, lair.name + ": no biome it spawns in within 4000 blocks");
			return;
		}
		BlockPos pos = target[0];
		used.add(pos);
		// /place needs the chunks loaded, so go there first.
		server(sp, s -> player(s).teleportTo(s.overworld(), pos.getX() + 0.5, 140, pos.getZ() + 0.5, Set.of(), 0f, 60f, true));
		context.waitTicks(40);
		sp.getConnection().waitForChunksRender();

		server(sp, s -> {
			try {
				PlaceCommand.placeStructure(s.createCommandSourceStack().withSuppressedOutput(), structure(s, lair.name), pos);
				LOG.info("LT {} placed ok", lair.name);
			} catch (Exception e) {
				check(false, lair.name + ": /place structure failed: " + e.getMessage());
			}
		});
		context.waitTicks(40);

		double[] camera = new double[5];
		server(sp, s -> {
			ServerLevel level = s.overworld();
			AABB area = new AABB(pos).inflate(64, 80, 64);
			List<RogueBossEntity> bosses = level.getEntitiesOfClass(RogueBossEntity.class, area, Entity::isAlive);
			check(bosses.size() == 1, lair.name + ": " + bosses.size() + " rogue bosses nearby");
			if (bosses.isEmpty()) {
				return;
			}
			RogueBossEntity boss = bosses.get(0);
			boolean setUp = !boss.entityTags().contains(WorldFeature.NEW_CHARACTER_TAG);
			int sea = level.getSeaLevel();
			String inBlock = blockedBy(level, boss);
			LOG.info("LT {} boss id={} name='{}' boss={} setUp={} health={}/{} at {} (sea level {}, {} above it) stuckIn={}", lair.name,
					boss.getCharacterId(), boss.getData() == null ? "?" : boss.getData().name, boss.isBoss(), setUp, boss.getHealth(),
					boss.getMaxHealth(), boss.blockPosition(), sea, boss.getBlockY() - sea, inBlock);
			check(boss.getCharacterId().equals(lair.boss), lair.name + ": boss is " + boss.getCharacterId() + ", not " + lair.boss);
			check(setUp && boss.isBoss(), lair.name + ": the boss wasn't set up (setUp=" + setUp + ", boss=" + boss.isBoss() + ")");
			check(inBlock == null, lair.name + ": the boss is stuck in " + inBlock);
			if (lair.sea) {
				check(boss.getBlockY() > sea && boss.getBlockY() < sea + 6, lair.name + ": the arena is " + (boss.getBlockY() - sea) + " blocks above the sea");
			}

			List<HumanNpc> crew = level.getEntitiesOfClass(HumanNpc.class, area, Entity::isAlive);
			int kitted = 0;
			for (HumanNpc npc : crew) {
				boolean leftover = npc.entityTags().stream().anyMatch(t -> t.equals(GuardKit.GUARD_TAG) || t.startsWith(GuardKit.KIT_TAG_PREFIX));
				LOG.info("LT {} crew {} kit={} name='{}' hand={} tagsLeft={} at {} stuckIn={}", lair.name, BuiltInRegistries.ENTITY_TYPE.getKey(npc.getType()),
						npc.getKitId(), npc.getName().getString(), npc.getMainHandItem(), leftover, npc.blockPosition(), blockedBy(level, npc));
				if (npc.getKitId().equals(lair.kit) && !leftover) {
					kitted++;
				}
			}
			check(kitted == lair.crew, lair.name + ": " + kitted + " crew with kit " + lair.kit + ", want " + lair.crew);

			int chests = 0;
			String rumor = BossItems.RUMORS.get(lair.boss) == null ? "?" : new ItemStack(BossItems.RUMORS.get(lair.boss)).getItem().toString();
			for (int cx = (pos.getX() >> 4) - 4; cx <= (pos.getX() >> 4) + 4; cx++) {
				for (int cz = (pos.getZ() >> 4) - 4; cz <= (pos.getZ() >> 4) + 4; cz++) {
					for (BlockPos bp : level.getChunk(cx, cz).getBlockEntitiesPos()) {
						BlockEntity be = level.getBlockEntity(bp);
						if (!(be instanceof ChestBlockEntity chest) || chest.getLootTable() == null) {
							continue;
						}
						String table = chest.getLootTable().identifier().toString();
						check(table.equals("opbosses:chests/" + lair.name), lair.name + ": chest at " + bp + " has loot table " + table);
						chest.unpackLootTable(player(s));
						List<String> items = new ArrayList<>();
						boolean poster = false;
						for (int slot = 0; slot < chest.getContainerSize(); slot++) {
							ItemStack stack = chest.getItem(slot);
							if (!stack.isEmpty()) {
								items.add(stack.getCount() + " " + stack.getItem());
								poster |= stack.is(BossItems.RUMORS.get(lair.boss));
							}
						}
						chests++;
						LOG.info("LT {} chest at {} ({} above the boss) items={}", lair.name, bp, bp.getY() - boss.getBlockY(), items);
						check(!items.isEmpty(), lair.name + ": the chest is empty");
						check(poster, lair.name + ": no " + rumor + " in the chest");
					}
				}
			}
			check(chests == 1, lair.name + ": " + chests + " loot chests");

			// High up, angled down at the arena, from the south-east.
			double dist = 26 + boss.getBbHeight() * 2;
			camera[0] = boss.getX() + dist * 0.75;
			camera[1] = boss.getY() + dist * 0.8;
			camera[2] = boss.getZ() + dist * 0.75;
			camera[3] = (float) Math.toDegrees(Math.atan2(-(boss.getX() - camera[0]), boss.getZ() - camera[2]));
			camera[4] = (float) Math.toDegrees(Math.atan2(camera[1] - boss.getY(), Math.hypot(camera[0] - boss.getX(), camera[2] - boss.getZ())));
			boss.setNoAi(true);
			for (HumanNpc npc : crew) {
				npc.setNoAi(true);
			}
		});
		if (camera[1] != 0) {
			server(sp, s -> player(s).teleportTo(s.overworld(), camera[0], camera[1], camera[2], Set.of(), (float) camera[3], (float) camera[4], true));
			context.waitTicks(30);
			sp.getConnection().waitForChunksRender();
			context.waitTicks(10);
			context.takeScreenshot("lair_" + lair.name);
		}
	}

	/** The first solid block inside the entity's box, or null if it's standing free. */
	private static String blockedBy(ServerLevel level, Entity e) {
		AABB box = e.getBoundingBox().deflate(0.05);
		for (BlockPos p : BlockPos.betweenClosed(BlockPos.containing(box.minX, box.minY, box.minZ), BlockPos.containing(box.maxX, box.maxY, box.maxZ))) {
			var state = level.getBlockState(p);
			if (!state.getCollisionShape(level, p).isEmpty() && state.getCollisionShape(level, p).bounds().move(p).intersects(box)) {
				return state.getBlock() + " at " + p.immutable();
			}
		}
		return null;
	}

	private static ServerPlayer player(MinecraftServer server) {
		return server.getPlayerList().getPlayers().get(0);
	}

	private static void cmd(TestSingleplayerContext sp, String command) {
		sp.getServer().runCommand(command);
	}

	private static void server(TestSingleplayerContext sp, Consumer<MinecraftServer> action) throws Exception {
		sp.getServer().runOnServer(action::accept);
	}
}
