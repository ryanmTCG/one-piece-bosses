package com.onepiecebosses.test;

import java.lang.reflect.Field;
import java.util.Collection;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;

import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

import com.onepiecebosses.BossItems;
import com.onepiecebosses.boss.RogueBossEntity;
import com.onepiecebosses.boss.RogueData;
import com.onepiecebosses.boss.RogueSignatures;
import com.onepiecemod.bounty.Bounty;
import com.onepiecemod.character.BossStrikes;
import com.onepiecemod.npc.HumanNpc;
import com.onepiecemod.npc.NpcFeature;
import com.onepiecemod.npc.NpcKit;
import com.onepiecemod.npc.NpcSkins;

/**
 * In-world check of every rogue boss: Rumor Poster spawn, crew, phase lines, signature moves, trophy, bounty,
 * the Hard rematch and Rumor Poster drops. Results are "BT" lines in the log; anything wrong says FAIL or MISSING.
 * Screenshots go to build/run/clientGameTest/screenshots.
 */
public class BossesClientTest implements FabricClientGameTest {
	private static final Logger LOG = LoggerFactory.getLogger("bosses-test");
	private static final double PX = 0.5, PY = 100, PZ = 0.5;
	private static final BlockPos POSTER_BLOCK = new BlockPos(3, 99, 0);
	/** Everything that went wrong. The test fails at the end if this isn't empty. */
	private static final List<String> FAILURES = new java.util.concurrent.CopyOnWriteArrayList<>();

	@Override
	public void runTest(ClientGameTestContext context) {
		try {
			run(context);
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	private void run(ClientGameTestContext context) throws Exception {
		try (TestSingleplayerContext sp = context.worldBuilder().create()) {
			sp.getConnection().waitForChunksRender();
			cmd(sp, "gamemode survival @a");
			cmd(sp, "time set day");
			cmd(sp, "weather clear");
			cmd(sp, "race set @p human");
			cmd(sp, "gamerule spawn_mobs false");
			cmd(sp, "gamerule advance_time false");
			context.waitTicks(10);
			context.setScreen(() -> null);
			context.runOnClient(client -> {
				try {
					Class<?> panel = Class.forName("com.onepiecemod.questtree.client.QuestTreePanel");
					Field visible = panel.getDeclaredField("visible");
					visible.setAccessible(true);
					visible.set(null, false);
				} catch (ReflectiveOperationException e) {
					LOG.info("BT could not hide quest panel: {}", e.toString());
				}
			});
			server(sp, s -> {
				arena(s.overworld());
				ServerPlayer p = player(s);
				p.teleportTo(s.overworld(), PX, PY, PZ, Set.of(), -90f, 10f, true);
				p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 20 * 1200, 4, false, false));
				p.addEffect(new MobEffectInstance(MobEffects.SATURATION, 20 * 1200, 4, false, false));
				p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 20 * 1200, 4, false, false));
				checkData();
			});
			context.waitTicks(20);
			context.setScreen(() -> null);

