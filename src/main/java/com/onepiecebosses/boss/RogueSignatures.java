package com.onepiecebosses.boss;

import java.util.List;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.phys.Vec3;

import com.onepiecebosses.compat.OnePieceBridge;
import com.onepiecemod.character.BossStrikes;
import com.onepiecemod.fx.MoveFx;

/**
 * The rogue bosses' phase 3 signature moves. Each one builds on one of the main mod's signature strikes
 * (they draw their own warning circles and land a moment later, so they can be dodged) and adds its own twist.
 * A boss's "signature" in bosses.json picks one of these.
 *
 * "extra" is the boss's difficulty (0 Normal, 1 Hard, 2 Expert): more strikes, longer effects.
 */
public final class RogueSignatures {
	private RogueSignatures() {
	}

	public static void use(String signature, Mob boss, LivingEntity target, ServerLevel level, BossStrikes strikes, float damage, int extra) {
		switch (signature) {
			case "anchor_drag" -> { // Rourke hurls his anchor and hauls you in along the chain, into the line it cuts.
				pull(target, boss, 1.4);
				target.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 40 + 20 * extra, 2));
				level.playSound(null, boss.blockPosition(), SoundEvents.CHAIN_BREAK, SoundSource.HOSTILE, 2.0f, 0.6f);
				strikes.signature("slash_line", boss, target, level, damage, extra);
			}
			case "widows_veil" -> { // Corvina vanishes into her fog and reappears behind you while smoke rains down.
				for (Player player : playersNear(boss, level, 14)) {
					player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 50 + 20 * extra, 0));
				}
				level.sendParticles(ParticleTypes.CAMPFIRE_COSY_SMOKE, boss.getX(), boss.getY() + 1, boss.getZ(), 60, 3, 1.5, 3, 0.01);
				boss.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 50, 0));
				Vec3 behind = target.position().subtract(target.getLookAngle().multiply(1, 0, 1).scale(2.0));
				BlockPos spot = safeSpot(level, BlockPos.containing(behind.x, target.getY(), behind.z));
				if (spot != null) { // Only onto solid ground: never off a cliff or into a wall.
					boss.teleportTo(behind.x, spot.getY(), behind.z);
				}
				strikes.signature("rain_smoke", boss, target, level, damage, extra);
			}
			case "seastone_volley" -> { // Graves's garrison fires seastone shot: it rains metal and drains fruit users.
				strikes.signature("rain_metal", boss, target, level, damage, extra);
				for (Player player : playersNear(boss, level, 12)) {
					if (OnePieceBridge.isFruitUser(player)) {
						OnePieceBridge.drainFruitPower(player, 100 + 40 * extra);
					}
				}
				level.playSound(null, boss.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 1.5f, 1.4f);
			}
			case "hollow_cut" -> { // Tsurugi's cut flies the whole line, and the empty armor's curse withers whoever is close.
				strikes.signature("slash_line", boss, target, level, damage * 1.15f, extra);
				for (Player player : playersNear(boss, level, 5)) {
					player.addEffect(new MobEffectInstance(MobEffects.WITHER, 60 + 20 * extra, 1));
				}
				level.sendParticles(ParticleTypes.SOUL, boss.getX(), boss.getY() + 1, boss.getZ(), 30, 0.8, 1.0, 0.8, 0.02);
			}
			case "boiler_burst" -> { // Gantz vents his boiler: a scalding wave all around, then he has to cool down.
				strikes.signature("ground_wave", boss, target, level, damage, extra);
				for (Player player : playersNear(boss, level, 9)) {
					player.igniteForSeconds(4 + 2 * extra);
				}
				MoveFx.shockwave(level, boss.position(), 9, MoveFx.FIRE, MoveFx.FIRE_OUT);
				level.sendParticles(ParticleTypes.CLOUD, boss.getX(), boss.getY() + boss.getBbHeight(), boss.getZ(), 50, 1.0, 0.5, 1.0, 0.15);
				level.playSound(null, boss.blockPosition(), SoundEvents.FIRE_EXTINGUISH, SoundSource.HOSTILE, 2.5f, 0.5f);
				boss.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60, 2)); // The opening: hit him while he cools.
			}
			case "tidal_judgment" -> { // Nereus opens a whirlpool that drags everything in, with freezing deep water raining down.
				strikes.signature("black_hole", boss, target, level, damage, extra);
				strikes.signature("rain_ice", boss, target, level, damage * 0.6f, extra);
				for (Player player : playersNear(boss, level, 12)) {
					player.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 100, 1));
				}
				level.sendParticles(ParticleTypes.SPLASH, boss.getX(), boss.getY() + 0.5, boss.getZ(), 120, 5, 0.5, 5, 0.3);
			}
			// ---- The film villains ----
			case "golden_finale" -> { // Tesoro: the gold everyone touched grabs them, and molten gold rains down.
				for (Player player : playersNear(boss, level, 12)) {
					player.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 50 + 20 * extra, 4));
					player.addEffect(new MobEffectInstance(MobEffects.MINING_FATIGUE, 80 + 20 * extra, 2));
					level.sendParticles(ParticleTypes.WAX_ON, player.getX(), player.getY() + 1, player.getZ(), 30, 0.4, 0.8, 0.4, 0.05);
				}
				MoveFx.shockwave(level, boss.position(), 12, MoveFx.GOLD, MoveFx.GOLD_OUT);
				level.playSound(null, boss.blockPosition(), SoundEvents.ANVIL_LAND, SoundSource.HOSTILE, 1.5f, 0.6f);
				strikes.signature("rain_metal", boss, target, level, damage, extra + 2);
			}
			case "uta_world" -> { // Uta: her song pulls everyone into a dream (you nod off), then Tot Musica's light falls.
				for (Player player : playersNear(boss, level, 16)) {
					player.addEffect(new MobEffectInstance(MobEffects.NAUSEA, 120 + 20 * extra, 0));
					player.addEffect(new MobEffectInstance(MobEffects.SLOWNESS, 60 + 20 * extra, 2));
					player.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 25, 0));
				}
				for (int i = 0; i < 24; i++) {
					double a = Math.PI * 2 * i / 24;
					level.sendParticles(ParticleTypes.NOTE, boss.getX() + Math.cos(a) * 6, boss.getY() + 2, boss.getZ() + Math.sin(a) * 6, 1, 0, 0, 0, i / 24.0);
				}
				level.playSound(null, boss.blockPosition(), SoundEvents.NOTE_BLOCK_CHIME.value(), SoundSource.HOSTILE, 3.0f, 0.7f);
				level.playSound(null, boss.blockPosition(), SoundEvents.NOTE_BLOCK_BELL.value(), SoundSource.HOSTILE, 3.0f, 1.0f);
				boss.heal(boss.getMaxHealth() * 0.02f); // The dreamers' cheering keeps her going.
				strikes.signature("rain_light", boss, target, level, damage, extra + 1);
			}
			case "battle_smasher" -> { // Zephyr: a seastone haymaker that sends you flying, then the shockwave and his Smash Blaster shells.
				Vec3 away = target.position().subtract(boss.position()).multiply(1, 0, 1).normalize().scale(2.2);
				target.setDeltaMovement(away.x, 0.9, away.z);
				target.needsSync = true;
				level.sendParticles(ParticleTypes.EXPLOSION_EMITTER, target.getX(), target.getY() + 1, target.getZ(), 1, 0, 0, 0, 0);
				level.playSound(null, boss.blockPosition(), SoundEvents.GENERIC_EXPLODE.value(), SoundSource.HOSTILE, 2.0f, 0.8f);
				for (Player player : playersNear(boss, level, 12)) {
					if (OnePieceBridge.isFruitUser(player)) {
						OnePieceBridge.drainFruitPower(player, 140 + 40 * extra);
					}
				}
				strikes.signature("ground_wave", boss, target, level, damage, extra);
				strikes.signature("rain_metal", boss, target, level, damage * 0.8f, extra);
			}
			case "gasha_fortress" -> { // Bullet: fuses all the metal around into armour (hard to hurt for a while), and the scrap comes down.
				boss.addEffect(new MobEffectInstance(MobEffects.RESISTANCE, 100 + 20 * extra, 1));
				boss.addEffect(new MobEffectInstance(MobEffects.ABSORPTION, 200, 3 + extra));
				MoveFx.shockwave(level, boss.position(), 10, 0xFFD0D0D8, 0xFF505060);
				level.sendParticles(ParticleTypes.CRIT, boss.getX(), boss.getY() + 1.5, boss.getZ(), 80, 1.5, 1.5, 1.5, 0.3);
				level.playSound(null, boss.blockPosition(), SoundEvents.ANVIL_USE, SoundSource.HOSTILE, 2.0f, 0.5f);
				level.playSound(null, boss.blockPosition(), SoundEvents.IRON_GOLEM_REPAIR, SoundSource.HOSTILE, 2.0f, 0.6f);
				strikes.signature("rain_metal", boss, target, level, damage, extra + 2);
				strikes.signature("ground_wave", boss, target, level, damage, extra);
			}
			case "lion_float" -> { // Shiki: floats everyone into the sky and lets go, while he drops floating rock on them.
				for (Player player : playersNear(boss, level, 14)) {
					player.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 30 + 10 * extra, 1));
					level.sendParticles(ParticleTypes.END_ROD, player.getX(), player.getY(), player.getZ(), 15, 0.4, 0.2, 0.4, 0.05);
				}
				level.playSound(null, boss.blockPosition(), SoundEvents.WIND_CHARGE_BURST.value(), SoundSource.HOSTILE, 2.0f, 0.6f);
				strikes.signature("rain_rock", boss, target, level, damage, extra + 2);
			}
			default -> strikes.signature(signature, boss, target, level, damage, extra); // Any main mod signature works too.
		}
	}

	/** Pulls the target toward the boss. */
	private static void pull(LivingEntity target, Mob boss, double strength) {
		Vec3 toward = boss.position().subtract(target.position()).normalize().scale(strength);
		target.setDeltaMovement(toward.x, 0.3, toward.z);
		target.needsSync = true;
	}

	/** The spot itself, or one a block up or down, where the boss can stand: solid below, two blocks of air. Null if none. */
	private static BlockPos safeSpot(ServerLevel level, BlockPos pos) {
		for (int dy : new int[] {0, 1, -1}) {
			BlockPos p = pos.offset(0, dy, 0);
			if (level.getBlockState(p.below()).isFaceSturdy(level, p.below(), Direction.UP)
					&& level.getBlockState(p).getCollisionShape(level, p).isEmpty()
					&& level.getBlockState(p.above()).getCollisionShape(level, p.above()).isEmpty()) {
				return p;
			}
		}
		return null;
	}

	private static List<Player> playersNear(Mob boss, ServerLevel level, double radius) {
		return level.getEntitiesOfClass(Player.class, boss.getBoundingBox().inflate(radius),
				player -> player.isAlive() && !player.isCreative() && !player.isSpectator());
	}
}
