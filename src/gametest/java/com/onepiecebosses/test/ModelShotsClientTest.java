package com.onepiecebosses.test;

import java.util.Set;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

import com.onepiecebosses.boss.RogueBossEntity;
import com.onepiecebosses.boss.RogueBosses;
import com.onepiecebosses.boss.RogueData;

/**
 * Model portraits: every rogue stands still on a flat floor with the HUD hidden, and the camera circles them
 * (front, three-quarter, side, back) and catches a swing. Screenshots go to build/run/clientGameTest/screenshots
 * as model_&lt;id&gt;_&lt;view&gt;.png. Nothing is checked here; it's for looking at the models.
 */
public class ModelShotsClientTest implements FabricClientGameTest {
	private static final Logger LOG = LoggerFactory.getLogger("bosses-models");
	private static final double BX = 0.5, BY = 100, BZ = 0.5;
	/** View name and the camera's angle around the boss, in degrees (0 = in front of it). */
	private static final String[] VIEWS = {"front", "three_quarter", "side", "back"};
	private static final double[] ANGLES = {0, 35, 90, 180};

	@Override
	public void runTest(ClientGameTestContext context) {
		if (!TestFilter.runs("models")) {
			return;
		}
		try {
			run(context);
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	private void run(ClientGameTestContext context) throws Exception {
		try (TestSingleplayerContext sp = context.worldBuilder().create()) {
			sp.getConnection().waitForChunksRender();
			sp.getServer().runCommand("time set noon");
			sp.getServer().runCommand("weather clear");
			sp.getServer().runCommand("gamerule spawn_mobs false");
			sp.getServer().runCommand("gamerule advance_time false");
			sp.getServer().runCommand("gamerule advance_weather false");
			sp.getServer().runCommand("gamemode spectator @a");
			context.waitTicks(10);
			context.setScreen(() -> null);
			// Hide the HUD (26.3 keeps it in a private field on gui.hud, not in options.hideGui).
			context.runOnClient(client -> {
				try {
					java.lang.reflect.Field hidden = client.gui.hud.getClass().getDeclaredField("isHidden");
					hidden.setAccessible(true);
					hidden.set(client.gui.hud, true);
				} catch (ReflectiveOperationException e) {
					throw new RuntimeException(e);
				}
			});
			sp.getServer().runOnServer(s -> floor(s.overworld()));
			context.waitTicks(20);

			for (String id : RogueData.all().keySet()) {
				if (!TestFilter.picks(id)) {
					continue;
				}
				shoot(context, sp, id);
			}
			LOG.info("MS DONE");
		}
	}

	private void shoot(ClientGameTestContext context, TestSingleplayerContext sp, String id) throws Exception {
		float[] height = {2f};
		sp.getServer().runOnServer(s -> {
			ServerLevel level = s.overworld();
			for (Entity e : level.getEntitiesOfClass(Entity.class, new AABB(BX, BY, BZ, BX, BY, BZ).inflate(30), e -> !(e instanceof Player))) {
				e.discard();
			}
			RogueBossEntity boss = RogueBosses.ROGUE_BOSS.create(level, EntitySpawnReason.COMMAND);
			if (boss == null) {
				return;
			}
			boss.setPos(BX, BY, BZ);
			boss.setYRot(0);
			boss.setYBodyRot(0);
			boss.setYHeadRot(0);
			boss.setCharacter(id, false);
			boss.setNoAi(true);
			boss.setSilent(true);
			level.addFreshEntity(boss);
			height[0] = boss.getBbHeight();
			LOG.info("MS {} height={} width={}", id, boss.getBbHeight(), boss.getBbWidth());
		});
		context.waitTicks(10);
		double h = height[0];
		double dist = Math.max(3.5, h * 1.35 + 1.5);
		for (int i = 0; i < VIEWS.length; i++) {
			camera(sp, ANGLES[i], dist, h);
			context.waitTicks(8);
			context.takeScreenshot("model_" + id + "_" + VIEWS[i]);
		}
		// A swing, from the three-quarter view.
		camera(sp, 35, dist, h);
		context.waitTicks(6);
		sp.getServer().runOnServer(s -> {
			for (RogueBossEntity boss : s.overworld().getEntitiesOfClass(RogueBossEntity.class, new AABB(BX, BY, BZ, BX, BY, BZ).inflate(5))) {
				boss.swing(InteractionHand.MAIN_HAND, net.minecraft.world.item.component.SwingAnimation.DEFAULT, true);
			}
		});
		context.waitTicks(3);
		context.takeScreenshot("model_" + id + "_attack");
	}

	/** Puts the camera {@code angle} degrees around the boss (it faces +Z) and looks at its middle. */
	private static void camera(TestSingleplayerContext sp, double angle, double dist, double h) throws Exception {
		double rad = Math.toRadians(angle);
		double cx = BX + Math.sin(rad) * dist;
		double cz = BZ + Math.cos(rad) * dist;
		double eye = BY + h * 0.62;
		double lookY = BY + h * 0.5;
		double dx = BX - cx, dz = BZ - cz;
		float yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
		float pitch = (float) Math.toDegrees(Math.atan2(eye - lookY, Math.sqrt(dx * dx + dz * dz)));
		sp.getServer().runOnServer(s -> {
			ServerPlayer p = s.getPlayerList().getPlayers().get(0);
			// teleportTo places the feet; the eye sits 1.62 above them.
			p.teleportTo(s.overworld(), cx, eye - 1.62, cz, Set.of(), yaw, pitch, true);
		});
	}

	private static void floor(ServerLevel level) {
		for (int x = -24; x <= 24; x++) {
			for (int z = -24; z <= 24; z++) {
				level.setBlockAndUpdate(new BlockPos(x, (int) BY - 1, z), Blocks.STONE.defaultBlockState());
				for (int y = (int) BY; y < BY + 20; y++) {
					level.setBlockAndUpdate(new BlockPos(x, y, z), Blocks.AIR.defaultBlockState());
				}
			}
		}
	}
}
