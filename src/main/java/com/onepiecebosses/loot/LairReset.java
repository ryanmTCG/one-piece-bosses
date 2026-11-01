package com.onepiecebosses.loot;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.ChatFormatting;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.AABB;

import com.onepiecebosses.BossesMod;
import com.onepiecebosses.boss.RogueData;
import com.onepiecebosses.compat.OnePieceBridge;
import com.onepiecemod.character.CharacterEntity;
import com.onepiecemod.npc.HumanNpc;

/**
 * Rebuilds the boss structure a player stands in, like the world made it: every block back in place, the chest
 * refilled, and the boss and crew back (the structure's pieces carry them, and the main mod sets them up as they
 * appear, as it does for /place). It's done by placing the structure's own pieces again, chunk by chunk, as
 * /place structure does. Works on this mod's lairs and on the One Piece Mod's boss structures whose pieces carry
 * their boss (listed in opbosses/rebuildable.json, from tools/gen_rebuildable.py).
 */
public final class LairReset {
	private LairReset() {
	}

	public enum Result { NOT_IN_LAIR, BOSS_STILL_HERE, DONE }

	/** A structure the charter can rebuild: its name for messages and the boss ids its pieces bring. */
	public record Site(Identifier structure, String name, Set<String> bosses, List<String> beasts) {}

	private static final Map<Identifier, Site> SITES = new LinkedHashMap<>();

	public static Map<Identifier, Site> sites() {
		if (SITES.isEmpty()) {
			for (Map.Entry<String, String> lair : LairChests.LAIR_BOSSES.entrySet()) {
				RogueData boss = RogueData.get(lair.getValue());
				Identifier id = BossesMod.id(lair.getKey());
				SITES.put(id, new Site(id, boss.lair.isEmpty() ? "The lair" : boss.lair, Set.of(boss.id), boss.beasts));
			}
			try (InputStream in = LairReset.class.getResourceAsStream("/opbosses/rebuildable.json")) {
				JsonObject file = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
				for (Map.Entry<String, JsonElement> e : file.getAsJsonObject("sites").entrySet()) {
					JsonObject site = e.getValue().getAsJsonObject();
					List<String> bosses = new ArrayList<>();
					site.getAsJsonArray("bosses").forEach(b -> bosses.add(b.getAsString()));
					Identifier id = Identifier.parse(e.getKey());
					SITES.put(id, new Site(id, site.get("name").getAsString(), Set.copyOf(bosses), List.of()));
				}
			} catch (Exception e) {
				BossesMod.LOGGER.warn("Could not read opbosses/rebuildable.json; only this mod's lairs can be rebuilt", e);
			}
		}
		return SITES;
	}

	/** The rebuildable structure at the player's feet (or a few blocks below, for a ship deck or a floating island), or null. */
	public static Map.Entry<Site, StructureStart> siteAt(ServerLevel level, Player player) {
		Map<Identifier, Site> sites = sites();
		for (int down = 0; down <= 8; down += 4) {
			StructureStart start = level.structureManager().getStructureWithPieceAt(player.blockPosition().below(down),
					holder -> holder.unwrapKey().map(k -> sites.containsKey(k.identifier())).orElse(false));
			if (start.isValid()) {
				Identifier id = level.registryAccess().lookupOrThrow(net.minecraft.core.registries.Registries.STRUCTURE).getKey(start.getStructure());
				Site site = sites.get(id);
				if (site != null) {
					return Map.entry(site, start);
				}
			}
		}
		return null;
	}

	public static Result reset(ServerLevel level, ServerPlayer player) {
		Map.Entry<Site, StructureStart> found = siteAt(level, player);
		if (found == null) {
			player.sendOverlayMessage(Component.literal("There's no boss's lair here to rebuild.").withStyle(ChatFormatting.GRAY));
			return Result.NOT_IN_LAIR;
		}
		Site site = found.getKey();
		StructureStart start = found.getValue();
		BoundingBox bb = start.getBoundingBox();
		AABB area = AABB.of(bb).inflate(24);
		String bossNames = String.join(" and ", site.bosses().stream().map(OnePieceBridge::characterName).sorted().toList());

		// One fight at a time: beat whoever's here first.
		List<CharacterEntity> alive = level.getEntitiesOfClass(CharacterEntity.class, area, e -> e.isAlive() && site.bosses().contains(e.getCharacterId()));
		if (!alive.isEmpty()) {
			player.sendOverlayMessage(Component.literal(OnePieceBridge.characterName(alive.get(0).getCharacterId())
					+ " is still here. Beat them before you rebuild the lair.").withStyle(ChatFormatting.RED));
			return Result.BOSS_STILL_HERE;
		}
		// Clear out what's left of the old crew (and beasts), so nothing doubles up when the pieces bring their own back.
		for (Entity e : level.getEntitiesOfClass(Entity.class, area, e -> !(e instanceof Player))) {
			boolean boss = e instanceof CharacterEntity c && site.bosses().contains(c.getCharacterId());
			boolean crew = e instanceof HumanNpc npc && npc.isPersistenceRequired();
			// The pirates and Marines a structure brings (onepiece:sea_pirate and kin) are kept for good; free-roaming ones aren't.
			boolean guard = e instanceof Mob mob && mob.isPersistenceRequired() && !(e instanceof CharacterEntity)
					&& BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getNamespace().equals("onepiece");
			boolean beast = site.beasts().contains(BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).toString());
			if (boss || crew || guard || beast) {
				e.discard();
			}
		}
		// Place every piece again in each chunk it covers (loading those chunks if they aren't).
		ChunkPos min = new ChunkPos(bb.minX() >> 4, bb.minZ() >> 4);
		ChunkPos max = new ChunkPos(bb.maxX() >> 4, bb.maxZ() >> 4);
		for (int cx = min.x(); cx <= max.x(); cx++) {
			for (int cz = min.z(); cz <= max.z(); cz++) {
				level.getChunk(cx, cz);
			}
		}
		for (int cx = min.x(); cx <= max.x(); cx++) {
			for (int cz = min.z(); cz <= max.z(); cz++) {
				ChunkPos cp = new ChunkPos(cx, cz);
				BoundingBox chunkBox = new BoundingBox(cp.getMinBlockX(), level.getMinY(), cp.getMinBlockZ(),
						cp.getMaxBlockX(), level.getMaxY() - 1, cp.getMaxBlockZ());
				start.placeInChunk(level, level.structureManager(), level.getChunkSource().getGenerator(), level.getRandom(), chunkBox, cp);
			}
		}
		level.playSound(null, player.blockPosition(), SoundEvents.RAID_HORN.value(), SoundSource.HOSTILE, 1.5f, 1.0f);
		Component title = Component.literal(site.name()).withStyle(ChatFormatting.GOLD);
		for (ServerPlayer near : level.getEntitiesOfClass(ServerPlayer.class, area.inflate(32))) {
			near.sendSystemMessage(Component.empty().append(title).append(Component.literal(" stands again, and " + bossNames + " is back.")
					.withStyle(ChatFormatting.YELLOW)));
		}
		BossesMod.LOGGER.info("Rebuilt {} at {} for {}", site.structure(), bb, player.getName().getString());
		return Result.DONE;
	}
}
