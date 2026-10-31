package com.onepiecebosses.client;

import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.resources.Identifier;

import com.onepiecebosses.BossesMod;
import com.onepiecemod.character.client.CharacterRenderer;

/**
 * Draws a rogue boss the way the One Piece Mod draws its characters (player-shaped, with the health bar's
 * wind-up animations), with the skin assets/opbosses/textures/entity/boss/<id>.png (a normal 64x64 Minecraft skin).
 * Replace any of them with a real skin of the same name.
 */
public class RogueBossRenderer extends CharacterRenderer {
	public RogueBossRenderer(EntityRendererProvider.Context context) {
		super(context);
	}

	@Override
	public Identifier getTextureLocation(State state) {
		return BossesMod.id("textures/entity/boss/" + state.characterId + ".png");
	}
}
