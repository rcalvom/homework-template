# homework-template

A restrained LaTeX template for university assignments.

The body keeps LaTeX's own serif and generous spacing, because a homework is paragraphs of prose, proofs and mathematics and that is what those are set in.
Code is different: listings, terminal transcripts and inline identifiers are set in **UbuntuMono**, on the same plate the [slides template](https://github.com/rcalvom/personal-slides-template) uses, with the same palette taken from `~/.config/nvim/lua/ricardo/colors.lua`.
A listing here and a listing on a slide are recognisably the same object.

On top of that: numbered problems, solutions and answers, four callouts, theorem environments, figures, D2 diagrams, tables, BibTeX citations and shell transcripts.
Both documents validate as **PDF/UA-2**, and `make check` will not let one stop.

See [`showcase.pdf`](showcase.pdf) for a compiled catalogue of the supported components.

The repository represents one assignment. Create a new repository with GitHub's **Use this template** button instead of cloning this repository directly.

```bash
gh repo create algorithms-homework-01 \
  --template rcalvom/homework-template \
  --private --clone
cd algorithms-homework-01
make
```

## Getting Started

1. Edit `fragments/metadata.tex`.
2. Replace the example files in `fragments/problems/`.
3. Include each problem explicitly from `homework.tex` in submission order.
4. Put images in `assets/img/` and D2 sources in `assets/diagrams/`.
5. Add BibTeX entries to `references.bib`.
6. Set `\TemplateStatus` to `final`, freeze the date, and run `make submission-check` before submitting the PDF.

Number problem files with room to insert new work later: `010`, `020`, `030`, and so on. Explicit `\input` lines make the submission order visible without generated manifests or engine-specific directory scanning.

## Build

| Command | Result |
|---|---|
| `make` | Build `homework.pdf`. |
| `make showcase` | Build the component catalogue. |
| `make all` | Build both PDFs. |
| `make diagrams` | Compile D2 sources to vector PDFs. |
| `make watch` | Rebuild the homework after source changes. |
| `make open` | Open `homework.pdf`. |
| `make check` | Run source, contrast, log, paper, tagging, and font checks. |
| `make check-all` | Also require PDF/UA-2 validation with veraPDF. |
| `make submission-check` | Run normal checks and reject unchanged metadata. |
| `make clean` | Remove auxiliary files while preserving PDFs. |
| `make distclean` | Also remove the two generated document PDFs. |

The build uses `lualatex` with TeX Live's restricted shell escape. `lualatex` and not `pdflatex` because loading a `.ttf` needs `fontspec`, and UbuntuMono is a `.ttf`; nothing else about the body text depends on the switch, and Latin Modern is Computer Modern's OpenType successor. `latexminted` is on the restricted command allowlist, so unrestricted `-shell-escape` is neither required nor enabled. BibTeX runs automatically. Build from the repository root because theme and asset paths are relative to it.

## Docker

No local TeX installation is needed:

```bash
docker compose run --rm homework
docker compose run --rm homework make showcase
docker compose run --rm homework make check-all
docker compose run --rm homework bash
```

The Docker image is the reference environment used by GitHub Actions. Its TeX Live image digest, `latexminted`, D2, and veraPDF versions are fixed; downloaded tools are verified by SHA-256.

Compose defaults to UID/GID 1000. On a Linux account with different IDs, prefix commands with:

```bash
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose run --rm homework
```

## Arch Linux

Install the local toolchain with:

```bash
sudo pacman -S --needed \
  make texlive-basic texlive-bin texlive-latexrecommended \
  texlive-latexextra texlive-fontsrecommended python-pygments \
  poppler qpdf d2 librsvg ghostscript
```

Optional drafting support:

```bash
sudo pacman -S --needed inotify-tools
```

The body font comes from TeX Live and needs no configuration.
UbuntuMono ships inside the repository, in `assets/fonts/`, so a clone and the container render identically; its licences travel with it in `assets/fonts/licenses/`.

The code plate's colours are a Pygments plugin in `theme/pygments/`.
Pygments resolves a style through its registry and never from a path, so it has to be installed:

```bash
pip install --user -e theme/pygments
```

The container image does it at build time.

## Problems and Solutions

```latex
\begin{problem}[10 points]{A descriptive title}
  State the problem here.
  \begin{subproblems}
    \item First part.
    \item Second part.
  \end{subproblems}

  \begin{solution}
    Write the derivation here.
  \end{solution}
\end{problem}
```

The optional argument records points. The title is required. `theorem`, `lemma`, `proposition`, `corollary`, `definition`, `remark`, `proof`, and `answer` are also available.

## Images and Diagrams

Every figure requires a visual description distinct from its caption:

```latex
\HomeworkFigure[0.7\linewidth]
  {assets/img/architecture.png}
  {System architecture.}
  {A client sends requests to a cache, which forwards misses to a server.}
  {fig:architecture}
```

D2 diagrams use the same interface and the shared accessible palette:

```latex
\HomeworkDiagram[0.85\linewidth]
  {workflow}
  {Submission workflow.}
  {Problem sources flow through lualatex and validation to the final PDF.}
  {fig:workflow}
```

Edit `assets/diagrams/workflow.d2`, then run `make diagrams`. The build converts D2 through SVG and PostScript to a vector PDF that embeds cleanly in the tagged document. Commit both the `.d2` source and generated `.pdf`; users can compile the homework without installing D2.

## Code and References

```latex
\begin{codebox}[python]{linear_search.py}
def locate(values, target):
    return next((i for i, value in enumerate(values)
                 if value == target), None)
\end{codebox}
```

The optional argument is the Pygments lexer and the mandatory one is the title, which is read verbatim so that a filename full of underscores needs no escaping.
That signature is the slides project's, deliberately: a fragment written for one template reads the same in the other.

`codeplain` is the same plate without the title bar or line numbers, and `terminal` sets a shell transcript.
Every colour in the syntax style is held to 4.5:1 against the plate by `make check-contrast` — none of the styles Pygments ships would pass, the best of them missing AA by a hair.

Keep lines short enough not to wrap, and accompany code with prose that explains indentation-dependent behaviour for readers using assistive technology.

Use standard Natbib commands such as `\citet{key}` and `\citep{key}`. Add records to `references.bib`; the Makefile invokes BibTeX and performs enough LaTeX passes to resolve references.

## Layout

```text
homework.tex                 assignment assembly
showcase.tex                 component catalogue
fragments/metadata.tex       editable assignment metadata
fragments/problems/          one file per problem
fragments/showcase/          catalogue content
assets/img/                  figures
assets/diagrams/             D2 sources and generated PDFs
theme/                       typography, palette, boxes, code, layouts
scripts/                     automated checks
```

The generated `homework.pdf` and `showcase.pdf` are tracked so the repository can be previewed directly on GitHub. `make clean` preserves them; `make distclean` removes them.

## License

The template is available under the MIT License. A repository created from it inherits `LICENSE`; review or replace that file if your assignment content should not be published under MIT. Course materials, imported images, and bibliography entries may have separate licensing requirements.
