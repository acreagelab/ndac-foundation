# Diagrams

| Source (edit this) | Rendered | What |
|---|---|---|
| [pipeline.mmd](pipeline.mmd) | pipeline.png | Data and processing pipeline, grouped by security zone |
| [plan_gantt.mmd](plan_gantt.mmd) | plan_gantt.png | Project timeline |
| [concept.mmd](concept.mmd) | concept.png | Conceptual framework |

Render all: `python scripts/render_diagrams.py` (needs Node.js; renders locally).
Never use online Mermaid renderers for these: they send the diagram text to an outside
server, and the pipeline shows data sources and security zones.

Rendered PNGs are committed so slides and reports can use them. Re-render after every edit.
Before a PNG goes into a talk or paper, it goes through `/export-check` like any other figure.
