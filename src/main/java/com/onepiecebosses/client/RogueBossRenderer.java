package com.onepiecebosses.client;

import java.util.HashMap;
import java.util.Map;

import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.resources.Identifier;

import com.onepiecebosses.BossesMod;
import com.onepiecemod.character.client.CharacterRenderer;

/**
 * Draws a rogue boss the way the One Piece Mod draws its characters (its wind-up and attack animations included),
 * but with that rogue's own body (RogueModels) and skin, assets/opbosses/textures/entity/boss/<id>.png.
 */
public class RogueBossRenderer extends CharacterRenderer {
	private final Map<String, RogueModel> rogueModels = new HashMap<>();

	public RogueBossRenderer(EntityRendererProvider.Context context) {
		super(context);
		for (String id : RogueModels.IDS) {
			rogueModels.put(id, new RogueModel(context.bakeLayer(RogueModels.layer(id)), id));
		}
	}

	@Override
	protected RenderType getRenderType(State state, boolean bodyVisible, boolean translucent, boolean glowing) {
		RenderType type = super.getRenderType(state, bodyVisible, translucent, glowing);
		// The parent picks the player-shaped model just before drawing; swap in this rogue's body after it.
		RogueModel body = rogueModels.get(state.characterId);
		if (body != null) {
			this.model = body;
		}
		return type;
	}

	@Override
	public Identifier getTextureLocation(State state) {
		return BossesMod.id("textures/entity/boss/" + state.characterId + ".png");
	}
}
