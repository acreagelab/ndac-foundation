# Acknowledging NDAC

Every output of this project that uses NDAC data, equipment, computing or staff time must
acknowledge the **Nutrien Digital Agriculture Centre (NDAC), University of Saskatchewan**.
This covers papers, theses, conference talks, posters, slides, reports, shared datasets
and published code. `/export-check` blocks a publication or public release that is missing it.

> **DRAFT WORDING: replace with NDAC's official text.** Ask the NDAC data manager for the
> approved wording, logo files and any funder lines, then update this file in the
> ndac-foundation template so every new project gets the official version.

## Standard text

**Papers, theses, reports (Acknowledgements section)**

> This research used data and facilities provided by the Nutrien Digital Agriculture
> Centre (NDAC), University of Saskatchewan.

Add specifics where they apply, e.g. "...including UAV imagery collected by NDAC staff
and computing resources of the NDAC data platform."

**Talks, posters, slides**: the short line on the title or final slide, with the NDAC logo
if the template allows:

> Data and facilities: Nutrien Digital Agriculture Centre (NDAC), University of Saskatchewan

**Shared datasets**: in the dataset's `.meta.yaml` sidecar (`acknowledgement:` field) and in
the deposit record's description or funding/acknowledgement field.

**Published code**: in README.md ("Acknowledgements") and in CITATION.cff (`message:`).

## Also acknowledge (fill in for this project)

| What | Text | Where it must appear |
|---|---|---|
| Funding | TODO (grant, agency, number) | papers, theses, deposits |
| External data providers | TODO (from [data_sources.md](data_sources.md), as their licence requires) | wherever their data is used |
| Collaborators / field sites | TODO | papers, talks |
