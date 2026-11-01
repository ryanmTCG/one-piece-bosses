package com.onepiecebosses.world.mixin;

import com.onepiecebosses.world.LairGrowth;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Notes the lairs in a chunk while it is decorated, so no tree grows inside them (LairGrowth). */
@Mixin(ChunkGenerator.class)
public abstract class ChunkGeneratorMixin {
	@Inject(method = "applyBiomeDecoration", at = @At("HEAD"))
	private void opbosses$decorateStart(WorldGenLevel level, ChunkAccess chunk, StructureManager structures, CallbackInfo ci) {
		LairGrowth.begin(level, chunk.getPos(), structures);
	}

	@Inject(method = "applyBiomeDecoration", at = @At("RETURN"))
	private void opbosses$decorateEnd(WorldGenLevel level, ChunkAccess chunk, StructureManager structures, CallbackInfo ci) {
		LairGrowth.end();
	}
}
