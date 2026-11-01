package com.onepiecebosses.test;

import java.lang.reflect.Field;
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
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.AABB;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

import com.onepiecebosses.compat.OnePieceBridge;
import com.onepiecebosses.world.PirateRaids;
import com.onepiecebosses.world.RookieRaiderEntity;
import com.onepiecebosses.world.WanderingHunterEntity;
import com.onepiecebosses.world.WanderingHunters;
import com.onepiecebosses.world.WorldMobs;
import com.onepiecemod.bounty.Bounty;
import com.onepiecemod.npc.HumanNpc;
import com.onepiecemod.npc.NpcFeature;
import com.onepiecemod.npc.NpcKit;
import com.onepiecemod.npc.NpcSkins;

/**
 * In-world check of the world mobs on the flat test world: bounty hunters come for a small bounty, leave a big one
 * alone and fight pirates; beating one raises your bounty; a rookie crew raids a village, the boss bar and the reward
 * for beating it, and the raiders leaving when nobody defends. Results are "WM" lines in the log; anything wrong says
 * FAIL. Run it alone with `gradlew runClientGameTest -Dopbosses.tests=mobs`.
 */
public class WorldMobsClientTest implements FabricClientGameTest {
	private static final Logger LOG = LoggerFactory.getLogger("world-mobs-test");
	private static final List<String> FAILURES = new java.util.concurrent.CopyOnWriteArrayList<>();
	/** Standing on the superflat grass. */
	private static final BlockPos HOME = new BlockPos(0, -60, 0);

