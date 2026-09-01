# =====================================================================
# homework-template
#
# Common targets:
#   make                  build homework.pdf
#   make showcase         build showcase.pdf
#   make all              build both PDFs
#   make diagrams         rebuild D2 diagrams
#   make watch            rebuild homework.pdf after source changes
#   make check            run checks available in a normal local setup
#   make check-all        also require PDF/UA-2 validation with veraPDF
#   make submission-check fail if template metadata remains
#   make clean            remove auxiliary files, preserving tracked PDFs
#   make distclean        also remove homework.pdf and showcase.pdf
# =====================================================================

MAIN       := homework
SHOWCASE   := showcase
PDF_ENGINE := pdflatex
TEXMFVAR   := /tmp/texmf-var
TEXFLAGS   := -interaction=nonstopmode -halt-on-error -file-line-error
TEXENV     := TEXMFVAR=$(TEXMFVAR) TERM=$${TERM:-dumb}

PDF          := $(MAIN).pdf
SHOWCASE_PDF := $(SHOWCASE).pdf

THEME_FILES    := $(shell find theme -type f -name '*.sty' | sort)
FRAGMENT_FILES := $(shell find fragments -type f -name '*.tex' | sort)
IMAGE_FILES    := $(shell find assets/img -type f | sort)
D2_SOURCES     := $(filter-out assets/diagrams/_%,$(wildcard assets/diagrams/*.d2))
D2_PDFS        := $(D2_SOURCES:.d2=.pdf)

SOURCES := $(MAIN).tex references.bib $(THEME_FILES) $(FRAGMENT_FILES) \
           $(IMAGE_FILES) $(D2_PDFS) Makefile
SHOWCASE_SOURCES := $(SHOWCASE).tex references.bib $(THEME_FILES) \
                    $(FRAGMENT_FILES) $(IMAGE_FILES) $(D2_PDFS) Makefile

LATEX_AUX_FILES := *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk \
                   *.synctex.gz *.bbl *.blg *.bcf *.run.xml *.listing
MINTED_FILES    := _minted* _*.*.minted *.pyg *.pygtex *.pygstyle
TAG_FILES       := *-luamml-mathml.html
PYC_FILES       := scripts/__pycache__
D2_SCRATCH      := assets/diagrams/*.svg assets/diagrams/*.ps \
                   assets/diagrams/*.tmp.pdf

VERAPDF ?= verapdf

.DEFAULT_GOAL := pdf

.PHONY: all pdf showcase diagrams watch open check check-homework check-all check-sources \
        check-logs check-pdf check-contrast check-pdfua submission-check \
        clean distclean docker-build docker-shell help

all: pdf showcase

pdf: $(PDF)

showcase: $(SHOWCASE_PDF)

define build
	@mkdir -p $(TEXMFVAR)
	@rm -f $(1).pdf
	@echo ">> $(1): LaTeX pass 1"
	@env $(TEXENV) $(PDF_ENGINE) $(TEXFLAGS) $(2).tex >/dev/null || { \
	  python3 scripts/check-logs.py $(1).log || true; rm -f $(1).pdf; exit 1; }
	@if grep -q '\\citation' $(1).aux; then \
	  echo ">> $(1): BibTeX"; \
	  env $(TEXENV) bibtex $(1) >/dev/null || { rm -f $(1).pdf; exit 1; }; \
	else \
	  : > $(1).bbl; \
	fi
	@n=2; while [ $$n -le 5 ]; do \
	  echo ">> $(1): LaTeX pass $$n"; \
	  env $(TEXENV) $(PDF_ENGINE) $(TEXFLAGS) $(2).tex >/dev/null || { \
	    python3 scripts/check-logs.py $(1).log || true; rm -f $(1).pdf; exit 1; }; \
	  if [ $$n -ge 3 ] && ! grep -qE \
	    "Rerun to get|Label\\(s\\) may have changed" $(1).log; then break; fi; \
	  n=$$((n + 1)); \
	done
	@python3 scripts/check-logs.py $(1).log || { rm -f $(1).pdf; exit 1; }
endef

$(PDF): $(SOURCES)
	$(call build,$(MAIN),$(MAIN))

$(SHOWCASE_PDF): $(SHOWCASE_SOURCES)
	$(call build,$(SHOWCASE),$(SHOWCASE))

assets/diagrams/%.pdf: assets/diagrams/%.d2 assets/diagrams/_theme.d2
	@command -v d2 >/dev/null 2>&1 || { \
	  echo "d2 not found -- install it (Arch: pacman -S d2)"; exit 1; }
	@command -v rsvg-convert >/dev/null 2>&1 || { \
	  echo "rsvg-convert not found -- install it (Arch: pacman -S librsvg)"; exit 1; }
	@command -v ps2pdf >/dev/null 2>&1 || { \
	  echo "ps2pdf not found -- install it (Arch: pacman -S ghostscript)"; exit 1; }
	@echo ">> d2: $<"
	@cd assets/diagrams && d2 $(notdir $<) $*.svg >/dev/null
	@rsvg-convert -f ps -o assets/diagrams/$*.ps assets/diagrams/$*.svg
	@SOURCE_DATE_EPOCH=946684800 ps2pdf -dEPSCrop assets/diagrams/$*.ps \
	  assets/diagrams/$*.tmp.pdf
	@mv assets/diagrams/$*.tmp.pdf $@
	@rm -f assets/diagrams/$*.svg assets/diagrams/$*.ps

diagrams: $(D2_PDFS)

watch:
	@command -v inotifywait >/dev/null 2>&1 || { \
	  echo "inotifywait not found -- install inotify-tools"; exit 1; }
	@echo ">> watching LaTeX sources and assets (Ctrl-C to stop)"
	@$(MAKE) --no-print-directory pdf || true
	@while inotifywait -qq -r -e close_write,create,delete,move \
	    $(MAIN).tex fragments theme assets; do \
	  $(MAKE) --no-print-directory pdf || true; \
	done

open: $(PDF)
	@xdg-open $(PDF) >/dev/null 2>&1 &

check-sources:
	@python3 scripts/check-sources.py

check-logs: all
	@python3 scripts/check-logs.py $(MAIN).log $(SHOWCASE).log

check-pdf: all
	@python3 scripts/check-pdf.py $(PDF) $(SHOWCASE_PDF)

check-contrast:
	@python3 scripts/check-contrast.py

check-pdfua: all
	@VERAPDF=$(VERAPDF) python3 scripts/check-pdfua.py $(PDF) $(SHOWCASE_PDF)

check: check-sources check-contrast $(D2_PDFS)
	$(call build,$(MAIN),$(MAIN))
	$(call build,$(SHOWCASE),$(SHOWCASE))
	@python3 scripts/check-pdf.py $(PDF) $(SHOWCASE_PDF)

check-homework: check-sources check-contrast $(D2_PDFS)
	$(call build,$(MAIN),$(MAIN))
	@python3 scripts/check-pdf.py $(PDF)

check-all: check
	@VERAPDF=$(VERAPDF) python3 scripts/check-pdfua.py $(PDF) $(SHOWCASE_PDF)

submission-check: check-homework
	@python3 scripts/check-metadata.py fragments/metadata.tex

docker-build:
	docker compose build

docker-shell:
	docker compose run --rm homework bash

clean:
	rm -f $(LATEX_AUX_FILES)
	rm -rf $(MINTED_FILES)
	rm -f $(TAG_FILES)
	rm -rf $(PYC_FILES)
	rm -f $(D2_SCRATCH)

distclean: clean
	rm -f $(PDF) $(SHOWCASE_PDF)

help:
	@python3 -c 'from pathlib import Path; s=Path("Makefile").read_text(); print(s.split("# =====================================================================", 2)[1].strip())'
