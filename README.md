# SimpleUI Compiler

SimpleUI is a mini language for describing 2D UI layouts using concise,
CSS‑like statements. This repository contains a complete compiler pipeline
that transforms `.sui` source files into runnable Python/Turtle scripts or an
embedded interactive previewer.

## Features
- **Lexing** via a custom tokenizer that understands positions, sizes, colors,
  rounded corners, and comments.
- **Parsing** powered by Lark (`grammar.lark`) that builds a typed AST defined
  in `ast_nodes.py`.
- **Code generation** that emits Turtle graphics code (`code_generator.py`) so
  compiled layouts can run anywhere Python’s standard library is available.
- **Interactive mode** (`interactive_app.py`) offering a Tk/Turtle IDE for
  live editing and rendering.
- **Smoke tests** inside `compiler.py` for quick validation of the toolchain.

## Prerequisites
- Python 3.9+ (tested on CPython)
- Pip packages:
  - `lark` (required by the parser)
  - `tk`/`turtle` ship with the CPython standard library on most platforms

Install dependencies manually:

```
pip install lark
```

## Project Layout
- `compiler.py` – CLI entry point and orchestration logic.
- `lexer.py` – Hand‑rolled tokenizer used for verbose debugging mode.
- `parser.py` / `grammar.lark` – Lark grammar plus AST transformer.
- `ast_nodes.py` – Dataclasses describing shapes, colors, and layout info.
- `code_generator.py` – Emits executable Turtle scripts.
- `interactive_app.py` – Optional GUI for live editing/rendering.
- `test_output.py` – Example Turtle output file produced by the generator.

## Writing SimpleUI Code

A program is a list of shape statements ending with `;`. Each statement combines
position (`left`, `top`), size (`w`, `h`), colors (`fill`, `outside`), and the
final shape keyword (`rectangle`, `circle`, or `line`):

```
100px left, 50px top, w:200px, h:100px, fill:#FF0000, outside:#000000, rounded, rectangle;
50px left, 125px top, w:80px, h:80px, fill:#00FF00, circle;
```

Widths/heights can be floats, hex colors use `#RRGGBB`, and lines interpret
`w`/`h` as the delta for the end point.

## Command-Line Usage

Compile a `.sui` file to Python:

```
python compiler.py path/to/input.sui
```

Options:
- `-o output.py` – Custom output file name.
- `--run` – Execute the generated Turtle script after compilation.
- `-v` – Verbose mode (shows tokens, AST contents, and statistics).
- `-g custom_grammar.lark` – Supply an alternate grammar file.

When run **without arguments**, `compiler.py` executes the built-in smoke tests
defined near the bottom of the file so you can quickly confirm the pipeline
works.

## Using the Interactive App

To experiment live:

```
python interactive_app.py
```

The window includes a SimpleUI text editor, buttons to compile/render,
clear the canvas, and load an example that draws stylized “WELCOME TO
SimpleUI” lettering.

## Development Tips
- Enable verbose mode (`-v`) when debugging lexer/parsing issues.
- AST dataclasses in `ast_nodes.py` enforce color normalization and defaults,
  making it easy to inspect shapes in a debugger.
- Generated Turtle scripts call `screen.exitonclick()` so you can close the
  preview window manually.

## Troubleshooting
- `ModuleNotFoundError: No module named 'lark'` – install the dependency with
  `pip install lark`.
- Turtle or Tk errors on headless servers: run inside an environment with a
  display server, or use `xvfb-run` on Linux if you only need to render.

Happy hacking!

