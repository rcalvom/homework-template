# Repository Guidelines

## Project Scope

This repository is a public LaTeX template for one university assignment per repository. The generated `homework.pdf` and `showcase.pdf` are tracked artifacts. Both documents use US Letter paper and English document strings.
The body is Latin Modern, LaTeX's own serif; only the typewriter family is replaced, with UbuntuMono loaded from `assets/fonts/` through `fontspec`.
That is why the engine is `lualatex` and not `pdflatex`.

## Repository Structure

- `homework.tex` assembles an assignment.
- `fragments/metadata.tex` contains assignment metadata and public placeholders.
- `fragments/problems/` contains one numbered source file per problem.
- `showcase.tex` and `fragments/showcase/` are living documentation for every supported component.
- `theme/` contains the visual system and public LaTeX environments.
- `assets/img/` contains ordinary figures.
- `assets/diagrams/` contains D2 sources and committed generated PDFs.
- `scripts/` contains source, log, PDF integrity, contrast, metadata, and PDF/UA checks.
- `references.bib` contains BibTeX references.

## Editing Guidelines

- Write content, code comments, documentation, and commit messages in English.
- Keep metadata in `fragments/metadata.tex`; do not put personal data in the reusable template.
- Add problems as `fragments/problems/010-name.tex`, `020-name.tex`, and so on, then include them explicitly from `homework.tex`.
- Preserve the restrained light design, the standard `article` class, and the two-family split: LaTeX's serif for prose and mathematics, UbuntuMono for anything that is code.
- Do not set body text in the monospace face. The slides project is all-monospace because a slide holds a sentence; a homework holds proofs.
- A document is a folder: `\DocFolder` inputs every `.tex` in one, in name order, so adding a problem is creating a file. Do not add `\input` lines to `homework.tex` or `showcase.tex`.
- Every `\HomeworkFigure` and `\HomeworkDiagram` must have a meaningful caption, alt text, and label.
- Edit D2 sources, not generated SVG or PostScript files. Run `make diagrams` and commit the generated PDF with its source.
- Do not commit LaTeX auxiliary files or minted caches.
- Keep `clean` non-destructive: it must preserve tracked PDFs and diagram outputs.

## Validation

Run the normal local gate after source or layout changes. It rebuilds both PDFs and checks them with Poppler and qpdf:

```bash
make check
```

Run the full reference gate, including veraPDF, through Docker before publishing theme changes:

```bash
docker compose run --rm homework make check-all
```

Before submitting a real assignment, replace every metadata placeholder, freeze the date, and run:

```bash
make submission-check
```

Inspect the complete generated PDF visually. A successful command does not replace checking page breaks, mathematical notation, figure placement, and the accuracy of the work.
