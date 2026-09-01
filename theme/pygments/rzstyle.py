"""Pygments styles matching theme/ricardo-palette.sty, in both schemes.

minted is the only code engine this theme has, and Pygments will not resolve
a style from a path -- only from a registered name -- so this module is a
plugin and has to be installed for the decks to build:

    pip install --user -e theme/pygments

The Docker image does it at build time. Without it, `\\usemintedstyle{rzstyle}`
fails with `Pygments style "rzstyle" was not found'.

Why not one of the styles Pygments ships. Two reasons, and the second is the
one that matters.

The colours would not be this deck's. Every other mark on a slide comes from
~/.config/nvim/lua/ricardo/colors.lua, and code set in one-dark reads as a
window from somebody else's editor.

And none of them are accessible on these backgrounds. Measured against the
code plate the theme actually uses: of the forty-odd styles Pygments ships,
the best against #212121 is one-dark, with one token colour at 4.29:1, and
the best against #F1F1F1 is xcode at 4.49:1. Both miss WCAG 1.4.3 AA, by a
little, in a way no build reports. The values below are the palette's own
rzsyn* roles, which scripts/check-contrast.py holds to 4.5:1 in both schemes
-- so the code on a slide is checked to the same bar as everything else.

The token -> role mapping follows the nvim highlight groups, so a code block
on a slide reads like the same code in the editor.
"""

from pygments.style import Style
from pygments.token import (
    Comment,
    Error,
    Generic,
    Keyword,
    Literal,
    Name,
    Number,
    Operator,
    Other,
    Punctuation,
    String,
    Text,
    Whitespace,
)


def _styles(surface, fg, fg_dim, fg_bright, selection,
            keyword, type_, builtin, const, string, comment, func, error):
    """The one mapping, resolved twice -- once per scheme.

    Written as a function rather than two hand-maintained dictionaries because
    the mapping is the design and the colours are the scheme. Editing one of
    them and not the other is how a light deck ends up with dark-deck greens.
    """
    return {
        Text:                   fg,
        Whitespace:             fg_dim,
        Error:                  f"bold {error}",
        Other:                  fg,

        Comment:                f"italic {comment}",
        Comment.Preproc:        builtin,
        Comment.PreprocFile:    string,
        Comment.Special:        f"italic bold {type_}",

        Keyword:                f"bold {keyword}",
        Keyword.Constant:       const,
        Keyword.Declaration:    f"bold {keyword}",
        Keyword.Namespace:      builtin,
        Keyword.Pseudo:         const,
        Keyword.Reserved:       f"bold {keyword}",
        Keyword.Type:           type_,

        Operator:               fg_bright,
        Operator.Word:          f"bold {keyword}",
        Punctuation:            fg_dim,

        Name:                   fg,
        Name.Attribute:         type_,
        Name.Builtin:           builtin,
        Name.Builtin.Pseudo:    builtin,
        Name.Class:             type_,
        Name.Constant:          const,
        Name.Decorator:         type_,
        Name.Entity:            builtin,
        Name.Exception:         error,
        Name.Function:          func,
        Name.Function.Magic:    builtin,
        Name.Label:             type_,
        Name.Namespace:         builtin,
        Name.Property:          builtin,
        Name.Tag:               keyword,
        Name.Variable:          fg,
        Name.Variable.Class:    builtin,
        Name.Variable.Global:   builtin,
        Name.Variable.Instance: builtin,
        Name.Variable.Magic:    builtin,

        Literal:                fg,
        Literal.Date:           string,

        String:                 string,
        String.Affix:           keyword,
        String.Char:            string,
        String.Doc:             f"italic {comment}",
        String.Escape:          type_,
        String.Interpol:        type_,
        String.Other:           string,
        String.Regex:           builtin,
        String.Symbol:          const,

        Number:                 const,

        Generic.Deleted:        error,
        Generic.Emph:           "italic",
        Generic.Error:          error,
        Generic.Heading:        f"bold {fg_bright}",
        Generic.Inserted:       string,
        Generic.Output:         fg_dim,
        Generic.Prompt:         f"bold {string}",
        Generic.Strong:         "bold",
        Generic.Subheading:     f"bold {func}",
        Generic.Traceback:      error,
    }


# --- dark ------------------------------------------------------------
# Resolved from theme/ricardo-palette.sty. The AA-adjusted variants are the
# ones the palette itself paints with -- rzc@blueAA rather than rzc@blue --
# because four of the raw terminal colours sit just under 4.5:1 on this plate.
# A terminal palette is tuned for a screen an arm's length away.
class RicardoStyle(Style):
    name = "rzstyle"

    background_color = "#212121"        # rzsurface
    highlight_color = "#2c2c2c"         # rzc@selection
    line_number_color = "#898989"       # rzfgdim   4.60:1
    line_number_background_color = "#212121"
    line_number_special_color = "#f1f1f1"
    line_number_special_background_color = "#2c2c2c"

    styles = _styles(
        surface="#212121",
        fg="#d6d6d6",                   # rzsynident   11.08:1
        fg_dim="#898989",               # rzfgdim       4.60:1
        fg_bright="#f1f1f1",            # rzfgbright   14.26:1
        selection="#2c2c2c",
        keyword="#0891c6",              # rzsynkeyword  4.51:1
        type_="#f3e430",                # rzsyntype    12.23:1
        builtin="#20a5ba",              # rzsynbuiltin  5.48:1
        const="#8879e5",                # rzsynconst    4.53:1
        string="#5fd7af",               # rzsynstring   9.07:1
        comment="#898989",              # rzsyncomment  4.60:1
        func="#20bbfc",                 # rzsynfunc     7.34:1
        error="#fc4aa1",                # rzsynerror    5.09:1
    )


# --- light -----------------------------------------------------------
# Not an inversion. A terminal palette comes in normal/bright pairs because
# the two ends are built for opposite backgrounds, so the light scheme is the
# same colours read from the other end -- and these are the rzsyn* roles the
# light palette sets, resolved the same way.
class RicardoLightStyle(Style):
    name = "rzstyle-light"

    background_color = "#f1f1f1"        # rzsurface
    highlight_color = "#d6d6d6"
    line_number_color = "#6e6e6e"       # rzfgdim   4.51:1
    line_number_background_color = "#f1f1f1"
    line_number_special_color = "#000000"
    line_number_special_background_color = "#d6d6d6"

    styles = _styles(
        surface="#f1f1f1",
        fg="#212121",                   # rzsynident   14.26:1
        fg_dim="#6e6e6e",               # rzfgdim       4.51:1
        fg_bright="#000000",            # rzfgbright   18.59:1
        selection="#d6d6d6",
        keyword="#005f87",              # rzsynkeyword  6.23:1
        type_="#766d0e",                # rzsyntype     4.69:1
        builtin="#167482",              # rzsynbuiltin  4.82:1
        const="#523c79",                # rzsynconst    8.15:1
        string="#0b6e4f",               # rzsynstring   5.54:1
        comment="#6e6e6e",              # rzsyncomment  4.51:1
        func="#0076a3",                 # rzsynfunc     4.51:1
        error="#b50769",                # rzsynerror    5.81:1
    )
