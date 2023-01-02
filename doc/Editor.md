# Editors

We will switch to using a Theia based editor with vscode-extensions.

## Basic vscode extensions

The primary addition to this editor will be a [customised
version](https://github.com/stephengaito/theia-open) of
[theia-open](https://github.com/perrinjerome/theia-open/) which can open
to a specific line in a file (using `editor.cursor.line`).

We will also use a custom [VSCode Syntax
Hightlight](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide)
which are based upon [TextMate Language
Grammars](https://macromates.com/manual/en/language_grammars). Our grammar
will be tailored to allow [code
embeddings](https://sublimetext.userecho.com/communities/1/topics/4953-nested-syntax-highlighting)
inside ConTeXt. See for example
[vscode-context-syntax](https://github.com/JulianGmp/vscode-context-syntax).

We will also specify the ConTeXt [language
configuration](https://code.visualstudio.com/api/language-extensions/language-configuration-guide).

We might provide ConTeXt
[snippets](https://code.visualstudio.com/api/language-extensions/snippet-guide).


## Language Server

Eventually it would be nice to provide a Language Server similar to
[digestif](https://github.com/astoff/digestif), to provide semantic
symbols (and outlines) as well as comprehensive cross-references and
citations.

Essentially this language server would use [embedded
languages](https://code.visualstudio.com/api/language-extensions/embedded-languages),
and essentially require the current literate programming in ConTeXt
"parser" to determine the boundaries of all of the embedded sections as
well as their language types.

To do this we should restructure the current "macros" to a superset of the
digestif tags file format.
