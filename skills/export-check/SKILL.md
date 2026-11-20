---
name: export-check
description: Pre-export disclosure control for NDAC data. Run before any dataset, map, figure, table, diagram, notebook, paper, poster, slide deck or repository leaves the secure environment (email, publication, GitHub, presentation, chat paste, committee slides, data deposit). Checks prairie re-identification vectors, small cells, security-zone crossings, OCAP®/CARE, NDAC acknowledgement, and licence/deposit requirements.
---

# Export check: disclosure control

Run against the specific artifact(s) about to leave the secure environment. The outcome
is a PASS or BLOCKED verdict per artifact, never "probably fine".

## Procedure

1. **Scan.** Launch the `pii-scanner` agent on the export candidate(s). For notebooks,
   include cell outputs; for repositories, include `git log --all --name-only` so files
   committed in the past are checked too.

2. **Identifier columns.** In tables and shapefile DBFs: `ppid`, `lld`, `quarter`,
   `section`, `township`, `range`, `meridian`, farm/operator names, addresses.
   Any hit → BLOCKED until dropped or aggregated.

3. **Small cells.** Any aggregate backed by < 5 farms/operators (check `Farms`/count
   columns) → suppress the cell or coarsen the aggregation.

4. **Coordinate precision.** Not finer than the upstream provider publishes (e.g., PPMN
   withholds survey locations; ISC parcel geometry implies ownership). Field boundaries
   joined to quarter sections count as identifying. Maps: does the extent or outline
   reveal a single operator's fields?

5. **Zone check.** Compare the source's security zone (`D_Restric > C_Limited >
   B_Internal > A_Public`, from CLAUDE.md and `docs/data_sources.md`) with the
   destination. Downward crossings need a documented justification in the metadata
   sidecar and sign-off from the project's data steward (named in CLAUDE.md; NDAC data
   manager by default). Don't record sign-off on someone's behalf: ask the user to confirm
   it has been given.

6. **OCAP® / CARE.** Indigenous community data → governance review, full stop. No
   automated pass exists for this category.

7. **Acknowledgement.** Papers, theses, talks, posters, slides, reports, shared datasets
   and published repos must acknowledge NDAC using the wording in the project's
   `docs/ACKNOWLEDGEMENT.md`, plus any funders and data providers listed there and in
   `docs/data_sources.md` whose licence requires it. Missing → BLOCKED (minimal fix: add
   the line).

8. **Outbound repos and publications.** LICENSE present, CITATION.cff filled, citation/DOI
   plan, deposit record (see `usask-superpowers-data:data-deposit-and-sharing`), no data
   files in git history unless cleared, no credentials in history, notebook outputs stripped.
   Remotes outside USask additionally need the push-guard override
   (`git config ndac.pushApproved true`), set by the user only after this check passes.

9. **Record the decision.** Write the verdict and justification into the dataset's
   `.meta.yaml` sidecar (`restrictions` field); use the `metadata-tagger` agent if the
   sidecar is missing. For non-dataset artifacts, log it in PROGRESS_REPORT.md.

## Output

Per artifact: **PASS** (with conditions applied) or **BLOCKED** (with the specific
failing check and the minimal change that would clear it).
