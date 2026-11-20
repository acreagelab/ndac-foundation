# data/raw — READ-ONLY

Raw data is never modified, renamed, or deleted. All derived results go to
`data/interim`, `data/processed`, or `data/outputs`. Nothing under `data/` is
ever committed to git (enforced by .gitignore). Each dataset placed here should
get a `<name>.meta.yaml` sidecar (see docs/metadata-template.meta.yaml) written
to `data/processed/`.
