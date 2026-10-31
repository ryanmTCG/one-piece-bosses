package com.onepiecebosses;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Function;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;

import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;

import com.onepiecebosses.boss.RogueData;
import com.onepiecebosses.boss.RumorPosterItem;

/** A Rumor Poster and a trophy for every rogue boss in bosses.json, and the creative tab. */
public final class BossItems {
	private BossItems() {
	}

	/** Boss id -> its Rumor Poster. */
	public static final Map<String, Item> RUMORS = new LinkedHashMap<>();
	/** Trophy id (bosses.json "trophy") -> item. */
	public static final Map<String, Item> TROPHIES = new LinkedHashMap<>();

	public static final ResourceKey<CreativeModeTab> TAB_KEY = ResourceKey.create(
			BuiltInRegistries.CREATIVE_MODE_TAB.key(), BossesMod.id("bosses"));

	static void initialize() {
		for (RogueData boss : RogueData.all().values()) {
			Rarity rarity = boss.tier() >= 4 ? Rarity.EPIC : boss.tier() >= 3 ? Rarity.RARE : Rarity.UNCOMMON;
			RUMORS.put(boss.id, register("rumor_" + boss.id, properties -> new RumorPosterItem(boss.id, properties),
					new Item.Properties().rarity(rarity)));
			if (!boss.trophy.isEmpty()) {
				TROPHIES.put(boss.trophy, register(boss.trophy, Item::new, new Item.Properties().stacksTo(1).rarity(rarity)));
			}
		}

		Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, TAB_KEY, FabricCreativeModeTab.builder()
				.icon(() -> new ItemStack(RUMORS.values().iterator().next()))
				.title(Component.literal("One Piece: Rogue Bosses"))
				.displayItems((params, output) -> {
					RUMORS.values().forEach(output::accept);
					TROPHIES.values().forEach(output::accept);
				})
				.build());
	}

	private static Item register(String name, Function<Item.Properties, Item> factory, Item.Properties properties) {
		ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, BossesMod.id(name));
		Item item = factory.apply(properties.setId(key));
		Registry.register(BuiltInRegistries.ITEM, key, item);
		return item;
	}
}
