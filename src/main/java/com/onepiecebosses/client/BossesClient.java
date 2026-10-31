package com.onepiecebosses.client;

import net.minecraft.client.renderer.entity.EntityRenderers;

import net.fabricmc.api.ClientModInitializer;

import com.onepiecebosses.boss.RogueBosses;

/** The client-only start of One Piece Bosses. */
public class BossesClient implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		RogueModels.register();
		EntityRenderers.register(RogueBosses.ROGUE_BOSS, RogueBossRenderer::new);
	}
}
