package com.onepiecebosses.compat;

import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;

import com.onepiecemod.bounty.Bounty;
import com.onepiecemod.character.BossStrikes;
import com.onepiecemod.character.CharacterAttachments;
import com.onepiecemod.character.CharacterEntity;
import com.onepiecemod.npc.HumanNpc;
import com.onepiecemod.npc.NpcFeature;
import com.onepiecemod.npc.NpcKit;
import com.onepiecemod.world.SeastoneEffects;

/**
 * Every static call into the One Piece Mod goes through here (RogueBossEntity also extends its CharacterEntity).
 * If the main mod renames something, this is the first file to fix.
 */
public final class OnePieceBridge {
	private OnePieceBridge() {
	}

	/** Adds an NPC kit to the main mod's list, unless it already has one with that id. */
	public static void addNpcKit(NpcKit kit) {
		NpcKit.all().putIfAbsent(kit.id, kit);
	}

	/** Spawns one of the main mod's NPCs from a kit, tagged as a boss minion (boss attacks pass through it). */
	public static Mob spawnMinion(ServerLevel level, String kitId, BlockPos pos, float yaw) {
		HumanNpc npc = NpcFeature.spawn(level, kitId, pos, yaw);
		if (npc != null) {
			npc.addTag(BossStrikes.MINION_TAG);
		}
		return npc;
	}

	/** Spawns any mob (a main mod creature like "onepiece:manticore", or a vanilla one), tagged as a boss minion. */
	public static Mob spawnBeast(ServerLevel level, String entityId, BlockPos pos, float yaw) {
		Identifier id = Identifier.tryParse(entityId);
		if (id == null || !BuiltInRegistries.ENTITY_TYPE.containsKey(id)) {
			return null;
		}
		Entity entity = BuiltInRegistries.ENTITY_TYPE.getValue(id).create(level, EntitySpawnReason.MOB_SUMMONED);
		if (!(entity instanceof Mob mob)) {
			if (entity != null) {
				entity.discard();
			}
			return null;
		}
		mob.snapTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, yaw, 0.0f);
		mob.addTag(BossStrikes.MINION_TAG);
		mob.setPersistenceRequired();
		level.addFreshEntity(mob);
		return mob;
	}

	/** The kit a main mod NPC was made from ("pirate", "fishman"...), or null for anything else. */
	public static String npcKit(LivingEntity entity) {
		return entity instanceof HumanNpc npc ? npc.getKitId() : null;
	}

	/** True for players who ate a fruit, and for bosses who have one. */
	public static boolean isFruitUser(LivingEntity entity) {
		return SeastoneEffects.isFruitUser(entity);
	}

	/** The main mod's seastone weakness. 20 ticks = 1 second. */
	public static void drainFruitPower(LivingEntity entity, int ticks) {
		SeastoneEffects.drain(entity, ticks);
	}

	/** What the main mod already pays for beating a boss with this id the first time. */
	public static long mainModBossReward(String bossId) {
		return Bounty.bossReward(bossId);
	}

	public static void raiseBounty(ServerPlayer player, long amount, String reason) {
		Bounty.raise(player, amount, reason, false);
	}

	/** The hardest fight this player has unlocked against a boss, the same way Wanted Posters work it out. */
	public static int unlockedDifficulty(Player player, String bossId) {
		if (CharacterAttachments.has(player, CharacterAttachments.BOSSES_DEFEATED, bossId + ":hard")) {
			return CharacterEntity.EXPERT;
		}
		if (CharacterAttachments.has(player, CharacterAttachments.BOSSES_DEFEATED, bossId)) {
			return CharacterEntity.HARD;
		}
		return CharacterEntity.NORMAL;
	}

	/** A main mod (or rogue) character's display name, or a tidied id if it has none. */
	public static String characterName(String id) {
		com.onepiecebosses.boss.RogueData rogue = com.onepiecebosses.boss.RogueData.get(id);
		if (rogue != null) {
			return rogue.name();
		}
		com.onepiecemod.character.CharacterData data = com.onepiecemod.character.CharacterData.get(id);
		return data != null && data.name != null ? data.name : id.replace('_', ' ');
	}
}
