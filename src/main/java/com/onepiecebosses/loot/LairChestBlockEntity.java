package com.onepiecebosses.loot;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.NonNullList;
import net.minecraft.network.chat.Component;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.WorldlyContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ChestMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.RandomizableContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

/**
 * The 27 slots of a lair chest, its loot table (filled the first time someone opens it) and its lock.
 * Hoppers can't reach in, so a hopper under a locked lair chest can't drain it.
 */
public class LairChestBlockEntity extends RandomizableContainerBlockEntity implements WorldlyContainer {
	private static final int[] NO_SLOTS = new int[0];
	private NonNullList<ItemStack> items = NonNullList.withSize(27, ItemStack.EMPTY);

	public LairChestBlockEntity(BlockPos pos, BlockState state) {
		super(LairChests.ENTITY, pos, state);
	}

	@Override
	public int getContainerSize() {
		return items.size();
	}

	@Override
	protected NonNullList<ItemStack> getItems() {
		return items;
	}

	@Override
	protected void setItems(NonNullList<ItemStack> items) {
		this.items = items;
	}

	@Override
	protected Component getDefaultName() {
		return Component.translatable(getBlockState().getBlock().getDescriptionId());
	}

	@Override
	protected AbstractContainerMenu createMenu(int id, Inventory inventory) {
		return ChestMenu.threeRows(id, inventory, this);
	}

	@Override
	protected void saveAdditional(ValueOutput output) {
		super.saveAdditional(output);
		if (!trySaveLootTable(output)) {
			ContainerHelper.saveAllItems(output, items);
		}
	}

	@Override
	protected void loadAdditional(ValueInput input) {
		super.loadAdditional(input);
		items = NonNullList.withSize(getContainerSize(), ItemStack.EMPTY);
		if (!tryLoadLootTable(input)) {
			ContainerHelper.loadAllItems(input, items);
		}
	}

	@Override
	public int[] getSlotsForFace(Direction side) {
		return NO_SLOTS;
	}

	@Override
	public boolean canPlaceItemThroughFace(int slot, ItemStack stack, Direction side) {
		return false;
	}

	@Override
	public boolean canTakeItemThroughFace(int slot, ItemStack stack, Direction side) {
		return false;
	}
}
