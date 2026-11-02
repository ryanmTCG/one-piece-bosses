package com.onepiecebosses.world.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.onepiecebosses.world.LairSites;
import java.util.Optional;
import net.minecraft.world.level.levelgen.structure.Structure;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/**
 * Runs our lairs' ground check (LairSites) on the spot a structure picked, where world generation asks for it
 * (Structure.generate). It wraps the call rather than injecting into findValidGenerationPoint: the main mod's own
 * site check also hooks the RETURN of that method and always sets the return value, which cancels any later callback
 * there, so depending on mixin order ours sometimes never ran. Wrapping the call puts ours after everything inside it.
 */
@Mixin(Structure.class)
public abstract class LairSiteMixin {
	@WrapOperation(method = "generate", at = @At(value = "INVOKE",
			target = "Lnet/minecraft/world/level/levelgen/structure/Structure;findValidGenerationPoint(Lnet/minecraft/world/level/levelgen/structure/Structure$GenerationContext;)Ljava/util/Optional;"))
	private Optional<Structure.GenerationStub> opbosses$checkLairSite(Structure structure, Structure.GenerationContext ctx,
			Operation<Optional<Structure.GenerationStub>> original) {
		return LairSites.filter(structure, ctx, original.call(structure, ctx));
	}
}
