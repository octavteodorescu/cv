# cv

Single source for my CV and personal site at https://cv.oteelab.org.

- `cv.yaml` - the one source of truth (all content).
- `build.py` - renders the site HTML, `llms.txt`, embedded JSON-LD, a profile README, and a document markdown.
- GitHub Actions builds the site and generates the downloadable **PDF** and **Word** document from `cv.yaml` on every push, then deploys to GitHub Pages.

Edit `cv.yaml`, push, and every surface regenerates.
