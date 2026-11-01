package com.onepiecebosses.loot;

import java.util.Map;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.AABB;

import com.onepiecebosses.BossesMod;
import com.onepiecebosses.boss.RogueBossEntity;
import com.onepiecebosses.boss.RogueData;
import com.onepiecemod.npc.HumanNpc;

/**
 * Rebuilds the lair a player stands in, like the world made it: every block back in place, a fresh locked chest with
 * new loot, and the boss and crew back (the lair's .nbt carries them, and the main mod sets them up as they appear,
 * as it does for /place). It's done by placing the lair's own pieces again, chunk by chunk, as /place structure does.
 */
public final class LairReset {
	private LairReset() {
	}

	public enum Result { NOT_IN_LAIR, BOSS_STILL_HERE, DONE }

	/** The lair at the player's feet (or a few blocks below, for a ship deck or a floating island), or null. */
	public static Map.Entry<String, StructureStart> lairAt(ServerLevel level, Player player) {
		for (String lair : LairChests.LAIRS) {
			ResourceKey<Structure> key = ResourceKey.create(Registries.STRUCTURE, BossesMod.id(lair));
			for (int down = 0; down <= 8; down += 4) {
				StructureStart start = level.structureManager().getStructureWithPieceAt(player.blockPosition().below(down), holder -> holder.is(key));
				if (start.isValid()) {
					return Map.entry(lair, start);
				}
			}
		}
		return null;
	}

	public static Result reset(ServerLevel level, ServerPlayer player) {
		Map.Entry<String, StructureStart> found = lairAt(level, player);
		if (found == null) {
			player.displayClientMessage(Component.literal("There's no rogue's lair here to rebuild.").withStyle(ChatFormatting.GRAY), true);
			return Result.NOT_IN_LAIR;
		}
		String lair = found.getKey();
		StructureStart start = found.getValue();
		BoundingBox bb = start.getBoundingBox();
		AABB area = AABB.of(bb).inflate(24);
		String bossId = LairChests.LAIR_BOSSES.get(lair);
		RogueData boss = RogueData.get(bossId);

		// One boss at a time: beat the one that's here first.
		if (!level.getEntitiesOfClass(RogueBossEntity.class, area, e -> e.isAlive() && e.getCharacterId().equals(bossId)).isEmpty()) {
			player.displayClientMessage(Component.literal(boss.name() + " is still here. Beat them before you rebuild the lair.")
					.withStyle(ChatFormatting.RED), true);
			return Result.BOSS_STILL_HERE;
		}
		// Clear out what's left of the old crew (and beasts), so nothing doubles up when the lair brings its own back.
		for (Entity e : level.getEntitiesOfClass(Entity.class, area, e -> !(e instanceof Player))) {
			boolean crew = e instanceof HumanNpc npc && npc.isPersistenceRequired();
			boolean beast = boss.beasts.contains(BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).toString());
			if (e instanceof RogueBossEntity || crew || beast) {
				e.discard();
			}
		}
		// Place every piece again in each chunk it covers (loading those chunks if they aren't).
		ChunkPos min = new ChunkPos(bb.minX() >> 4, bb.minZ() >> 4);
		ChunkPos max = new ChunkPos(bb.maxX() >> 4, bb.maxZ() >> 4);
		for (int cx = min.x; cx <= max.x; cx++) {
			for (int cz = min.z; cz <= max.z; cz++) {
				level.getChunk(cx, cz);
			}
		}
		for (int cx = min.x; cx <= max.x; cx++) {
			for (int cz = min.z; cz <= max.z; cz++) {
				ChunkPos cp = new ChunkPos(cx, cz);
				BoundingBox chunkBox = new BoundingBox(cp.getMinBlockX(), level.getMinY(), cp.getMinBlockZ(),
						cp.getMaxBlockX(), level.getMaxY() - 1, cp.getMaxBlockZ());
				start.placeInChunk(level, level.structureManager(), level.getChunkSource().getGenerator(), level.getRandom(), chunkBox, cp);
			}
		}
		level.playSound(null, player.blockPosition(), SoundEvents.RAID_HORN.value(), SoundSource.HOSTILE, 1.5f, 1.0f);
		Component title = Component.literal(boss.lair.isEmpty() ? "The lair" : boss.lair).withStyle(ChatFormatting.GOLD);
		for (ServerPlayer near : level.getEntitiesOfClass(ServerPlayer.class, area.inflate(32))) {
			near.displayClientMessage(Component.empty().append(title).append(Component.literal(" stands again, and " + boss.name() + " is back.")
					.withStyle(ChatFormatting.YELLOW)), false);
		}
		BossesMod.LOGGER.info("Rebuilt {} at {} for {}", lair, bb, player.getName().getString());
		return Result.DONE;
	}
}
