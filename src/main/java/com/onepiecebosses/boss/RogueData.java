package com.onepiecebosses.boss;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import com.onepiecemod.character.CharacterData;

/**
 * One rogue boss, read from src/main/resources/opbosses/bosses.json.
 * Each entry is read twice: once as the One Piece Mod's CharacterData (so its boss code can run the fight),
 * and once as this class for the parts only this mod uses. To change a boss, edit the JSON, not this class.
 */
public class RogueData {
	/** The main mod's view of this boss: name, tier, health, damage, Berries, size, powers and prizes. */
	public transient CharacterData character;

	public String id;
	/** Width and height of the boss's hitbox in blocks, before its size (scale) is applied. Fits its model. */
	public float[] hitbox = {0.6f, 1.95f};
	/** How much a first win raises your bounty. The main mod pays its tier value; BossRewards adds the rest. */
	public long bountyReward;
	/** An NPC kit from crews.json the boss calls at the start and at phase 2, or "" to fight alone. */
	public String crew = "";
	/** The phase 3 move (see RogueSignatures). */
	public String signature = "";
	/** One line about the boss, on its Rumor Poster. */
	public String lore = "";
	public String intro = "";
	public String phase2 = "";
	public String phase3 = "";
	public String defeat = "";
	/** Main mod NPC kits that sometimes drop this boss's Rumor Poster (see RumorDrops). */
	public List<String> rumorFrom = List.of();
	/** The trophy item this boss drops on a first win (an item id in this mod, like "rusted_anchor_link"). */
	public String trophy = "";
	/** Creatures (entity ids, like "onepiece:manticore") that come with each crew wave. Shiki's mutated beasts. */
	public List<String> beasts = List.of();

	public int tier() {
		return character.tier;
	}

	public String name() {
		return character.name;
	}

	// ---- Loading ----

	private static final Map<String, RogueData> ALL = new LinkedHashMap<>();

	public static Map<String, RogueData> all() {
		if (ALL.isEmpty()) {
			try (InputStream in = RogueData.class.getResourceAsStream("/opbosses/bosses.json")) {
				JsonObject file = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
				Gson gson = new Gson();
				for (JsonElement entry : file.getAsJsonArray("bosses")) {
					RogueData boss = gson.fromJson(entry, RogueData.class);
					boss.character = gson.fromJson(entry, CharacterData.class);
					boss.character.role = CharacterData.BOSS;
					// Prizes are the main mod's; a trophy is added by BossRewards. A boss with a fruitItem (Shiki's
					// Float-Float Fruit) drops it on a win, the way the main mod's story bosses do.
					ALL.put(boss.id, boss);
				}
			} catch (Exception e) {
				throw new RuntimeException("Could not read opbosses/bosses.json", e);
			}
		}
		return ALL;
	}

	/** The boss with this id, or null. */
	public static RogueData get(String id) {
		return all().get(id);
	}

	/** Any boss, for a mob whose id is missing (an old save, or a boss removed from the JSON). */
	public static RogueData fallback() {
		return all().values().iterator().next();
	}
}
