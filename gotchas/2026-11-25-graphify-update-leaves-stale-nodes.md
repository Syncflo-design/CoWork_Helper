# graphify --update: re-read notes keep their old nodes, and the two machines run different versions

**Date:** 2026-11-25
**Where:** `graphify-out/` in this repo, updated from the Dell after pulling the other machine's notes.

## What bit us

1. **Stale nodes survive the merge.** `build_merge` replaces a re-read file's old nodes per tier
   (AST or semantic). The semantic pass never stamps its tier, so the merge falls back to
   "has an `L<line>` source_location = AST". Extraction agents that fill in line numbers are then
   read as AST, and the note's old semantic nodes stay in the graph beside the new ones
   (1,948 nodes instead of 1,895; 82 "minted by two different files" warnings).
2. **`root='.'` does not match absolute paths.** Agents write absolute `source_file` values; with a
   relative root the old `sites/ardmore.md` nodes are not recognised as the same file.
3. **A note that mentions another file can replace that file's own node** when the ids collide.
4. **`to_json` without `community_labels`** leaves old nodes with their previous community name
   and new nodes with none.
5. **Version gap.** The Dell has graphify 0.9.32; the graph in git was last written by 0.9.97.
   0.9.32 deletes the other version's `cache/ast/` folder and drops `schema_version` /
   `graphify_version` from graph.json. AST cache is free to rebuild, so nothing is lost, but the
   two machines should run the same version.
6. **Notes pushed without a graph update** are picked up by the next `--update` on any machine
   (the commit hook only re-reads code, not notes).

## Fix (what the 25 Nov run did)

- Stamp `_origin: "semantic"` on every node and edge from the agents before merging.
- Pass the absolute repo path as `root` to `build_merge`, `build_from_json` and `save_manifest`.
- Drop new semantic nodes whose id already belongs to a file that was not re-read.
- Call `to_json(..., community_labels=labels)` after naming the communities.
- Check afterwards: 0 "minted by two different files" warnings, 0 nodes with an absolute
  `source_file`, every node named, `detect_incremental` reports 0 pending.

## Still open

Bring both machines to the same graphify version (`uv tool install --upgrade graphifyy`).
