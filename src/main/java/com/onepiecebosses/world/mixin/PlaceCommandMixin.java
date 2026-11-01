package com.onepiecebosses.world.mixin;

import com.onepiecebosses.world.LairSites;
import net.minecraft.server.commands.PlaceCommand;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** /place structure puts a lair exactly where it's asked: the ground check (LairSites) is off while it runs. */
@Mixin(PlaceCommand.class)
public abstract class PlaceCommandMixin {
	@Inject(method = "placeStructure", at = @At("HEAD"))
	private static void opbosses$placeStart(CallbackInfoReturnable<Integer> cir) {
		LairSites.PLACING.set(true);
	}

	@Inject(method = "placeStructure", at = @At("RETURN"))
	private static void opbosses$placeEnd(CallbackInfoReturnable<Integer> cir) {
		LairSites.PLACING.set(false);
	}
}
