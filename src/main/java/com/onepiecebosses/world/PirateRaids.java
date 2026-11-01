package com.onepiecebosses.world;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerBossEvent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.BossEvent;
import net.minecraft.world.Difficulty;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;

import com.onepiecebosses.compat.OnePieceBridge;

/**
 * Rookie pirate crews that raid villages and towns. While a player is in a vanilla village (3 or more villagers
 * close by) or one of the main mod's towns, now and then a small crew lands on the shore nearby (or walks in
 * from the edge when there's no water) and marches on it. A boss bar counts the raiders left.
 *
 * Beat them all and the place thanks you: Berries for everyone who stood their ground, and Hero of the Village
 * in a village. If every defender leaves, or nobody beats them within 6 minutes, they make off with their loot.
 * Raids aren't saved: after a restart the raiders that are left are just pirates.
 *
 * While a raid is on, the main mod holds back its own Marine hunts and Navy raids for the players defending it.
 */
public final class PirateRaids {
	private PirateRaids() {
	}

	private static final int CHECK_EVERY = 20 * 60;
	/** Chance per minute in a village or town: about one raid every 25 minutes you spend in one. */
	private static final float CHANCE = 0.04f;
	/** After a raid, this long before that player can see another. */
	private static final int BREAK = 20 * 60 * 20;
	private static final int MAX_TICKS = 20 * 60 * 6;
	/** Players this close to the raid see the bar and count as defenders. */
	private static final double BAR_RANGE = 64.0;
	/** With no player this close, the raiders leave. */
	private static final double LEAVE_RANGE = 96.0;
	private static final int MIN_VILLAGERS = 3;

	public static final String KIT = "rookie_raider";
	public static final String CAPTAIN_KIT = "raider_captain";
	public static final String TAG = "opbosses_raider";

	private static final List<Raid> RAIDS = new ArrayList<>();
	private static final Map<UUID, Long> NEXT_RAID = new HashMap<>();

	/** One raid going on. */
	public static final class Raid {
		public final ServerLevel level;
		public final BlockPos center;
		public final String place;
		public final String crew;
		public final boolean village;
		public final List<UUID> raiders = new ArrayList<>();
		public final long started;
		final ServerBossEvent bar;
		int total;
		boolean over;

		Raid(ServerLevel level, BlockPos center, String place, String crew, boolean village) {
			this.level = level;
			this.center = center;
			this.place = place;
			this.crew = crew;
			this.village = village;
			this.started = level.getGameTime();
			this.bar = new ServerBossEvent(UUID.randomUUID(), Component.literal(crew + " raid " + place),
					BossEvent.BossBarColor.RED, BossEvent.BossBarOverlay.NOTCHED_10);
		}

		/** Raiders still standing. */
		public int alive() {
			int count = 0;
			for (UUID id : raiders) {
				Entity e = level.getEntity(id);
				if (e != null && e.isAlive()) {
					count++;
				}
			}
			return count;
		}

		public boolean isOver() {
			return over;
		}

		List<ServerPlayer> defenders(double range) {
			return level.getEntitiesOfClass(ServerPlayer.class, new AABB(center).inflate(range), p -> p.isAlive() && !p.isSpectator());
		}
	}

	/** A village or town: where to march, what to call it, and whether it's a vanilla village. */
	private record Settlement(BlockPos center, String name, boolean village) {}

	static void initialize() {
		ServerTickEvents.END_SERVER_TICK.register(PirateRaids::tick);
		// A defender is busy: the main mod doesn't start its own Marine hunts or Navy raids on them meanwhile.
		OnePieceBridge.registerBusy(PirateRaids::isDefending);
	}

	private static void tick(MinecraftServer server) {
		if (server.getTickCount() % 20 == 0) {
			for (Raid raid : List.copyOf(RAIDS)) {
				update(raid);
			}
			RAIDS.removeIf(Raid::isOver);
		}
		if (server.getTickCount() % CHECK_EVERY != 0) {
			return;
		}
		for (ServerPlayer player : server.getPlayerList().getPlayers()) {
			if (player.level().dimension() != Level.OVERWORLD || player.isCreative() || player.isSpectator() || !player.isAlive()
					|| player.level().getDifficulty() == Difficulty.PEACEFUL || OnePieceBridge.isBusy(player)
					|| player.level().getGameTime() < NEXT_RAID.getOrDefault(player.getUUID(), 0L)) {
				continue;
			}
			if (player.getRandom().nextFloat() < CHANCE) {
				start(player);
			}
		}
	}

