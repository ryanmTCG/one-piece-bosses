package com.onepiecebosses.world.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.onepiecebosses.world.LairSites;
import java.util.Optional;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureCheck;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

/** The same ground check where /locate (and anything else asking "could it start here?") asks, so it agrees with world generation. */
@Mixin(StructureCheck.class)
public abstract class StructureCheckSiteMixin {
	@WrapOperation(method = "canCreateStructure", at = @At(value = "INVOKE",
			target = "Lnet/minecraft/world/level/levelgen/structure/Structure;findValidGenerationPoint(Lnet/minecraft/world/level/levelgen/structure/Structure$GenerationContext;)Ljava/util/Optional;"))
	private Optional<Structure.GenerationStub> opbosses$checkLairSite(Structure structure, Structure.GenerationContext ctx,
			Operation<Optional<Structure.GenerationStub>> original) {
		return LairSites.filter(structure, ctx, original.call(structure, ctx));
	}
}
