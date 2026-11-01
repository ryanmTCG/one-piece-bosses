package com.onepiecebosses.world;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;

import com.google.gson.Gson;

import com.mojang.brigadier.context.CommandContext;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.levelgen.Heightmap;

import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;

import com.onepiecebosses.BossesMod;
import com.onepiecebosses.compat.OnePieceBridge;
import com.onepiecemod.npc.NpcKit;

/**
 * Mobs out in the world that fill gaps the One Piece Mod leaves open (it already has Marine squads, Devil Fruit
 * bounty hunters from 100M, Sea Kings, Pacifista hunts and pirate ships, so those aren't repeated here):
 *  - Wandering bounty hunters (WanderingHunters), who go after small bounties under 100M and hunt pirate NPCs.
 *  - Rookie pirate crews that raid villages and towns (PirateRaids).
 * Their kits are in src/main/resources/opbosses/world_mobs.json, in the main mod's npc_kits.json format.
 *
 * Operators can call them with /opbosses hunters, /opbosses roam and /opbosses raid.
 */
public final class WorldMobs {
	private WorldMobs() {
	}

	private static final ResourceKey<EntityType<?>> HUNTER_KEY = ResourceKey.create(Registries.ENTITY_TYPE, BossesMod.id("wandering_hunter"));
	public static final EntityType<WanderingHunterEntity> WANDERING_HUNTER = Registry.register(BuiltInRegistries.ENTITY_TYPE, HUNTER_KEY,
			EntityType.Builder.<WanderingHunterEntity>of(WanderingHunterEntity::new, MobCategory.MONSTER)
					.sized(0.6f, 1.95f)
					.clientTrackingRange(8)
					.build(HUNTER_KEY));

	private static final ResourceKey<EntityType<?>> RAIDER_KEY = ResourceKey.create(Registries.ENTITY_TYPE, BossesMod.id("rookie_raider"));
	public static final EntityType<RookieRaiderEntity> ROOKIE_RAIDER = Registry.register(BuiltInRegistries.ENTITY_TYPE, RAIDER_KEY,
			EntityType.Builder.<RookieRaiderEntity>of(RookieRaiderEntity::new, MobCategory.MONSTER)
					.sized(0.6f, 1.95f)
					.clientTrackingRange(8)
					.build(RAIDER_KEY));

	private static class FileData {
		List<NpcKit> kits = List.of();
	}

	public static void initialize() {
		FabricDefaultAttributeRegistry.register(WANDERING_HUNTER, WanderingHunterEntity.createAttributes());
		FabricDefaultAttributeRegistry.register(ROOKIE_RAIDER, RookieRaiderEntity.createAttributes());
		try (InputStream in = WorldMobs.class.getResourceAsStream("/opbosses/world_mobs.json")) {
			FileData data = new Gson().fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), FileData.class);
			for (NpcKit kit : data.kits) {
				OnePieceBridge.addNpcKit(kit);
			}
		} catch (Exception e) {
			throw new RuntimeException("Could not read opbosses/world_mobs.json", e);
		}
		WanderingHunters.initialize();
		PirateRaids.initialize();
		registerCommands();
	}

	/**
	 * Dry, open ground minDist to maxDist blocks from origin, within 16 blocks of its height, in a loaded chunk.
	 * With nearWater it first tries for a spot right by the water (a beach landing). Null if nothing fits.
	 */
	static BlockPos dryGround(ServerLevel level, BlockPos origin, int minDist, int maxDist, RandomSource random, boolean nearWater) {
		BlockPos fallback = null;
		for (int attempt = 0; attempt < 24; attempt++) {
			double angle = random.nextDouble() * Math.PI * 2;
			int distance = minDist + random.nextInt(Math.max(1, maxDist - minDist + 1));
			int x = Mth.floor(origin.getX() + Math.cos(angle) * distance);
			int z = Mth.floor(origin.getZ() + Math.sin(angle) * distance);
			if (!level.hasChunkAt(new BlockPos(x, 0, z))) {
				continue;
			}
			BlockPos pos = new BlockPos(x, level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z), z);
			if (!level.getFluidState(pos.below()).isEmpty() || !level.getBlockState(pos.below()).isSolid()
					|| Math.abs(pos.getY() - origin.getY()) >= 16
					|| !level.getBlockState(pos).getCollisionShape(level, pos).isEmpty()
					|| !level.getBlockState(pos.above()).getCollisionShape(level, pos.above()).isEmpty()) {
				continue;
			}
			if (!nearWater || waterNextTo(level, pos) != null) {
				return pos;
			}
			if (fallback == null) {
				fallback = pos;
			}
		}
		return fallback;
	}

	/** A water surface block within 3 blocks of pos at about its height, or null. */
	static BlockPos waterNextTo(ServerLevel level, BlockPos pos) {
		for (int dx = -3; dx <= 3; dx++) {
			for (int dz = -3; dz <= 3; dz++) {
				for (int dy = -2; dy <= 0; dy++) {
					BlockPos water = pos.offset(dx, dy, dz);
					if (level.getFluidState(water).isSource() && level.getBlockState(water.above()).isAir()) {
						return water;
					}
				}
			}
		}
		return null;
	}

	// ---- /opbosses (operators only) ----

	private static void registerCommands() {
		CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> dispatcher.register(
				Commands.literal("opbosses")
						.requires(Commands.hasPermission(Commands.LEVEL_GAMEMASTERS))
						.then(Commands.literal("hunters")
								.executes(c -> hunters(c, c.getSource().getPlayerOrException()))
								.then(Commands.argument("player", EntityArgument.player())
										.executes(c -> hunters(c, EntityArgument.getPlayer(c, "player")))))
						.then(Commands.literal("roam")
								.executes(c -> roam(c, c.getSource().getPlayerOrException())))
						.then(Commands.literal("raid")
								.executes(c -> raid(c, c.getSource().getPlayerOrException()))
								.then(Commands.argument("player", EntityArgument.player())
										.executes(c -> raid(c, EntityArgument.getPlayer(c, "player")))))));
	}

	private static int hunters(CommandContext<CommandSourceStack> c, ServerPlayer player) {
		int sent = WanderingHunters.sendHunt(player);
		c.getSource().sendSuccess(() -> Component.literal(sent > 0 ? "Sent " + sent + " bounty hunters after " + player.getName().getString()
				: "No bounty hunters came: they only hunt bounties under 100M, and need dry ground nearby"), false);
		return sent;
	}

	private static int roam(CommandContext<CommandSourceStack> c, ServerPlayer player) {
		int sent = WanderingHunters.roam(player);
		c.getSource().sendSuccess(() -> Component.literal(sent > 0 ? sent + " bounty hunters are wandering nearby" : "No dry ground nearby"), false);
		return sent;
	}

	private static int raid(CommandContext<CommandSourceStack> c, ServerPlayer player) {
		PirateRaids.Raid raid = PirateRaids.start(player);
		c.getSource().sendSuccess(() -> Component.literal(raid != null ? "Pirates are raiding " + raid.place
				: "No raid: stand in a village (3+ villagers nearby) or a town, with no raid already on"), false);
		return raid != null ? 1 : 0;
	}
}
