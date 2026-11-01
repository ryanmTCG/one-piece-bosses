package com.onepiecebosses.world;

import com.onepiecebosses.BossesMod;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.feature.AbstractHugeMushroomFeature;
import net.minecraft.world.level.levelgen.feature.BambooFeature;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.TreeFeature;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.StructureStart;

/**
 * Keeps the world's trees out of our lairs. Trees are placed after structures, so a jungle tree could grow up through a
 * lair's garden, its yard or a crewman standing there (the Merveille and Gold Island crews ended up in leaves). While a
 * chunk is decorated, the lairs touching it are noted here, and FeaturePlacerMixin turns down any tree, giant
 * mushroom or bamboo whose root is inside one of them (or within a few blocks of its edge).
 */
public final class LairGrowth {
	private LairGrowth() {}

	private static final int PAD = 4;
	private static final ThreadLocal<List<BoundingBox>> LAIRS = new ThreadLocal<>();

	/** Called as a chunk's decoration starts (ChunkGeneratorMixin). */
	public static void begin(WorldGenLevel level, ChunkPos chunk, StructureManager structures) {
		var registry = level.registryAccess().lookupOrThrow(Registries.STRUCTURE);
		List<BoundingBox> boxes = new ArrayList<>();
		for (StructureStart start : structures.startsForStructure(chunk.x(), chunk.z(), s -> {
			Identifier id = registry.getKey(s);
			return id != null && id.getNamespace().equals(BossesMod.MOD_ID);
		})) {
			if (start.isValid()) boxes.add(start.getBoundingBox().inflatedBy(PAD));
		}
		LAIRS.set(boxes.isEmpty() ? null : boxes);
	}

	public static void end() {
		LAIRS.remove();
	}

	/** True if this feature mustn't grow at pos: it's a tree (or the like) and pos is in a lair. */
	public static boolean blocked(Feature feature, BlockPos pos) {
		List<BoundingBox> boxes = LAIRS.get();
		if (boxes == null) return false;
		if (!(feature instanceof TreeFeature || feature instanceof AbstractHugeMushroomFeature || feature instanceof BambooFeature)) return false;
		for (BoundingBox box : boxes) {
			if (box.minX() <= pos.getX() && pos.getX() <= box.maxX() && box.minZ() <= pos.getZ() && pos.getZ() <= box.maxZ()) return true;
		}
		return false;
	}
}
