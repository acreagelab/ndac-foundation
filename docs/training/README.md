# Training material

Slides for onboarding students and partners (PNG, ~16:9, 2352 px wide):

| Slide | File | Source (edit this) |
|---|---|---|
| 1 · Get ready (once per person) | [slide1_get_ready.png](slide1_get_ready.png) | [slide1_get_ready.mmd](slide1_get_ready.mmd) |
| 2 · Every research project | [slide2_every_project.png](slide2_every_project.png) | [slide2_every_project.mmd](slide2_every_project.mmd) |
| 3 · Using it on Fir (Alliance HPC) | [slide3_fir.png](slide3_fir.png) | [slide3_fir.mmd](slide3_fir.mmd) |
| 4 · On Fir, Claude picks node and storage | [slide4_fir_smart.png](slide4_fir_smart.png) | [slide4_fir_smart.mmd](slide4_fir_smart.mmd) |

Re-render after editing a .mmd (local, needs Node.js; uses the installed Chrome):

```powershell
'{"executablePath":"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe","headless":true}' | Out-File -Encoding ascii $env:TEMP\pp.json
$env:PUPPETEER_SKIP_DOWNLOAD = "1"
npx --yes @mermaid-js/mermaid-cli@12.2.0 -i slide1_get_ready.mmd -o slide1_get_ready.png -p $env:TEMP\pp.json --backgroundColor white --scale 3
```

For Edge, use `C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe` as the path
(backslashes doubled, because it goes inside JSON).
Never write `\n...` inside a Windows path in a label (e.g. `...\Projects\ndac-foundation`):
Mermaid renders it as a line break, even when escaped.
