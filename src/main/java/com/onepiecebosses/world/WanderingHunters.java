package com.onepiecebosses.world;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.level.Level;

import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;

import com.onepiecebosses.compat.OnePieceBridge;

/**
 * Brings wandering bounty hunters into the world:
 *  - Hunts: players with a bounty from 1 to 99,999,999 Berries (the main mod's threat levels 1 and 2, before its own
 *    Devil Fruit hunters take over at 100M) now and then find one to three hunters on their trail.
 *  - Roaming: anyone out in the Overworld sometimes comes across a pair just walking the land. They leave you alone
 *    without a bounty, and pick fights with the main mod's pirate patrols.
 *
 * Every 30 seconds each player (Overworld, survival or adventure, not Peaceful, on dry land) rolls for each.
 */
public final class WanderingHunters {
	private WanderingHunters() {
	}

	private static final int CHECK_EVERY = 20 * 30;
	/** Hunt chance per check at threat level 0, 1, 2: about every 6 minutes at level 1, every 4 at level 2. */
	private static final float[] HUNT_CHANCE = {0f, 0.08f, 0.12f};
	/** After a hunt, this long before the next one for that player. */
	private static final int HUNT_BREAK = 20 * 60 * 6;
	/** Chance per check of a roaming pair turning up near anyone (about every 15 minutes). */
	private static final float ROAM_CHANCE = 0.03f;
	/** No more roaming hunters while this many are already around. */
	private static final int MAX_NEARBY = 3;

	public static final String KIT = "wandering_hunter";
	public static final String VETERAN_KIT = "veteran_hunter";

	private static final Map<UUID, Long> NEXT_HUNT = new HashMap<>();

	static void initialize() {
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			if (server.getTickCount() % CHECK_EVERY != 0) {
				return;
			}
			for (ServerPlayer player : server.getPlayerList().getPlayers()) {
				if (!canMeet(player)) {
					continue;
				}
				RandomSource random = player.getRandom();
				int threat = threat(player);
				long now = player.level().getGameTime();
				if (threat > 0 && now >= NEXT_HUNT.getOrDefault(player.getUUID(), 0L) && OnePieceBridge.navyCanStart(player)
						&& random.nextFloat() < HUNT_CHANCE[threat]) {
					if (sendHunt(player) > 0) {
						NEXT_HUNT.put(player.getUUID(), now + HUNT_BREAK);
					}
				} else if (random.nextFloat() < ROAM_CHANCE && nearby((ServerLevel) player.level(), player.blockPosition()) < MAX_NEARBY) {
					roam(player);
				}
			}
		});
	}

	/** 1 or 2 for bounties these hunters chase (the main mod's threat levels), 0 otherwise. */
	static int threat(ServerPlayer player) {
		return WanderingHunterEntity.isPrey(player) ? Math.max(1, Math.min(2, OnePieceBridge.threatLevel(player))) : 0;
	}

	private static boolean canMeet(ServerPlayer player) {
		return player.level().dimension() == Level.OVERWORLD && !player.isCreative() && !player.isSpectator()
				&& player.level().getDifficulty() != Difficulty.PEACEFUL && player.isAlive()
				&& !player.isInWater() && player.getVehicle() == null;
	}

	private static int nearby(ServerLevel level, BlockPos pos) {
		return level.getEntitiesOfClass(WanderingHunterEntity.class, new net.minecraft.world.phys.AABB(pos).inflate(96), e -> e.isAlive()).size();
	}

	/** Sends hunters after a player with a small bounty. Returns how many came (0 if the bounty is out of range or there's no ground). */
	public static int sendHunt(ServerPlayer player) {
		int threat = threat(player);
		if (threat == 0) {
			return 0;
		}
		ServerLevel level = (ServerLevel) player.level();
		RandomSource random = player.getRandom();
		// Level 1: one or two. Level 2: two or three, led by a veteran.
		int count = threat == 1 ? 1 + random.nextInt(2) : 2 + random.nextInt(2);
		int sent = 0;
		for (int i = 0; i < count; i++) {
			BlockPos spot = WorldMobs.dryGround(level, player.blockPosition(), 20, 32, random, false);
			WanderingHunterEntity hunter = spawn(level, spot, threat == 2 && i == 0 ? VETERAN_KIT : KIT, random);
			if (hunter != null) {
				hunter.setTarget(player);
				sent++;
			}
		}
		if (sent > 0) {
			player.sendSystemMessage(Component.literal((sent == 1 ? "A bounty hunter has" : sent + " bounty hunters have")
					+ " picked up the trail of your " + OnePieceBridge.formatBerries(OnePieceBridge.bounty(player)) + " bounty!")
					.withStyle(ChatFormatting.DARK_PURPLE));
			level.playSound(null, player.blockPosition(), SoundEvents.PILLAGER_AMBIENT, SoundSource.HOSTILE, 1.0f, 0.8f);
		}
		return sent;
	}

	/** A pair of hunters walking the land somewhere near the player, not after anyone yet. Returns how many came. */
	public static int roam(ServerPlayer player) {
		ServerLevel level = (ServerLevel) player.level();
		RandomSource random = player.getRandom();
		BlockPos spot = WorldMobs.dryGround(level, player.blockPosition(), 36, 52, random, false);
		if (spot == null) {
			return 0;
		}
		int count = 1 + random.nextInt(2);
		int sent = 0;
		for (int i = 0; i < count; i++) {
			BlockPos pos = i == 0 ? spot : WorldMobs.dryGround(level, spot, 1, 3, random, false);
			if (spawn(level, pos != null ? pos : spot, random.nextInt(5) == 0 ? VETERAN_KIT : KIT, random) != null) {
				sent++;
			}
		}
		return sent;
	}

	private static WanderingHunterEntity spawn(ServerLevel level, BlockPos pos, String kit, RandomSource random) {
		if (pos == null) {
			return null;
		}
		WanderingHunterEntity hunter = WorldMobs.WANDERING_HUNTER.create(level, EntitySpawnReason.EVENT);
		if (hunter == null) {
			return null;
		}
		hunter.snapTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, random.nextFloat() * 360f, 0f);
		hunter.applyKit(kit, random);
		level.addFreshEntity(hunter);
		return hunter;
	}
}
