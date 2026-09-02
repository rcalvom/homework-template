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
- Diagrams compile through PostScript (`rsvg-convert -f ps` then `ps2pdf` with a pinned `SOURCE_DATE_EPOCH`), not through `rsvg-convert -f pdf`.
  The direct route keeps the labels in the text layer but writes different bytes on every run, which breaks the CI check that a committed diagram still matches its source.
  The PostScript route is byte-reproducible and outlines the glyphs, so a diagram contributes nothing to the text layer and its `\Description` is the only thing a screen reader gets.
  Both halves of that trade are real; do not flip it without deciding which one matters more.
- A document is a folder: `\DocFolder` inputs every `.tex` in one, in name order, so adding a problem is creating a file. Do not add `\input` lines to `homework.tex` or `showcase.tex`.
- Every `\HomeworkFigure` and `\HomeworkDiagram` must have a meaningful caption, alt text, and label.
- Edit D2 sources, not generated SVG or PostScript files. Run `make diagrams` and commit the generated PDF with its source.
- Do not commit LaTeX auxiliary files or minted caches.
- Keep `clean` non-destructive: it must preserve tracked PDFs and diagram outputs.

## Design Decisions Already Made

These were chosen deliberately, several of them after trying the alternative.
They are recorded so a later session improves the template instead of relitigating it.

- **Typography is split, and only the mono half is ours.**
  The body is LaTeX's own serif because a homework is paragraphs of prose, proofs and mathematics.
  UbuntuMono is for code, terminal transcripts and inline identifiers only.
  Do not set body text in the monospace face: the slides project is all-monospace because a slide holds a sentence, and a homework holds proofs.
- **The title block is centred**, in the manner of a journal article, chosen over a left rail, a mono kicker and a tinted plate.
  Title, what the assignment is, who is handing it in, the course, the date, then instructor and collaborators last and smallest.
- **Headings are accent blue.**
  Setting them in ink was tried and reverted: with black headings the accent survives only on callout labels, the code tab and links, and the page reads more sober but less like the rest of the family.
- **The running head is two anchors** -- course left, assignment right, with an accent hairline under them.
  A centred version was tried and rejected: a running head is a locator, and two anchors at the outer edges are easier to find with a thumb than one line in the middle.
- **The accent goes on the running rule, never on the running head's text.**
  The headings are accent; a coloured running head would read as loud as a heading on every page while saying what the reader already knows.
- **The rule under the title block is `\rzheadrule`**, two fifths of the text width.
  It is one number on purpose, so the next opinion about its length costs one edit.
- **The code plate is the slides project's**, down to the signature: `\begin{codebox}[lexer]{title}`, optional lexer and mandatory title.
  A fragment written for one template then reads the same in the other, which is the point of the two sharing a look.
  Its title is a verbatim argument because filenames in a homework are full of underscores.
- **List markers are accent, and the colour lives in `\labelitemi` and `\labelenumi`.**
  enumitem's `font=` key is shorter and does the same thing on LaTeX2e 2026-06-01, which is what the container runs.
  It does nothing on the 2025-11-01 release Arch ships, where the tagged-list code builds a standard list's label outside enumitem's reach -- so the same source rendered blue markers in the container and black ones on the host.
  `label=` fails there too, for the same reason; only a list enumitem owns through `\newlist`, such as `subproblems`, honours either key.
  Do not shorten this back to `font=` without building on both releases.
- **Callouts have no frame, only a rail and a tint.**
  A box inside a page of prose should interrupt as little as it can, and a page of three framed boxes looks like a form.
  Every one of them carries an icon and a word as well as a colour, so a reader in greyscale still gets which kind it is.

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
