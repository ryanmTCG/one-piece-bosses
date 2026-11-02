package com.onepiecebosses.world.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.onepiecebosses.world.LairGrowth;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.placement.FeaturePlacer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/**
 * Turns down a tree (or giant mushroom, or bamboo) rooted inside one of our lairs (LairGrowth). In 26.3 features are
 * plain Feature records with no ConfiguredFeature wrapper, and every placed feature (selectors' picks included) is
 * placed through FeaturePlacer, so the check sits on its Feature.place calls.
 */
@Mixin(FeaturePlacer.class)
public abstract class FeaturePlacerMixin {
	@WrapOperation(method = "place(Lnet/minecraft/world/level/levelgen/placement/PlacedFeature;Lnet/minecraft/util/RandomSource;Lnet/minecraft/core/BlockPos;Z)Z",
			at = @At(value = "INVOKE", target = "Lnet/minecraft/world/level/levelgen/feature/Feature;place(Lnet/minecraft/world/level/WorldGenLevel;Lnet/minecraft/world/level/chunk/ChunkGenerator;Lnet/minecraft/util/RandomSource;Lnet/minecraft/core/BlockPos;)Z"))
	private boolean opbosses$noTreesInLairs(Feature feature, WorldGenLevel level, ChunkGenerator generator, RandomSource random,
			BlockPos pos, Operation<Boolean> original) {
		if (LairGrowth.blocked(feature, pos)) return false;
		return original.call(feature, level, generator, random, pos);
	}
}
