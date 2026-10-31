package com.onepiecebosses.loot;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;

import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;

import com.onepiecebosses.BossItems;
import com.onepiecebosses.boss.RogueData;
import com.onepiecebosses.compat.OnePieceBridge;

/**
 * How survival players find rogue bosses: the main mod's pirates and Marines sometimes carry a Rumor Poster.
 * Each boss lists which NPC kits know about it ("rumorFrom" in bosses.json). Deadlier rogues are rarer rumors.
 */
public final class RumorDrops {
	private RumorDrops() {
	}

	/** Chance per kill, by tier (index 1 to 5). */
	private static final float[] CHANCE = {0f, 0.04f, 0.03f, 0.02f, 0.012f, 0.006f};

	public static void initialize() {
		ServerLivingEntityEvents.AFTER_DEATH.register((entity, source) -> {
			if (!(entity.level() instanceof ServerLevel level) || !(source.getEntity() instanceof ServerPlayer)) {
				return;
			}
			String kit = OnePieceBridge.npcKit(entity);
			if (kit == null) {
				return;
			}
			List<RogueData> heard = new ArrayList<>();
			for (RogueData boss : RogueData.all().values()) {
				if (boss.rumorFrom.contains(kit)) {
					heard.add(boss);
				}
			}
			if (heard.isEmpty()) {
				return;
			}
			RogueData boss = heard.get(entity.getRandom().nextInt(heard.size()));
			if (entity.getRandom().nextFloat() < CHANCE[Math.max(1, Math.min(5, boss.tier()))]) {
				entity.spawnAtLocation(level, new ItemStack(BossItems.RUMORS.get(boss.id)));
			}
		});
	}
}
