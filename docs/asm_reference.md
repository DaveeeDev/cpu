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

---

## Expression Operators

These operators allow you to extract specific bytes of a 16-bit address (such as a label or constant) during the assembly process. They are essential when you need to load an address offset into an 8-bit register.

| Operator | Name | Function | Example | Result (if `label = 0x0212`) |
| :---: | :--- | :--- | :--- | :--- |
| **`<`** | Low-Byte | Extracts the lower 8 bits (`0x00` - `0xFF`) | `LDA #<label` | `LDA #0x12` |
| **`>`** | High-Byte | Extracts the upper 8 bits (`0x00` - `0xFF`) | `LDA #>label` | `LDA #0x02` |

---

## Addressing Modes

The CPU distinguishes between loading a literal value and accessing a memory address using two distinct addressing modes:

*   **Immediate Addressing (`#`):** Instructs the CPU to use the literal value following the instruction.
    *   *Example:* `LDA #0x05` (Loads the numeric value `0x05` directly into the Accumulator).
*   **Direct/Absolute Addressing (No prefix):** Instructs the CPU to treat the argument as a 16-bit RAM address and load the data stored *at* that address.
    *   *Example:* `LDA 0x0212` (Loads the byte stored in memory location `0x0212` into the Accumulator).
*   **Indexed Addressing (page):** Instructs the CPU to use the (page * 256) + X as the 16-bit RAM address and load the data stored *at* that address.
    *   *Example:* `LDAX 0x02`, `X` = `0x14` (Loads the byte stored in memory location `0x0214` into the Accumulator).

---

## Assembly Example

Here is a brief, complete program demonstrating how instructions, directives, constants, and labels work together:
```assembly
; ==============================================================================
; ARRAY PROCESSING & STACK EXAMPLE
; Iterates through a null-terminated data block, adds a fixed offset to each 
; value, and pushes the results to the stack.
; ==============================================================================

; --- Constants ---
STACK_P  EQU 0x0100      ; Define stack page (for reference)
IO_DATA  EQU 0x8000      ; Define memory-mapped I/O address (unused here)
START    EQU 0x0200      ; Define the program's base memory address

    ORG START            ; Set the assembler PC to 0x0200

start:
    ; Initialize our array pointer in the X register.
    ; We extract only the low-byte of the data_block address.
    LDA #<data_block     ; Load low-byte of data_block address into A
    TAX                  ; Transfer A to X (X is now our array index)

loop:
    ; Read the current array element into A.
    ; LDAX reads from [Page:X]. We dynamically extract the High-Byte
    ; of our START address to use as the memory page (0x02).
    LDAX >START          ; A = RAM[ (START >> 8) : X ]
    
    ; Check for null-terminator (0x00)
    JZ finish            ; If A == 0, Zero Flag is set, jump to finish

    ; Perform the math: ArrayValue + Offset
    TAB                  ; Move the array value from A into B
    LDA offset           ; Load the constant offset (0x10) into A
    ADD B                ; A = A + B (Result is now in A)
    
    ; Save the result
    PUSH                 ; Push the calculated value onto the stack

    ; Increment our pointer (X = X + 1)
    TXA                  ; Move X back to A so we can use the ALU
    INCA                 ; Increment A by 1
    TAX                  ; Move the incremented value back to X
    
    JMP loop             ; Jump back to the start of the loop

finish:
    HLT                  ; Halt the CPU

; --- Data Section ---
offset:     DB 0x10      ; The offset value to add to each element
data_block: DB 0x05      ; Array element 1
            DB 0x0A      ; Array element 2
            DB 0x00      ; Null-terminator (ends the loop)
```

## Errors & Troubleshooting

The assembler performs validation checks and will halt assembly if it encounters any of the following:
*   **Syntax & Formatting Violations:** Enforces valid mnemonics and correct argument counts (e.g., catching typos like `LAD #0x05` or missing arguments).
*   **Out of Range Immediate Value (8-bit):** High-byte arguments for `LDA #imm` and values for `DB` must sit between `0` and `255` (`0x00` - `0xFF`).
*   **Out of Range Address (16-bit):** Target addresses for jump/call instructions or `EQU` values used as addresses must sit between `0` and `65535` (`0x0000` - `0xFFFF`).
*   **Duplicate Symbols:** Declaring the same label or `EQU` constant twice will result in a duplication error.
*   **Undefined Symbols:** Referencing a label or constant that hasn't been defined anywhere in the source file will cause an assembly failure.