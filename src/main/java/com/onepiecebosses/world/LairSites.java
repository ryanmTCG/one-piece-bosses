package com.onepiecebosses.world;

import com.mojang.datafixers.util.Either;
import com.onepiecebosses.BossesMod;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.TerrainAdjustment;
import net.minecraft.world.level.levelgen.structure.pieces.StructurePiecesBuilder;

/**
 * Keeps our lairs off mountains and out of the sea (ryan 2026-11-01: "the lairs keep spawning in mountains").
 * Vanilla only checks the biome at a structure's middle, and our lairs are 70-120 blocks across, so a desert fort could
 * run up the side of the mountain next door. This samples the ground on a 5x5 grid over the lair's real footprint and,
 * if it's too steep or too wet (or, for a sea lair, too dry), slides the whole lair to the nearest spot within
 * {@link #MAX_SHIFT} blocks that fits. If none does, the lair isn't built there and the next spot in the set gets it.
 * Hooked into Structure.findValidGenerationPoint (LairSiteMixin), so /locate agrees with world generation.
 * -Dopbosses.siteRules=false turns it off.
 */
public final class LairSites {
	private LairSites() {}

	private static final boolean ENABLED = !"false".equals(System.getProperty("opbosses.siteRules"));
	private static final boolean DEBUG = Boolean.getBoolean("opbosses.siteDebug");

	private static final int GRID = 5;
	/** Most a land lair's ground may rise and fall across its footprint (the top 2 and bottom 2 samples are ignored). */
	public static final int MAX_SPREAD = 10;
	/** Most of the 25 samples under a land lair that may be water. */
	private static final int MAX_WET = 3;
	/** Fewest of the 25 samples under a sea lair that must be water (most of it: reef and beach lairs keep a bit of shore). */
	private static final int MIN_WET_SEA = 15;
	private static final int STEP = 16;
	/** A chunk looks 8 chunks around for structure starts: our widest lair (~120) can move ~48 blocks and stay seen. */
	private static final int MAX_SHIFT = 48;

	public static Optional<Structure.GenerationStub> filter(Structure structure, Structure.GenerationContext ctx,
			Optional<Structure.GenerationStub> found) {
		if (!ENABLED || found.isEmpty()) return found;
		Identifier id = ctx.registryAccess().lookupOrThrow(Registries.STRUCTURE).getKey(structure);
		if (id == null || !id.getNamespace().equals(BossesMod.MOD_ID)) return found;
		boolean sea = structure.terrainAdaptation() == TerrainAdjustment.NONE;

		Structure.GenerationStub stub = found.get();
		// Lay the pieces out once for the real footprint; the builder is handed on so they aren't laid out twice.
		StructurePiecesBuilder builder = stub.getPiecesBuilder();
		if (builder.isEmpty()) return found;
		BoundingBox box = builder.getBoundingBox();
		BlockPos start = stub.position();
		int shift = Math.max(0, Math.min(MAX_SHIFT, 128 - 16 - Math.max(box.getXSpan(), box.getZSpan()) / 2));

		for (int[] o : spiral(shift)) {
			Ground g = sample(ctx, box.moved(o[0], 0, o[1]));
			boolean fits = sea ? g.wet >= MIN_WET_SEA : g.wet <= MAX_WET && g.spread() <= MAX_SPREAD;
			if (DEBUG) BossesMod.LOGGER.info("lair site {} at {} {} offset {},{}: wet {} spread {} -> {}", id.getPath(),
					start.getX(), start.getZ(), o[0], o[1], g.wet, g.spread(), fits);
			if (!fits) continue;
			int dy = 0;
			if (!sea) {
				// Sit the lair on the ground under the footprint (a little low, so the yard cuts into the slope rather
				// than floating over it), not on whatever the single column under its start point was.
				int now = ctx.chunkGenerator().getFirstFreeHeight(start.getX(), start.getZ(), Heightmap.Types.WORLD_SURFACE_WG,
						ctx.heightAccessor(), ctx.randomState());
				dy = Math.max(-12, Math.min(12, g.low() - now));
			}
			if (o[0] != 0 || o[1] != 0 || dy != 0) {
				for (StructurePiece piece : builder.build().pieces()) piece.move(o[0], dy, o[1]);
				start = start.offset(o[0], dy, o[1]);
			}
			return Optional.of(new Structure.GenerationStub(start, Either.right(builder)));
		}
		return Optional.empty();
	}

	private record Ground(List<Integer> dry, int wet) {
		/** Rise and fall of the dry ground, ignoring the two highest and two lowest samples (a tree stump, a gully). */
		int spread() {
			return dry.size() < 5 ? 0 : dry.get(dry.size() - 3) - dry.get(2);
		}

		/** The lower third of the dry ground. */
		int low() {
			return dry.isEmpty() ? 0 : dry.get(dry.size() * 3 / 10);
		}
	}

	private static Ground sample(Structure.GenerationContext ctx, BoundingBox box) {
		int sea = ctx.chunkGenerator().getSeaLevel();
		int x0 = box.minX() + 2, x1 = box.maxX() - 2, z0 = box.minZ() + 2, z1 = box.maxZ() - 2;
		List<Integer> dry = new ArrayList<>();
		int wet = 0;
		for (int i = 0; i < GRID; i++) {
			for (int j = 0; j < GRID; j++) {
				int x = x0 + (x1 - x0) * i / (GRID - 1), z = z0 + (z1 - z0) * j / (GRID - 1);
				int h = ctx.chunkGenerator().getFirstFreeHeight(x, z, Heightmap.Types.OCEAN_FLOOR_WG, ctx.heightAccessor(), ctx.randomState());
				if (h >= sea) dry.add(h);
				else wet++;
			}
		}
		Collections.sort(dry);
		return new Ground(dry, wet);
	}

	/** Offsets to try, the original spot first, then rings out to `max` blocks. */
	private static List<int[]> spiral(int max) {
		List<int[]> out = new ArrayList<>();
		out.add(new int[] {0, 0});
		for (int r = STEP; r <= max; r += STEP) {
			for (int dx = -r; dx <= r; dx += STEP) {
				for (int dz = -r; dz <= r; dz += STEP) {
					if (Math.max(Math.abs(dx), Math.abs(dz)) == r) out.add(new int[] {dx, dz});
				}
			}
		}
		return out;
	}
}
