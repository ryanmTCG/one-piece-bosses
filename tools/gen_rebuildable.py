#!/usr/bin/env python3
"""Lists the One Piece Mod's structures whose pieces carry their own boss, for the Lair Restoration Charter.

    python3 tools/gen_rebuildable.py <path to the main mod's src/main/resources>

Writes src/main/resources/opbosses/rebuildable.json: structure id -> its name and the boss character ids its
pieces bring. Only those structures can be rebuilt, since rebuilding re-places the pieces, boss and all; a
structure whose boss spawns some other way would come back empty. Run it again when the main mod's structures
change (use the same main mod version as libs/). This mod's own lairs are always rebuildable and aren't listed.
"""
import glob
import gzip
import json
import os
import re
import sys

CHARACTER = re.compile(rb'\x08\x00\x09Character(..)', re.S)


def bosses_in(path):
    """Boss character ids saved in a structure piece: a Character tag with Boss:1b in the same entity."""
    data = gzip.open(path).read()
    found = set()
    for m in CHARACTER.finditer(data):
        n = int.from_bytes(m.group(1), 'big')
        cid = data[m.end():m.end() + n].decode('utf-8', 'replace')
        around = data[max(0, m.start() - 400):m.end() + n + 400]
        if b'\x01\x00\x04Boss\x01' in around:
            found.add(cid)
    return found


def main(res):
    D = os.path.join(res, 'data/onepiece')
    sites = {}
    for sj in sorted(glob.glob(os.path.join(D, 'worldgen/structure/*.json'))):
        name = os.path.basename(sj)[:-5]
        pieces = glob.glob(os.path.join(D, 'structure', name, '**/*.nbt'), recursive=True) + glob.glob(os.path.join(D, 'structure', name + '.nbt'))
        bosses = set()
        for p in pieces:
            bosses |= bosses_in(p)
        if bosses:
            sites['onepiece:' + name] = {"name": name.replace('_', ' ').title(), "bosses": sorted(bosses)}
            print('%-28s %s' % (name, ', '.join(sorted(bosses))))
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src/main/resources/opbosses/rebuildable.json')
    with open(out, 'w') as f:
        json.dump({"_comment": "Written by tools/gen_rebuildable.py from the One Piece Mod's structures: the ones whose pieces carry their boss.",
                   "sites": sites}, f, indent=2)
        f.write('\n')
    print(len(sites), 'rebuildable main mod structures')


if __name__ == '__main__':
    main(sys.argv[1])
