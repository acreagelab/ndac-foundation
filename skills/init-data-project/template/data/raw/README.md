# data/raw: READ-ONLY

Raw data is never modified, renamed, or deleted. All derived results go to
`data/interim`, `data/processed`, or `data/outputs`. Nothing under `data/` is
ever committed to git (enforced by .gitignore).

Large or shared inputs stay on the shared drive and are referenced from configs as
`${DATA_ROOT}/...`; copy into `data/raw/` only small, project-specific files.
Either way, register every input in `docs/data_sources.md` when it arrives.

Because this folder is read-only, `.meta.yaml` sidecars describing raw datasets are
written to `data/processed/` (same base name). Sidecars for derived datasets sit next
to the dataset.
