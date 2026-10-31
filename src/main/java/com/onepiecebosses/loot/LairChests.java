package com.onepiecebosses.loot;

import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;

import net.fabricmc.fabric.api.event.player.PlayerBlockBreakEvents;

/**
 * A lair's chest is locked to its boss's key. Vanilla stops you opening a locked chest, but not breaking it and
 * picking up what spills, so a locked chest only breaks for someone who could open it (holding the key) or in creative.
 */
public final class LairChests {
	private LairChests() {
	}

	public static void initialize() {
		PlayerBlockBreakEvents.BEFORE.register((level, player, pos, state, blockEntity) ->
				player.isCreative() || !(blockEntity instanceof BaseContainerBlockEntity container) || container.canOpen(player));
	}
}
