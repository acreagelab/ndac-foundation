# Training material

| File | What |
|---|---|
| [workflow_overview.png](workflow_overview.png) | One-slide overview of the NDAC project workflow with Claude Code |
| [workflow_overview.mmd](workflow_overview.mmd) | Its Mermaid source: edit this, then re-render |

Re-render (local, needs Node.js; uses the installed Chrome or Edge):

```powershell
'{"executablePath":"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe","headless":true}' | Out-File -Encoding ascii $env:TEMP\pp.json
$env:PUPPETEER_SKIP_DOWNLOAD = "1"
npx --yes @mermaid-js/mermaid-cli@12.2.0 -i workflow_overview.mmd -o workflow_overview.png -p $env:TEMP\pp.json --backgroundColor white --scale 3
```

For Edge, use `C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe` as the path.
