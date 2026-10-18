# Maintain one curriculum and regenerate both guides

Do not edit `packages/`, `builder/`, `.claude-plugin/marketplace.json` or
`release-manifest.json` by hand. They are generated artifacts. Edit templates,
profiles or the selected curriculum source, build to a fresh external directory,
review the diff and replace the generated directories as a unit. Delete obsolete
generated files as part of replacement; otherwise the verifier rejects them.

For this default distribution, the source remains the public educator curriculum.
The kit stores a pinned imported snapshot, not a new lesson-authoring stream.
Corrections to those lessons belong in the curriculum project first. A school that
uses its own curriculum maintains its own selected source folder instead.

## Import a new public BLI curriculum release

Obtain and inspect a clean checkout of the public
https://github.com/BigLeverVentures/bli-for-educators repository. Record its full
commit SHA. From this kit, run (replace both paths and the SHA):

```sh
python3 -B tools/import_curriculum.py /path/to/public-curriculum /tmp/reviewed-curriculum-next --commit FULL_COMMIT_SHA
```

The destination must not exist. The importer uses the public release manifest's
resource list, selected educator teaching references and original license. It
checks selected source hashes and recognizes only exact reviewed license texts, combines the material, and resolves relative links
to pinned public source URLs. The source must match the recorded Git commit. Select
the genuine public repository yourself; local hashes do not authenticate a remote
repository's identity. It does not crawl links, read the private Institute
repository, or fetch anything at build time. Review the resulting diff and copy the
reviewed folder over `curriculum/big-lever/`, removing obsolete files. Set the
profile's snapshot date to the new catalog date and increment its release version.

The initial snapshot includes 64 lesson pages plus the glossary. This is a dated
inventory, not a hardcoded teaching sequence or requirement to take all lessons.
Future full courses have no invented bodies in the imported collection.

## Rebuild the default distribution

```sh
python3 -B tools/build.py --profile profiles/big-lever.json --output /tmp/reviewed-guide-release-next
```

Compare the output with the committed generated artifacts. After review, replace
`packages/`, `builder/`, `.claude-plugin/marketplace.json` and
`release-manifest.json` from that output. Keep README, source and documentation.
Then run:

```sh
python3 -B tools/test_build.py
python3 -B tools/verify.py
```

Where Claude CLI is installed, also run `claude plugin validate` against the root
marketplace and each generated plugin directory. That checks package structure,
not recipient access or coaching. Use [evaluation](evaluation.md) for those checks.

Give each published update a version and explain changes to curriculum dates and
learner behavior. Update the educator-owned provider publication and
verify a learner actually receives it. A provider may need an explicit marketplace
sync or reinstall. Do not claim automatic live curriculum updates.

Release-manifest hashes cover generated files and their selected inputs. The
verifier independently regenerates expected artifacts and compares bytes, rather
than trusting a possibly stale or edited checksum list alone.

If an upstream license notice changes, the importer stops for review. Review the complete notice and preserved prior permissions before adding its SHA-256 to `REVIEWED_LICENSES` in `tools/import_curriculum.py`; a matching title or a historical CC mention is insufficient. Existing historical releases keep their original terms.