	/** True if a raid is going on around this player. */
	public static boolean isDefending(ServerPlayer player) {
		for (Raid raid : RAIDS) {
			if (!raid.over && raid.level == player.level() && raid.center.distSqr(player.blockPosition()) < BAR_RANGE * BAR_RANGE) {
				return true;
			}
		}
		return false;
	}

	/** The raid at a position, if one is on. */
	public static Raid raidNear(ServerLevel level, BlockPos pos) {
		for (Raid raid : RAIDS) {
			if (!raid.over && raid.level == level && raid.center.distSqr(pos) < LEAVE_RANGE * LEAVE_RANGE) {
				return raid;
			}
		}
		return null;
	}

	/**
	 * Starts a raid on the village or town the player is in. Returns null if they aren't in one, one is already
	 * being raided, or no landing spot was found. The chance roll and the break between raids are the caller's.
	 */
	public static Raid start(ServerPlayer player) {
		ServerLevel level = (ServerLevel) player.level();
		Settlement place = findSettlement(level, player);
		if (place == null || raidNear(level, place.center) != null) {
			return null;
		}
		RandomSource random = player.getRandom();
		BlockPos landing = WorldMobs.dryGround(level, place.center, 26, 38, random, true);
		if (landing == null) {
			landing = WorldMobs.dryGround(level, place.center, 16, 26, random, false);
		}
		if (landing == null) {
			return null;
		}
		Raid raid = new Raid(level, place.center, place.name, OnePieceBridge.pirateCrewName(random), place.village);
		// A captain and two to four rookies; a known pirate (50M+) defending draws one more.
		int count = 3 + random.nextInt(3) + (OnePieceBridge.threatLevel(player) >= 2 ? 1 : 0);
		for (int i = 0; i < count; i++) {
			BlockPos pos = i == 0 ? landing : WorldMobs.dryGround(level, landing, 1, 3, random, false);
			RookieRaiderEntity raider = WorldMobs.ROOKIE_RAIDER.create(level, EntitySpawnReason.EVENT);
			if (raider == null) {
				continue;
			}
			BlockPos at = pos != null ? pos : landing;
			raider.snapTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, random.nextFloat() * 360f, 0f);
			raider.applyKit(i == 0 ? CAPTAIN_KIT : KIT, random);
			// Everyone on the raid sails under the same flag.
			String name = raider.getCustomName() != null ? raider.getCustomName().getString() : "";
			raider.setCustomName(Component.literal(i == 0 ? name + " of the " + raid.crew : raid.crew + " " + name));
			raider.setRaidTarget(place.center);
			raider.setOnRaid(true);
			raider.addTag(TAG);
			level.addFreshEntity(raider);
			raid.raiders.add(raider.getUUID());
		}
		if (raid.raiders.isEmpty()) {
			return null;
		}
		raid.total = raid.raiders.size();
		// The rowboat they came in, pulled up on the shore.
		BlockPos water = WorldMobs.waterNextTo(level, landing);
		if (water != null) {
			Entity boat = EntityType.OAK_BOAT.create(level, EntitySpawnReason.EVENT);
			if (boat != null) {
				boat.snapTo(water.getX() + 0.5, water.getY() + 1, water.getZ() + 0.5, random.nextFloat() * 360f, 0f);
				level.addFreshEntity(boat);
			}
		}
		RAIDS.add(raid);
		Component news = Component.literal("Pirates! The " + raid.crew + " are raiding " + raid.place + "!").withStyle(ChatFormatting.RED);
		for (ServerPlayer defender : raid.defenders(BAR_RANGE)) {
			defender.sendSystemMessage(news);
			NEXT_RAID.put(defender.getUUID(), level.getGameTime() + BREAK);
		}
		level.playSound(null, landing, SoundEvents.RAID_HORN.value(), SoundSource.HOSTILE, 3.0f, 1.2f);
		update(raid);
		return raid;
	}

	private static Settlement findSettlement(ServerLevel level, ServerPlayer player) {
		OnePieceBridge.TownSpot town = OnePieceBridge.townAt(level, player.blockPosition());
		if (town != null) {
			return new Settlement(town.center(), town.name(), false);
		}
		List<AbstractVillager> villagers = level.getEntitiesOfClass(AbstractVillager.class, player.getBoundingBox().inflate(48, 16, 48), Entity::isAlive);
		if (villagers.size() < MIN_VILLAGERS) {
			return null;
		}
		Vec3 sum = Vec3.ZERO;
		for (AbstractVillager villager : villagers) {
			sum = sum.add(villager.position());
		}
		return new Settlement(BlockPos.containing(sum.scale(1.0 / villagers.size())), "the village", true);
	}

	/** Once a second: the bar, then whether the raid was beaten or gave up. */
	private static void update(Raid raid) {
		if (raid.over) {
			return;
		}
		int alive = raid.alive();
		List<ServerPlayer> inRange = raid.defenders(BAR_RANGE);
		for (ServerPlayer player : List.copyOf(raid.bar.getPlayers())) {
			if (!inRange.contains(player)) {
				raid.bar.removePlayer(player);
			}
		}
		for (ServerPlayer player : inRange) {
			raid.bar.addPlayer(player);
		}
		raid.bar.setName(Component.literal(raid.crew + " raid " + raid.place + " (" + alive + " left)"));
		raid.bar.setProgress(raid.total == 0 ? 0f : (float) alive / raid.total);

		// Leaving comes first: with nobody near, the raiders' chunks may have unloaded, and they'd look beaten.
		if (raid.defenders(LEAVE_RANGE).isEmpty() || raid.level.getGameTime() - raid.started > MAX_TICKS) {
			retreat(raid);
		} else if (alive == 0) {
			win(raid, inRange);
		}
	}

	private static void win(Raid raid, List<ServerPlayer> defenders) {
		raid.over = true;
		raid.bar.removeAllPlayers();
		Component news = Component.literal("The " + raid.crew + " are beaten! " + capital(raid.place) + " is safe.").withStyle(ChatFormatting.GREEN);
		int berries = 5 * raid.total;
		for (ServerPlayer player : defenders) {
			player.sendSystemMessage(news);
			net.minecraft.world.item.ItemStack reward = OnePieceBridge.berries(berries);
			player.getInventory().add(reward);
			if (!reward.isEmpty()) {
				player.drop(reward, false);
			}
			if (raid.village) {
				player.addEffect(new MobEffectInstance(MobEffects.HERO_OF_THE_VILLAGE, 20 * 60 * 10, 0));
			}
		}
		raid.level.playSound(null, raid.center, SoundEvents.PLAYER_LEVELUP, SoundSource.PLAYERS, 1.0f, 1.0f);
	}

	/** Gave up: the raiders row off with whatever they grabbed. */
	private static void retreat(Raid raid) {
		raid.over = true;
		raid.bar.removeAllPlayers();
		for (UUID id : raid.raiders) {
			Entity e = raid.level.getEntity(id);
			if (e != null && e.isAlive()) {
				raid.level.sendParticles(ParticleTypes.POOF, e.getX(), e.getY() + 1, e.getZ(), 12, 0.3, 0.6, 0.3, 0.02);
				e.discard();
			}
		}
		Component news = Component.literal("The " + raid.crew + " made off from " + raid.place + " with what they could carry.").withStyle(ChatFormatting.GRAY);
		for (ServerPlayer player : raid.defenders(LEAVE_RANGE * 2)) {
			player.sendSystemMessage(news);
		}
	}

	private static String capital(String text) {
		return text.isEmpty() ? text : Character.toUpperCase(text.charAt(0)) + text.substring(1);
	}

	/** Ends every raid quietly (the in-world test uses this between checks). */
	public static void clear() {
		for (Raid raid : RAIDS) {
			raid.over = true;
			raid.bar.removeAllPlayers();
		}
		RAIDS.clear();
		NEXT_RAID.clear();
	}
}