	@Override
	public void runTest(ClientGameTestContext context) {
		if (!TestFilter.runs("mobs")) {
			return;
		}
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
			cmd(sp, "difficulty normal");
			context.waitTicks(10);
			context.setScreen(() -> null);
			context.runOnClient(client -> {
				try {
					Field visible = Class.forName("com.onepiecemod.questtree.client.QuestTreePanel").getDeclaredField("visible");
					visible.setAccessible(true);
					visible.set(null, false);
				} catch (ReflectiveOperationException e) {
					LOG.info("WM could not hide quest panel: {}", e.toString());
				}
			});
			server(sp, s -> {
				ServerPlayer p = player(s);
				p.teleportTo(s.overworld(), HOME.getX() + 0.5, HOME.getY(), HOME.getZ() + 0.5, Set.of(), 0f, 10f, true);
				p.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 20 * 1200, 4, false, false));
				p.addEffect(new MobEffectInstance(MobEffects.SATURATION, 20 * 1200, 4, false, false));
				p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 20 * 1200, 4, false, false));
				checkKits();
			});
			context.waitTicks(20);

			if (TestFilter.picks("hunters")) {
				huntTest(context, sp);
				bigGameTest(context, sp);
			}
			if (TestFilter.picks("raids")) {
				raidTest(context, sp);
				retreatTest(context, sp);
			}
			LOG.info("WM DONE, {} failures", FAILURES.size());
		}
		if (!FAILURES.isEmpty()) {
			throw new AssertionError("One Piece Bosses world mob test failures:\n" + String.join("\n", FAILURES));
		}
	}

	private static void checkKits() {
		for (String id : List.of(WanderingHunters.KIT, WanderingHunters.VETERAN_KIT, PirateRaids.KIT, PirateRaids.CAPTAIN_KIT)) {
			NpcKit kit = NpcKit.get(id);
			check(kit != null, "kit " + id + " is missing");
			if (kit != null) {
				for (String skin : kit.skins) {
					check(NpcSkins.COUNT.containsKey(skin), "kit " + id + " uses missing skin group " + skin);
				}
			}
		}
	}

	/** 10M bounty: hunters come for you, call you out, and beating one raises your bounty. */
	private static void huntTest(ClientGameTestContext context, TestSingleplayerContext sp) throws Exception {
		server(sp, s -> {
			clearMobs(s);
			Bounty.set(player(s), 10_000_000L);
			int sent = WanderingHunters.sendHunt(player(s));
			LOG.info("WM HUNT sent {}", sent);
			check(sent > 0, "no hunters came for a 10M bounty");
		});
		context.waitTicks(100);
		context.takeScreenshot("world_mobs_hunters");
		server(sp, s -> {
			ServerPlayer p = player(s);
			List<WanderingHunterEntity> hunters = hunters(s);
			long onPlayer = hunters.stream().filter(h -> h.getTarget() == p).count();
			double closest = hunters.stream().mapToDouble(h -> h.distanceTo(p)).min().orElse(-1);
			LOG.info("WM HUNT {} hunters, {} on the player, closest {}", hunters.size(), onPlayer, String.format("%.1f", closest));
			check(onPlayer > 0, "hunters aren't after a 10M player");
			check(closest >= 0 && closest < 18, "hunters didn't close in (closest " + closest + ")");
			long before = Bounty.get(p);
			for (WanderingHunterEntity h : hunters) {
				h.hurtServer(s.overworld(), p.damageSources().playerAttack(p), 100_000);
			}
			long after = Bounty.get(p);
			LOG.info("WM HUNT bounty {} -> {}", before, after);
			check(after > before, "beating hunters didn't raise the bounty");
		});
	}

	/** 200M bounty: out of their league. No hunt, a hunter right next to you ignores you and fights a pirate instead. */
	private static void bigGameTest(ClientGameTestContext context, TestSingleplayerContext sp) throws Exception {
		server(sp, s -> {
			clearMobs(s);
			ServerPlayer p = player(s);
			Bounty.set(p, 200_000_000L);
			check(WanderingHunters.sendHunt(p) == 0, "hunters came for a 200M bounty");
			check(spawn(s, WorldMobs.WANDERING_HUNTER, HOME.offset(4, 0, 0), WanderingHunters.KIT) != null, "couldn't place a hunter");
		});
		context.waitTicks(60);
		server(sp, s -> {
			ServerPlayer p = player(s);
			WanderingHunterEntity h = hunters(s).isEmpty() ? null : hunters(s).get(0);
			check(h != null && h.getTarget() != p, "a hunter went after a 200M player");
			NpcFeature.spawn(s.overworld(), "pirate", HOME.offset(10, 0, 0), 0f);
		});
		context.waitTicks(100);
		server(sp, s -> {
			WanderingHunterEntity h = hunters(s).isEmpty() ? null : hunters(s).get(0);
			Entity target = h != null ? h.getTarget() : null;
			List<HumanNpc> pirates = s.overworld().getEntitiesOfClass(HumanNpc.class, area(), e -> "pirate".equals(e.getKitId()));
			boolean fought = (target instanceof HumanNpc npc && "pirate".equals(npc.getKitId()))
					|| pirates.isEmpty() || pirates.get(0).getHealth() < pirates.get(0).getMaxHealth();
			LOG.info("WM BIG hunter target {}, pirates left {}", target == null ? "none" : target.getName().getString(), pirates.size());
			check(fought, "the hunter didn't go after a pirate");
			Bounty.set(player(s), 0);
		});
	}

	/** A crew raids a village of five villagers; beating them pays out and gives Hero of the Village. */
	private static void raidTest(ClientGameTestContext context, TestSingleplayerContext sp) throws Exception {
		server(sp, s -> {
			clearMobs(s);
			villagers(s);
			ServerPlayer p = player(s);
			check(PirateRaids.start(p) != null, "no raid started in a village");
			check(PirateRaids.start(p) == null, "a second raid started on the same village");
			List<RookieRaiderEntity> raiders = raiders(s);
			LOG.info("WM RAID {} raiders: {}", raiders.size(), raiders.stream().map(r -> r.getName().getString()).toList());
			check(raiders.size() >= 3, "only " + raiders.size() + " raiders");
			check(PirateRaids.isDefending(p), "the player isn't counted as defending");
		});
		context.waitTicks(160);
		context.takeScreenshot("world_mobs_raid");
		server(sp, s -> {
			ServerPlayer p = player(s);
			List<RookieRaiderEntity> raiders = raiders(s);
			long fighting = raiders.stream().filter(r -> r.getTarget() != null).count();
			double closest = raiders.stream().mapToDouble(r -> Math.sqrt(r.distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(r.getRaidTarget())))).min().orElse(-1);
			LOG.info("WM RAID {} raiders fighting, closest to the village {}", fighting, String.format("%.1f", closest));
			check(fighting > 0 || (closest >= 0 && closest < 20), "the raiders neither fought nor marched on the village");
			int berriesBefore = p.getInventory().countItem(OnePieceBridge.berries(1).getItem());
			for (RookieRaiderEntity r : raiders) {
				r.hurtServer(s.overworld(), p.damageSources().playerAttack(p), 100_000);
			}
			LOG.info("WM RAID berries before {}", berriesBefore);
		});
		context.waitTicks(40);
		server(sp, s -> {
			ServerPlayer p = player(s);
			check(!PirateRaids.isDefending(p), "the raid didn't end when every raider was beaten");
			check(p.hasEffect(MobEffects.HERO_OF_THE_VILLAGE), "no Hero of the Village after the raid");
			check(p.getInventory().countItem(OnePieceBridge.berries(1).getItem()) > 0, "no Berries for beating the raid");
		});
	}

	/** Nobody defends: the raiders leave. And no raid starts away from a village. */
	private static void retreatTest(ClientGameTestContext context, TestSingleplayerContext sp) throws Exception {
		server(sp, s -> {
			clearMobs(s);
			PirateRaids.clear();
			check(PirateRaids.start(player(s)) == null, "a raid started with no village around");
			villagers(s);
			check(PirateRaids.start(player(s)) != null, "no second raid");
			ServerPlayer p = player(s);
			p.teleportTo(s.overworld(), 140.5, HOME.getY(), 0.5, Set.of(), 0f, 10f, true);
		});
		context.waitTicks(60);
		server(sp, s -> {
			int left = raiders(s).size();
			LOG.info("WM RETREAT raiders left {}", left);
			check(left == 0, left + " raiders stayed after everyone left");
			player(s).teleportTo(s.overworld(), HOME.getX() + 0.5, HOME.getY(), HOME.getZ() + 0.5, Set.of(), 0f, 10f, true);
			clearMobs(s);
		});
	}

	// ---- Helpers ----

	private static void villagers(MinecraftServer s) {
		for (int i = 0; i < 5; i++) {
			Entity v = EntityType.VILLAGER.create(s.overworld(), EntitySpawnReason.COMMAND);
			if (v != null) {
				v.snapTo(HOME.getX() + 2 + i, HOME.getY(), HOME.getZ() + 6, 0f, 0f);
				s.overworld().addFreshEntity(v);
			}
		}
	}

	private static <T extends HumanNpc> T spawn(MinecraftServer s, EntityType<T> type, BlockPos pos, String kit) {
		T npc = type.create(s.overworld(), EntitySpawnReason.COMMAND);
		if (npc == null) {
			return null;
		}
		npc.snapTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, 0f, 0f);
		npc.applyKit(kit, s.overworld().getRandom());
		s.overworld().addFreshEntity(npc);
		return npc;
	}

	private static List<WanderingHunterEntity> hunters(MinecraftServer s) {
		return s.overworld().getEntitiesOfClass(WanderingHunterEntity.class, area(), Entity::isAlive);
	}

	private static List<RookieRaiderEntity> raiders(MinecraftServer s) {
		return s.overworld().getEntitiesOfClass(RookieRaiderEntity.class, area().inflate(40), Entity::isAlive);
	}

	private static AABB area() {
		return new AABB(HOME).inflate(64, 24, 64);
	}

	private static void clearMobs(MinecraftServer s) {
		for (Entity e : s.overworld().getEntitiesOfClass(Entity.class, area().inflate(60), e -> !(e instanceof Player))) {
			e.discard();
		}
	}

	private static void check(boolean ok, String what) {
		if (!ok) {
			LOG.info("WM FAIL {}", what);
			FAILURES.add(what);
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
}
