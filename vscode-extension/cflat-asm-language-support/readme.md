# CFlat & Custom Assembly Language Support

[![VS Code Extension](https://shields.io)](https://github.com/DaveeeDev/cpu)
[![License: MIT](https://shields.io)](https://opensource.org)

This extension provides comprehensive syntax highlighting and editor support for **CFlat** (`.cflat`) and its compiled **Custom Assembly** (`.asm`) files. Designed specifically to work seamlessly with the [DaveeeDev CPU Ecosystem](https://github.com/DaveeeDev/cpu).

---

## Features

*   **CFlat Support (`.cflat`):** Full syntax highlighting for variables (`uint8`, `bool`), control flow (`if`, `else`, `for`, `while`, `break`), mathematical/relational operators, and block comments (`//`).
*   **Custom Assembly Support (`.asm`):** Dedicated tokenization for custom opcodes (`LDA`, `STA`, `JZ`, `HLT`, etc.), architectural registers, compiler directives (`ORG`, `EQU`, `DB`), and assembly-style comments (`;`).
*   **Smart Code Editing:** Automated brackets pairing, closing, and toggle comment shortcuts mapped correctly to both file formats.

---

## Development & Installation

### For Users (Manual Installation)
1. Download the latest `.vsix` file from the repository.
2. In VS Code, open the Extensions view (`Ctrl+Shift+X`).
3. Click the `...` (Views and More Actions) in the top-right corner.
4. Select **Install from VSIX...** and choose the downloaded file.

### For Contributors (Working on the Extension)
If you want to modify the language grammars, clone the repository and run it in development mode:

1. Open the project root directory in VS Code.
2. Press **`F5`** to launch a new *Extension Development Host* window.
3. Open any `.cflat` or `.asm` file in the new window to test your changes live.

---

## Project Structure

*   `syntaxes/cflat.tmLanguage.json` — TextMate grammar rules for high-level CFlat code.
*   `syntaxes/asm.tmLanguage.json` — TextMate grammar rules for the compiled assembly output.
*   `language-configuration.json` / `asm-configuration.json` — Editor behaviors (brackets, auto-closing, comment tokens).

---

## 🔗 Links & Resources

*   **Source Code & Compiler:** [DaveeeDev/cpu GitHub Repository](https://github.com/DaveeeDev/cpu)

**Developed for the Custom CPU Ecosystem. Enjoy!**
