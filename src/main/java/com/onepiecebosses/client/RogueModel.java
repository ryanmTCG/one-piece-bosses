package com.onepiecebosses.client;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.mojang.blaze3d.vertex.PoseStack;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.HumanoidArm;

import com.onepiecemod.character.client.CharacterRenderer;

/**
 * A rogue's own body (see RogueModels). Animates like a player model, with two changes: the arms stay on this
 * body's shoulders (the player model puts them 5 px from the middle while it swings), and the coat tails,
 * trains and skirts swing back as the boss walks, like the main mod's giant capes. Held items sit in this body's
 * hands, however long its arms are.
 */
public class RogueModel extends HumanoidModel<CharacterRenderer.State> {
	private final float shoulderX;
	private final float shoulderZ;
	private final float handDrop;
	private final List<ModelPart> swayParts = new ArrayList<>();
	private final List<Integer> swayDirections = new ArrayList<>();

	public RogueModel(ModelPart root, String id) {
		super(root);
		float[] shoulder = RogueModels.SHOULDERS.get(id);
		this.shoulderX = -shoulder[0];
		this.shoulderZ = shoulder[2];
		// The held-item layer puts items 10 px down the arm, where a player's hand is.
		this.handDrop = (RogueModels.HANDS.get(id) - 10.0F) / 16.0F;
		for (Map.Entry<String, Integer> sway : RogueModels.sway(id).entrySet()) {
			ModelPart part = root;
			for (String name : sway.getKey().split("/")) {
				part = part.getChild(name);
			}
			swayParts.add(part);
			swayDirections.add(sway.getValue());
		}
	}

	@Override
	public void setupAnim(CharacterRenderer.State state) {
		super.setupAnim(state);
		float yaw = body.yRot;
		rightArm.x = -Mth.cos(yaw) * shoulderX;
		rightArm.z = Mth.sin(yaw) * shoulderX + shoulderZ;
		leftArm.x = Mth.cos(yaw) * shoulderX;
		leftArm.z = -Mth.sin(yaw) * shoulderX + shoulderZ;

		float speed = Math.min(1.0F, state.walkAnimationSpeed);
		float drift = Mth.sin(state.ageInTicks * 0.09F) * 0.04F;
		float step = Mth.sin(state.walkAnimationPos * 0.6662F) * 0.08F * speed;
		for (int i = 0; i < swayParts.size(); i++) {
			// Positive x rotation lifts cloth out behind; front cloth (-1) lifts out in front.
			swayParts.get(i).xRot = swayDirections.get(i) * (0.05F + speed * 0.45F + drift + step);
		}
	}

	@Override
	public void translateToHand(CharacterRenderer.State state, HumanoidArm arm, PoseStack poseStack) {
		super.translateToHand(state, arm, poseStack);
		poseStack.translate(0.0F, handDrop, 0.0F);
	}
}
