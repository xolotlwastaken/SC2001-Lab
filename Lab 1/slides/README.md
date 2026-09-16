# Presentation files

- `SC2001_Project_1.pptx`: editable PowerPoint, 16:9, eight main slides plus seven Q&A backups. Speaker notes are embedded on every slide.
- `SC2001_Project_1.pdf`: matching PDF for viewing or presenting without PowerPoint; PDF pages do not include the speaker notes.
- `blueprint.md`: full eight-minute script, transitions, timing, and Q&A preparation.
- `measured_content.md`: result statements generated from the full experiment.

Present slides 1–8 in eight minutes; reserve two minutes for questions. Use backup slides 9–15 only as needed. Add your team names and lab group to the title slide before the lab. Open Presenter View or the Notes pane in PowerPoint to see the explanations. The deck embeds the figures, so it does not require an internet connection or external image files.

The slide source is `scripts/create_slides.py` (requires python-pptx and Pillow). It reads the existing figures, summary CSV, selection JSON, findings, and blueprint. The extra figure `figures/deck_cpu_10m.png` shows the 10-million-element subset of the coarse CPU sweep; the full four-size plot is included as Backup A.

Checks performed: all 15 slides have speaker notes; shape bounds checked; PDF has 15 pages; all PDF pages visually reviewed; title and chart labels inspected. Arial is used for body text, Menlo for code. The PDF embeds its rendered fonts.
