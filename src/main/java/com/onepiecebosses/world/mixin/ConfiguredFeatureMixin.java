package com.onepiecebosses.world.mixin;

import com.onepiecebosses.world.LairGrowth;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Turns down a tree (or giant mushroom, or bamboo) rooted inside one of our lairs (LairGrowth). */
@Mixin(ConfiguredFeature.class)
public abstract class ConfiguredFeatureMixin {
	@Inject(method = "place", at = @At("HEAD"), cancellable = true)
	private void opbosses$noTreesInLairs(WorldGenLevel level, ChunkGenerator generator, RandomSource random, BlockPos pos,
			CallbackInfoReturnable<Boolean> cir) {
		if (LairGrowth.blocked(((ConfiguredFeature<?, ?>) (Object) this).feature(), pos)) cir.setReturnValue(false);
	}
}
