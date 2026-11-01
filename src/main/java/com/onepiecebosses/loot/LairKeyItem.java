package com.onepiecebosses.loot;

import java.util.function.Consumer;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;

import com.onepiecebosses.boss.RogueData;

/**
 * The key a rogue boss drops when beaten. Its lair's chest is locked to it (the chest's vanilla "lock",
 * set in tools/lairs/gen_lairs.py): hold the key in your main hand and open the chest.
 */
public class LairKeyItem extends Item {
	private final String bossId;

	public LairKeyItem(String bossId, Properties properties) {
		super(properties);
		this.bossId = bossId;
	}

	@Override
	public Component getName(ItemStack stack) {
		RogueData boss = RogueData.get(bossId);
		return Component.literal(boss.lair.isEmpty() ? boss.name() + "'s Key" : "Key to " + boss.lair);
	}

	@Override
	public void appendHoverText(ItemStack stack, TooltipContext context, TooltipDisplay displayComponent, Consumer<Component> textConsumer, TooltipFlag type) {
		RogueData boss = RogueData.get(bossId);
		textConsumer.accept(Component.literal("Dropped by " + boss.name()).withStyle(ChatFormatting.GRAY));
		textConsumer.accept(Component.literal("Hold it to open the locked chest in " + (boss.lair.isEmpty() ? "their lair" : boss.lair) + ".")
				.withStyle(ChatFormatting.DARK_GRAY));
	}
}
