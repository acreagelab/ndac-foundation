# Data management plan: <PROJECT_NAME>

Working copy of the project's DMP, following the Tri-Agency RDM Policy and the
Alliance (Portage) DMP Assistant sections. If a funder requires a DMP, write the
official one in DMP Assistant (https://dmp-pgd.ca) and keep this file in step with it.
Ask Claude for the `usask-superpowers-data:data-management-plan` skill to draft or review it.

| | |
|---|---|
| Funder / grant | TODO |
| Data steward | TODO |
| Last reviewed | <DATE> |

## 1. Data collection
What data, formats, volumes, how collected. Inputs: [data_sources.md](data_sources.md).

## 2. Documentation and metadata
`.meta.yaml` sidecars ([template](metadata-template.meta.yaml)), README files,
run manifests next to every result, [experiments.md](experiments.md).

## 3. Storage and backup
Working data on the NDAC shared drive (`DATA_ROOT`), security zone TODO. Code in git
(USask GitLab or approved remote). Backup: TODO (who, how often, where).

## 4. Preservation
What is kept after the project, where (e.g. FRDR, Borealis, USask repository), for how long.

## 5. Sharing and reuse
What can be shared, at what aggregation, under what licence; embargo; DOI plan.
Outputs acknowledge NDAC ([ACKNOWLEDGEMENT.md](ACKNOWLEDGEMENT.md)).

## 6. Responsibilities and resources
Who does what (see [contributions.md](contributions.md)); storage and staff costs.

## 7. Ethics and legal compliance
REB approval (number, if human participants), data-sharing agreements, consent limits,
OCAP®/CARE for Indigenous data, producer confidentiality (C_Limited field-level data).
