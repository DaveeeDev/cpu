# Assembly Language Reference

This document serves as the official reference manual for writing programs compatible with my custom 8-bit assembler. It covers syntax rules, data directives, and the mechanics of label resolution.

---

## Directives

Directives are instructions for the assembler itself. They do not map directly to CPU opcodes, but instead control where code is loaded, define variables, or insert raw data.

### `ORG` (Origin)
Sets the **Program Counter (PC)** to a specific 16-bit memory location. All subsequent instruction and label addresses are calculated relative to this address.
*   **Format:** `ORG <address>`
*   **Example:**
    ```assembly
    ORG 0x8000  ; Start assembling code at memory address 0x8000
    ```

### `EQU` (Equate / Constants)
Defines a global compile-time constant. It assigns a label to a fixed value. `EQU` does **not** generate machine code or advance the Program Counter.
*   **Format:** `<constant_name> EQU <value>`
*   **Example:**
    ```assembly
    RAM_START EQU 0x0200
    MAX_LIMIT EQU 255
    ```

### `DB` (Define Byte)
Inserts a raw 8-bit byte directly into the compiled machine code. When combined with a preceding label, it serves as a variable declaration. This directive advances the Program Counter by 1 byte.
*   **Format:** `<variable_name>: DB <value>` or `DB <value>`
*   **Example:**
    ```assembly
    speed: DB 0x03   ; Declares 'speed' at the current PC and writes 0x03
    DB 0xFF          ; Inserts 0xFF at the current PC (anonymous data)
    ```

---

## Syntax & Formatting Rules

### Literals (Numeric Representations)
Numbers can be written in two formats:
*   **Hexadecimal:** Prefixed with `0x` (e.g., `0x0A`, `0x8002`). Case-insensitive.
*   **Decimal:** Written normally (e.g., `10`, `32768`).

### Comments
Comments are initiated with a semicolon (`;`). Anything following a semicolon on a line is ignored by the assembler.
```assembly
LDA #10  ; This is an inline comment
; This is a standalone comment line
```

### Case Sensitivity
*   **Opcodes and Directives:** Case-insensitive (e.g., `lda`, `Lda`, and `LDA` are identical).
*   **Labels and Constants:** Case-sensitive. `speed` and `Speed` are treated as two distinct symbols.

---

## Labels vs. Constants

The assembler handles variables and constants using two distinct mechanisms during its two-pass compilation:

| Feature | Labels (with `:` or via `DB`) | Constants (`EQU`) |
| :--- | :--- | :--- |
| Declaration | `my_label:` or `my_var: DB 0x05` | `my_const EQU 0x8000` |
| PC Advance | Advances PC by the instruction/data size | Does not advance PC |
| Assigned Valeu | Set to the current memory address (PC) | Set to the specified literal value |
| Pass Resolved	| Address calculated during Pass 1 | Value assigned during Pass 1 |

## Assembly Example

Here is a brief, complete program demonstrating how instructions, directives, constants, and labels work together:
```assembly
; Define system constants
IO_PORT EQU 0x8000

ORG 0x0000

start:
    LDA #0x05       ; Load 5 into A
    TAB             ; Copy A to B
    LDA speed       ; Load value from 'speed' address (0x000B) into A
    ADD B           ; A = A + B
    STA IO_PORT     ; Write sum to IO_PORT (0x8000)
    HLT             ; Stop execution

; Variable Data Block
speed: DB 0x03      ; Defined at PC address 0x000B
```

## Errors & Troubleshooting

The assembler performs validation checks and will halt assembly if it encounters any of the following:
*   **Out of Range Immediate Value (8-bit):** High-byte arguments for `LDA #imm` and values for `DB` must sit between `0` and `255` (`0x00` - `0xFF`).
*   **Out of Range Address (16-bit):** Target addresses for jump/call instructions or `EQU` values used as addresses must sit between `0` and `65535` (`0x0000` - `0xFFFF`).
*   **Duplicate Symbols:** Declaring the same label or `EQU` constant twice will result in a duplication error.
*   **Undefined Symbols:** Referencing a label or constant that hasn't been defined anywhere in the source file will cause an assembly failure.