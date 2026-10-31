# One Piece Bosses

A companion mod for the One Piece Mod that adds original rogue boss fights, not story characters, so there's always someone new to fight. Each rogue brings their own crew, their own lines and a phase 3 signature move.

Requires the One Piece Mod (Fabric, Minecraft 26.3, Java 25).

## The rogues

| Rogue | Tier | Fights with | Crew | Phase 3 signature | Trophy |
| --- | --- | --- | --- | --- | --- |
| **"Saltjaw" Gully Rourke**, a salvage pirate who drags his ship's anchor on a chain | 1 | Punches, then ground quakes | Scrapdeck Raiders | **Anchor Drag**: hauls you in along the chain into a flying cut | Rusted Anchor Link |
| **Corvina, the Fog Widow**, queen of a smuggling ring that only sails in fog | 2 | Smoke, then vanishing strikes | Lantern Smugglers | **Widow's Veil**: blinds everyone nearby, reappears behind you, smoke rains down | Widow's Lantern |
| **Commodore Hollis "Iron Tide" Graves**, a Navy deserter selling "protection" | 3 | Sword sweeps, then Haki | Deserter Marines | **Seastone Volley**: metal rains down and drains Devil Fruit users | Deserter's Epaulette |
| **Tsurugi, the Hollow Ronin**, an empty suit of samurai armor that still duels | 3 | Sword, then curses | none (duels alone) | **Hollow Cut**: a flying cut, and the armor's curse withers anyone close | Hollow Menpo |
| **Boilerheart Gantz**, a shipbreaker built around a ship's boiler | 4 | Fire, then quakes | Boiler Stokers | **Boiler Burst**: a scalding wave all around, then he slows down to cool (hit him then) | Cracked Boiler Core |
| **Nereus Vane, Herald of the Deep**, a fishman prophet of something far below | 5 | Pulls, then quakes | Abyssal Cultists | **Tidal Judgment**: a whirlpool drags everything in while freezing water rains down | Abyssal Conch |

## Their looks

Each rogue has their own body, with wild One Piece proportions instead of the player shape: Rourke is all barrel chest and ground-scraping forearms on tiny legs with his anchor on his back, Corvina is a stilt-legged shadow under a table-wide hat trailing a fog-grey train, Graves is a V-shaped slab with a ship's-prow chin and a torn Justice coat, Tsurugi is floating samurai armour with nothing inside, Gantz is a riveted boiler with a firebox belly, smokestacks and piston arms, and Nereus is a long-armed fishman with a dorsal fin, fin ears and a shark's jaw. They still walk, swing and look around like any mob, and coats, trains and skirts swing as they move. Each one's hitbox is sized to their body (`hitbox` in `bosses.json`).

The models and their skins come from `tools/gen_models.py` (needs Pillow): change a box or colour there and run `python3 tools/gen_models.py .`. It writes `client/RogueModels.java` and the 128x128 skins together, so they always match.

## How the fights work

- **Underneath they're the One Piece Mod's own bosses**, so everything its story bosses do, rogues do too: the health bar, phases at 66% and 33%, warning circles before attacks, Expert rage, healing when you run, Berries and XP, and Hard and Expert rematches with better prizes. Their special attacks are the main mod's boss powers.
- **Their crew** arrives when the fight starts and again at phase 2 (more on Hard and Expert), and scatters when the boss falls. Crews are the main mod's pirate NPCs, so they use its fighting styles and skins. `/npc spawn scrapdeck_raider` and friends work too.
- **Their lines**: each rogue has something to say when the fight starts, at each phase and when beaten.
- **Bounty**: a first win raises your bounty by the rogue's own amount (12M for Rourke up to 600M for Nereus Vane). Rematches add 10% of the tier value, like any boss. The paper reports first wins, and Arsenal's meito count rogues as named bosses.
- **Trophy**: each rogue drops their trophy the first time someone nearby beats them at that difficulty.

## Finding them

- **Rumor Posters** are the rogues' Wanted Posters. Use one on a block to call the rogue out. Beat them and the poster brings them back on Hard, then Expert; sneak while using it for a Normal fight.
- The main mod's pirates and Marines sometimes carry a Rumor Poster when beaten (4% for a tier 1 rogue down to 0.6% for tier 5). Which NPCs know about which rogue is `rumorFrom` in `bosses.json`.
- Creative: the **One Piece: Rogue Bosses** tab has every poster and trophy.

## Changing or adding a rogue

| File | What it does |
| --- | --- |
| `src/main/resources/opbosses/bosses.json` | **Every rogue: stats, powers, prizes, bounty, crew, lines, signature, rumors and trophy.** Same format as the main mod's `characters.json`, plus this mod's fields. |
| `src/main/resources/opbosses/crews.json` | **The crews.** Same format as the main mod's `npc_kits.json`. |
| `src/main/java/com/onepiecebosses/boss/RogueSignatures.java` | The phase 3 signature moves. A boss can also use any of the main mod's (`slash_line`, `black_hole`, `rain_fire`...). |
| `src/main/java/com/onepiecebosses/boss/RogueBossEntity.java` | The boss mob: the main mod's boss with our data, plus crew, lines and signature. |
| `src/main/java/com/onepiecebosses/compat/OnePieceBridge.java` | Every other call into the main mod. If it renames something, fix it here. |
| `tools/gen_models.py` | **Each rogue's body shape and skin.** Writes `client/RogueModels.java` and the skins. |
| `tools/gen_assets.py` | Draws the poster and trophy art and writes the item JSON. |

To add a rogue: add an entry to `bosses.json` (and a crew to `crews.json` if it has one), give it a body in `ROGUES` in `tools/gen_models.py` and its trophy a look in `TROPHIES` in `tools/gen_assets.py`, then run both (`python3 tools/gen_models.py .` and `python3 tools/gen_assets.py src/main/resources`, needs Pillow).

## Building

The One Piece Mod isn't on a maven, so build against its jar, the same way as One Piece Arsenal:

1. In the One Piece Mod, run `./gradlew build`.
2. Copy `build/libs/onepiece-0.1.0.jar` into this repo's `libs/` folder (change `onepiece_jar` in `gradle.properties` if the name differs).
3. Run `./gradlew build` here. The jar lands in `build/libs/`; put it in your `mods/` folder next to the One Piece Mod.
4. To test, run `./gradlew runClientGameTest`. A game window opens, fights every boss in a test world and closes: Rumor Poster spawn, crew waves, phase lines, signature moves, trophy, bounty (including a long-range kill), the Hard rematch and Rumor Poster drops. It fails with a list of what went wrong, and saves screenshots to `build/run/clientGameTest/screenshots`. The tests are in `src/gametest` and never go into the mod jar.

## Planned

- Lairs: a structure for each rogue out at sea, so you can stumble on them without a poster.
- Their own Devil Fruits (needs a small hook in the main mod, which only registers fruits from its own list).
- Rogue-only prizes that work with Arsenal (a Boiler Core as a material, the Hollow Ronin's blade as a meito).
