package com.onepiecebosses.world.mixin;

import com.onepiecebosses.world.LairSites;
import java.util.Optional;
import net.minecraft.world.level.levelgen.structure.Structure;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Runs our lairs' ground check (see LairSites) after vanilla has picked a spot and checked its biome. */
@Mixin(Structure.class)
public abstract class LairSiteMixin {
	@Inject(method = "findValidGenerationPoint", at = @At("RETURN"), cancellable = true)
	private void opbosses$checkLairSite(Structure.GenerationContext ctx,
			CallbackInfoReturnable<Optional<Structure.GenerationStub>> cir) {
		cir.setReturnValue(LairSites.filter((Structure) (Object) this, ctx, cir.getReturnValue()));
	}
}