			for (String id : RogueData.all().keySet()) {
				bossTest(context, sp, id);
			}
			rumorDropTest(sp);
			LOG.info("BT DONE, {} failures", FAILURES.size());
		}
		if (!FAILURES.isEmpty()) {
			throw new AssertionError("One Piece Bosses test failures:\n" + String.join("\n", FAILURES));
		}
	}

	private static void check(boolean ok, String what) {
		if (!ok) {
			LOG.info("BT FAIL {}", what);
			FAILURES.add(what);
		}
	}

	/** Every crew kit, rumor kit and skin group the JSON names must exist in the main mod. */
	private static void checkData() {
		for (RogueData boss : RogueData.all().values()) {
			if (!boss.crew.isEmpty()) {
				NpcKit kit = NpcKit.get(boss.crew);
				check(kit != null, boss.id + ": crew kit " + boss.crew + " is missing");
				if (kit != null) {
					for (String skin : kit.skins) {
						if (!NpcSkins.COUNT.containsKey(skin)) {
							check(false, boss.id + ": crew " + boss.crew + " uses missing skin group " + skin);
						}
					}
				}
			}
			for (String kit : boss.rumorFrom) {
				if (NpcKit.get(kit) == null) {
					check(false, boss.id + ": rumorFrom kit " + kit + " is missing");
				}
			}
			check(BossItems.TROPHIES.containsKey(boss.trophy), boss.id + ": trophy " + boss.trophy + " is not registered");
		}
	}

	private void bossTest(ClientGameTestContext context, TestSingleplayerContext sp, String id) throws Exception {
		server(sp, s -> {
			clearMobs(s);
			arena(s.overworld());
			ServerPlayer p = player(s);
			p.teleportTo(s.overworld(), PX, PY, PZ, Set.of(), -90f, 10f, true);
			p.setHealth(p.getMaxHealth());
			p.getInventory().clearContent();
			p.getInventory().setSelectedSlot(0);
			p.getInventory().setItem(0, new ItemStack(BossItems.RUMORS.get(id)));
		});
		clearChat(context);
		context.waitTicks(5);
		// Use the Rumor Poster on the block in front, like a player would.
		context.getInput().lookAt(POSTER_BLOCK);
		context.waitTicks(3);
		context.getInput().pressKey(o -> o.keyUse);
		context.waitTicks(10);

		server(sp, s -> {
			RogueBossEntity boss = boss(s);
			if (boss == null) {
				check(false, id + ": no boss spawned from the Rumor Poster");
				return;
			}
			LOG.info("BT {} spawned id={} name='{}' boss={} difficulty={} health={}/{} scale={} posterLeft={}", id, boss.getCharacterId(),
					boss.getData().name, boss.isBoss(), boss.getDifficulty(), boss.getHealth(), boss.getMaxHealth(), boss.getScale(),
					player(s).getInventory().getItem(0).getCount());
			RogueData data = RogueData.get(id);
			check(boss.getCharacterId().equals(id), id + ": spawned as " + boss.getCharacterId());
			check(boss.isBoss() && boss.getDifficulty() == 0, id + ": first fight should be a Normal boss");
			check(boss.getMaxHealth() == Math.min(1024f, data.character.health), id + ": max health " + boss.getMaxHealth());
			check(!player(s).getInventory().contains(new ItemStack(BossItems.RUMORS.get(id))), id + ": the poster wasn't used up (slot 0: " + player(s).getInventory().getItem(0) + ")");
			boss.setTarget(player(s));
		});
		context.waitTicks(40);
		server(sp, s -> {
			int crew = crewCount(s);
			LOG.info("BT {} after intro: crew={}", id, crew);
			check(RogueData.get(id).crew.isEmpty() ? crew == 0 : crew > 0, id + ": " + crew + " crew after the intro");
		});
		context.takeScreenshot("boss_" + id + "_intro");

		// Phase 2 (below 66%) and phase 3 (below 33%).
		server(sp, s -> {
			RogueBossEntity boss = boss(s);
			if (boss != null) {
				boss.setHealth(boss.getMaxHealth() * 0.6f);
				boss.setTarget(player(s));
			}
		});
		context.waitTicks(20);
		server(sp, s -> {
			int crew = crewCount(s);
			LOG.info("BT {} phase 2: crew={}", id, crew);
			check(RogueData.get(id).crew.isEmpty() ? crew == 0 : crew > 2, id + ": " + crew + " crew after phase 2 (no second wave)");
		});
		server(sp, s -> {
			RogueBossEntity boss = boss(s);
			if (boss != null) {
				boss.setHealth(boss.getMaxHealth() * 0.3f);
				boss.setTarget(player(s));
			}
		});
		// The first signature comes 40 ticks into phase 3.
		context.waitTicks(70);
		context.takeScreenshot("boss_" + id + "_phase3");
		server(sp, s -> {
			RogueBossEntity boss = boss(s);
			if (boss == null) {
				return;
			}
			// Run the signature directly too, so an exception shows up here instead of crashing the tick.
			try {
				RogueSignatures.use(boss.rogue().signature, boss, player(s), s.overworld(), new BossStrikes(), 5f, 0);
				LOG.info("BT {} signature {} ran ok, playerHealth={}", id, boss.rogue().signature, player(s).getHealth());
			} catch (Exception e) {
				LOG.info("BT {} signature {} threw", id, boss.rogue().signature, e);
				check(false, id + ": signature " + boss.rogue().signature + " threw " + e);
			}
		});
		context.waitTicks(40);
		logChat(context, "BT " + id);

		// A first win: trophy drop and bounty.
		server(sp, s -> {
			RogueBossEntity boss = boss(s);
			if (boss == null) {
				check(false, id + ": the boss is gone before the kill");
				return;
			}
			ServerPlayer p = player(s);
			// Rourke is killed from 60 blocks away: the killer still gets the whole bounty.
			if (!id.equals("saltjaw_rourke")) {
				p.teleportTo(s.overworld(), boss.getX() + 1.5, boss.getY(), boss.getZ(), Set.of(), 90f, 10f, true);
			} else {
				p.teleportTo(s.overworld(), boss.getX() + 60, 100, boss.getZ(), Set.of(), 90f, 10f, true);
			}
			long before = Bounty.get(p);
			LOG.info("BT {} at kill: player {} boss {} distance {}", id, p.blockPosition(), boss.blockPosition(), p.distanceTo(boss));
			boss.hurtServer(s.overworld(), p.damageSources().playerAttack(p), 100_000);
			LOG.info("BT {} killed dead={} firstWin={} bounty +{} (want {})", id, boss.isDeadOrDying(), boss.isFirstWin(),
					Bounty.get(p) - before, boss.rogue().bountyReward);
			check(boss.isDeadOrDying() && boss.isFirstWin(), id + ": didn't die as a first win");
			check(Bounty.get(p) - before == boss.rogue().bountyReward,
					id + ": bounty rose by " + (Bounty.get(p) - before) + ", not " + boss.rogue().bountyReward);
		});
		context.waitTicks(30);
		server(sp, s -> {
			List<ItemEntity> drops = s.overworld().getEntitiesOfClass(ItemEntity.class, area());
			net.minecraft.world.item.Item trophyItem = BossItems.TROPHIES.get(RogueData.get(id).trophy);
			boolean trophy = drops.stream().anyMatch(e -> e.getItem().is(trophyItem)) || player(s).getInventory().contains(new ItemStack(trophyItem));
			LOG.info("BT {} trophy dropped={} drops={} crewLeft={}", id, trophy,
					drops.stream().map(e -> e.getItem().toString()).toList(), crewCount(s));
			check(trophy, id + ": no trophy");
			check(crewCount(s) == 0, id + ": the crew didn't scatter");

			// The poster brings the boss back on Hard now.
			ServerPlayer p = player(s);
			for (ItemEntity drop : drops) {
				drop.discard();
			}
			p.teleportTo(s.overworld(), PX, PY, PZ, Set.of(), -90f, 10f, true);
			p.getInventory().setItem(0, new ItemStack(BossItems.RUMORS.get(id)));
		});
		context.waitTicks(10);
		context.getInput().lookAt(POSTER_BLOCK);
		context.waitTicks(3);
		context.getInput().pressKey(o -> o.keyUse);
		context.waitTicks(10);
		server(sp, s -> {
			RogueBossEntity boss = boss(s);
			LOG.info("BT {} rematch difficulty={} health={}", id, boss == null ? "none" : boss.getDifficulty(),
					boss == null ? 0 : boss.getMaxHealth());
			check(boss != null && boss.getDifficulty() == 1, id + ": the poster didn't bring the boss back on Hard");
		});
	}

	/** Kills lots of main mod NPCs whose kit is in a boss's rumorFrom and counts the posters. */
	private static void rumorDropTest(TestSingleplayerContext sp) throws Exception {
		server(sp, s -> {
			clearMobs(s);
			ServerLevel level = s.overworld();
			ServerPlayer p = player(s);
			int killed = 0;
			for (int i = 0; i < 200; i++) {
				HumanNpc npc = NpcFeature.spawn(level, "pirate", BlockPos.containing(PX + 3, PY, PZ), 0f);
				if (npc == null) {
					continue;
				}
				npc.hurtServer(level, p.damageSources().playerAttack(p), 100_000);
				killed++;
			}
			long posters = level.getEntitiesOfClass(ItemEntity.class, area()).stream()
					.filter(e -> BossItems.RUMORS.containsValue(e.getItem().getItem())).count();
			LOG.info("BT RUMOR killed {} pirates, rumor posters dropped={}", killed, posters);
			check(killed == 200 && posters > 0, "no Rumor Posters from " + killed + " pirates");
		});
	}

	private static RogueBossEntity boss(MinecraftServer s) {
		List<RogueBossEntity> bosses = s.overworld().getEntitiesOfClass(RogueBossEntity.class, area(), Entity::isAlive);
		return bosses.isEmpty() ? null : bosses.get(0);
	}

	private static int crewCount(MinecraftServer s) {
		return s.overworld().getEntitiesOfClass(HumanNpc.class, area(), e -> e.isAlive() && e.entityTags().contains(BossStrikes.MINION_TAG)).size();
	}

	private static AABB area() {
		return new AABB(PX, PY, PZ, PX, PY, PZ).inflate(40);
	}

	private static void arena(ServerLevel level) {
		for (int x = -12; x <= 16; x++) {
			for (int z = -12; z <= 12; z++) {
				level.setBlockAndUpdate(new BlockPos(x, 99, z), Blocks.STONE.defaultBlockState());
				// Barrier walls, so a boss can't knock the player off the platform (out of its boss bar).
				boolean edge = x == -12 || x == 16 || z == -12 || z == 12;
				for (int y = 100; y < 124; y++) {
					level.setBlockAndUpdate(new BlockPos(x, y, z), edge ? Blocks.BARRIER.defaultBlockState() : Blocks.AIR.defaultBlockState());
				}
			}
		}
	}

	private static void clearMobs(MinecraftServer s) {
		for (Entity e : s.overworld().getEntitiesOfClass(Entity.class, area().inflate(10), e -> !(e instanceof Player))) {
			e.discard();
		}
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

	private static void clearChat(ClientGameTestContext context) throws Exception {
		context.runOnClient(client -> client.gui.hud.getChat().clearMessages(true));
	}

	private static void logChat(ClientGameTestContext context, String tag) throws Exception {
		context.runOnClient(client -> {
			Object chat = client.gui.hud.getChat();
			for (Field f : chat.getClass().getDeclaredFields()) {
				if (Collection.class.isAssignableFrom(f.getType())) {
					f.setAccessible(true);
					Collection<?> list = (Collection<?>) f.get(chat);
					if (f.getName().toLowerCase().contains("trimmed") || list.isEmpty()) {
						continue;
					}
					for (Object o : list) {
						LOG.info("{} CHAT {}", tag, o);
					}
				}
			}
		});
	}
}
