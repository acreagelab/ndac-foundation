# Data source register: <PROJECT_NAME>

One row per input dataset, added **when the data arrives**, before it is used.
This is what the DMP, ethics/REB, data-sharing agreements and reviewers ask for.
Checksums: `python -c "from src.common import sha256_file; print(sha256_file(r'PATH'))"`.

| ID | Dataset | Provider / contact | How obtained (URL, request, agreement) | Licence or DSA terms | Security zone | Location (`${DATA_ROOT}/...` or `data/raw/...`) | Version / date acquired | SHA-256 (or file count) | Acknowledgement required | Used by |
|---|---|---|---|---|---|---|---|---|---|---|
| D1 | TODO | | | | A_Public / B_Internal / C_Limited / D_Restric | | | | NDAC + provider | `subprojects/TODO` |

Rules:
- The project's security zone is the highest zone of any row here.
- Data with personal or Indigenous-community information: flag for governance review
  before it lands in `data/raw/` (see CLAUDE.md, Sensitive data).
- Each dataset shared outside the project gets a `.meta.yaml` sidecar
  ([template](metadata-template.meta.yaml)).
