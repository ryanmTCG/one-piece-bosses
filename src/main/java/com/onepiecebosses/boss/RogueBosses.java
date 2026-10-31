package com.onepiecebosses.boss;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;

import com.onepiecebosses.BossesMod;
import com.onepiecemod.character.CharacterEntity;

/** Registers the rogue boss mob. One mob type for every rogue; which one it is gets saved on the mob. */
public final class RogueBosses {
	private RogueBosses() {
	}

	public static final ResourceKey<EntityType<?>> ROGUE_BOSS_KEY = ResourceKey.create(Registries.ENTITY_TYPE, BossesMod.id("rogue_boss"));
	public static final EntityType<RogueBossEntity> ROGUE_BOSS = Registry.register(
			BuiltInRegistries.ENTITY_TYPE,
			ROGUE_BOSS_KEY,
			EntityType.Builder.of(RogueBossEntity::new, MobCategory.MISC)
					.sized(0.6f, 1.95f) // Player-sized; big bosses use the scale attribute, like the main mod's.
					.fireImmune()
					.clientTrackingRange(10)
					.build(ROGUE_BOSS_KEY)
	);

	public static void initialize() {
		FabricDefaultAttributeRegistry.register(ROGUE_BOSS, CharacterEntity.createAttributes());
	}
}
