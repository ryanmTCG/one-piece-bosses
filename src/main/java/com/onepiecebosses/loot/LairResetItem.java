package com.onepiecebosses.loot;

import java.util.function.Consumer;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

/** The Lair Restoration Charter: use it inside a rogue's lair and the lair is rebuilt, boss, crew, chest and all. Used up. */
public class LairResetItem extends Item {
	public LairResetItem(Properties properties) {
		super(properties);
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		if (!(level instanceof ServerLevel serverLevel) || !(player instanceof ServerPlayer serverPlayer)) {
			return InteractionResult.SUCCESS;
		}
		ItemStack stack = player.getItemInHand(hand);
		if (LairReset.reset(serverLevel, serverPlayer) == LairReset.Result.DONE) {
			if (!player.isCreative()) {
				stack.shrink(1);
			}
			player.getCooldowns().addCooldown(stack, 100);
			return InteractionResult.SUCCESS;
		}
		return InteractionResult.FAIL;
	}

	@Override
	public void appendHoverText(ItemStack stack, TooltipContext context, TooltipDisplay displayComponent, Consumer<Component> textConsumer, TooltipFlag type) {
		textConsumer.accept(Component.literal("Use it inside a rogue's lair to rebuild it:").withStyle(ChatFormatting.GRAY));
		textConsumer.accept(Component.literal("the boss, their crew and a fresh locked chest come back.").withStyle(ChatFormatting.GRAY));
		textConsumer.accept(Component.literal("Only once the boss there is beaten.").withStyle(ChatFormatting.DARK_GRAY));
	}
}
