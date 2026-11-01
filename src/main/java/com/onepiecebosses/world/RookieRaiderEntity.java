package com.onepiecebosses.world;

import java.util.EnumSet;

import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.animal.golem.IronGolem;
import net.minecraft.world.entity.npc.villager.AbstractVillager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;

import com.onepiecemod.bounty.MarineEntity;
import com.onepiecemod.npc.HumanNpc;
import com.onepiecemod.town.TownsfolkEntity;

/**
 * A rookie pirate on a raid (see PirateRaids). They march on the village or town they came for and go after
 * villagers, townsfolk, iron golems, players, Marines and bounty hunters on the way. Pirate-side, so the main mod's
 * Marines and townsfolk treat them like any other pirate.
 */
public class RookieRaiderEntity extends HumanNpc {
	/** Where the raid is headed (the village's middle or the town's plaza). Null for a raider with nowhere to go. */
	private BlockPos raidTarget;
	private boolean onRaid = false;

	public RookieRaiderEntity(EntityType<? extends RookieRaiderEntity> type, Level level) {
		super(type, level);
	}

	public static AttributeSupplier.Builder createAttributes() {
		return HumanNpc.createNpcAttributes().add(Attributes.FOLLOW_RANGE, 32.0);
	}

	@Override
	public boolean isMarineSide() {
		return false;
	}

	@Override
	protected void registerGoals() {
		super.registerGoals();
		this.goalSelector.addGoal(5, new MarchGoal());
	}

	@Override
	protected void addTargetGoals() {
		this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Player.class, true));
		this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, AbstractVillager.class, false));
		this.targetSelector.addGoal(3, new NearestAttackableTargetGoal<>(this, TownsfolkEntity.class, false));
		this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, IronGolem.class, true));
		this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, MarineEntity.class, true));
		this.targetSelector.addGoal(4, new NearestAttackableTargetGoal<>(this, WanderingHunterEntity.class, true));
	}

	/** On a raid that's going on right now (not saved): it mustn't despawn, or the raid would count it as beaten. */
	public void setOnRaid(boolean onRaid) {
		this.onRaid = onRaid;
	}

	@Override
	public boolean removeWhenFarAway(double distance) {
		return !onRaid && super.removeWhenFarAway(distance);
	}

	public void setRaidTarget(BlockPos target) {
		this.raidTarget = target;
	}

	public BlockPos getRaidTarget() {
		return raidTarget;
	}

	/** With nobody to fight, head for the middle of the village. */
	private class MarchGoal extends Goal {
		private int repath = 0;

		MarchGoal() {
			setFlags(EnumSet.of(Goal.Flag.MOVE));
		}

		@Override
		public boolean canUse() {
			return raidTarget != null && getTarget() == null && distanceToSqr(net.minecraft.world.phys.Vec3.atCenterOf(raidTarget)) > 8 * 8;
		}

		@Override
		public boolean canContinueToUse() {
			return canUse();
		}

		@Override
		public void start() {
			repath = 0;
		}

		@Override
		public void tick() {
			if (--repath <= 0) {
				repath = 40;
				getNavigation().moveTo(raidTarget.getX() + 0.5, raidTarget.getY(), raidTarget.getZ() + 0.5, 1.0);
			}
		}

		@Override
		public void stop() {
			getNavigation().stop();
		}
	}

	@Override
	protected void addAdditionalSaveData(ValueOutput output) {
		super.addAdditionalSaveData(output);
		if (raidTarget != null) {
			output.putLong("RaidTarget", raidTarget.asLong());
		}
	}

	@Override
	protected void readAdditionalSaveData(ValueInput input) {
		super.readAdditionalSaveData(input);
		long packed = input.getLongOr("RaidTarget", Long.MIN_VALUE);
		raidTarget = packed == Long.MIN_VALUE ? null : BlockPos.of(packed);
	}
}
