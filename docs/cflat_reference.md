# CFlat Language Reference

CFlat is a lightweight, strictly typed, high-level programming language designed specifically to compile down to my custom 8-bit Von Neumann ISA. It provides structural programming features while abstracting away manual stack management and CPU register transfers.

## Overview and Design Philosophy

The primary goal of CFlat is to provide a C-like syntax that maps efficiently to an 8-bit accumulator-based CPU. Because the target hardware has severe memory constraints and a limited instruction set, CFlat enforces strict limits on variable scoping, mathematical operations, and memory allocation.

---

## Data Types and Memory Management

CFlat does not use dynamic memory allocation or a runtime heap. All memory mapping and layout limits are handled entirely at compile time.

### Available Types

| Type | Description | Size | Initialization |
| :--- | :--- | :--- | :--- |
| **`uint8`** | Unsigned 8-bit integer (`0` to `255`). | 1 Byte | `uint8 step;` |
| **`bool`** | Boolean logic value (`true` or `false`). | 1 Byte | `bool keep_going;` |
| **`const`** | Read-only constant value. | 1 Byte | `const uint8 MAX = 150;` |

---

## System Memory Map

The compiler enforces a strict Von Neumann memory segmentation layout based on your 16-bit address space.

| Address Range | Segment Name | Description |
| :--- | :--- | :--- |
| **`0x0000 - 0x00EF`** | **Zero Page RAM** | Dynamically allocated for standard compiler variables (`uint8`, `bool`). Max capacity: **240 variables**. |
| **`0x00F0 - 0x00FF`** | **System Reserved Zero Page** | Hardcoded internal scratchpad registers used by the standard library (e.g., `__sys_mul` at `0x00FC/0x00FD`) and hardware frame pointers. |
| **`0x0100 - 0x01FF`** | **Hardware Stack** | Dedicated stack memory. The Stack Pointer automatically decrements down from `0x01FF`. |
| **`0x0200 - 0x7FFF`** | **Program Space** | Execution area for generated machine code instructions and `DB` constant data placements. |
| **`0x8000 - 0xFFFF`** | **General RAM / IO Mapping**| High memory zone utilized for external hardware communication registers or extended data arrays. |

### Variable Allocation & Constants Placement
*   **Standard Variables:** All non-constant variables are assigned addresses sequentially starting at `0x0000`. Exceeding address `0x00EF` triggers a compile-time overflow error to protect the system-reserved scratchpad zone.
*   **Constants:** Variables defined with `const` are not placed in RAM. They are embedded directly inside the **Program Space (`0x0200+`)** using `DB` assembly directives, making them permanent read-only execution memory.

---

## Syntax and Operators

CFlat is whitespace-agnostic. Every statement must be explicitly terminated with a semicolon (`;`).

### Comments
Single-line comments are supported using double slashes. Everything following the slashes on the same line is ignored by the lexer.
```
// This is a CFlat comment
uint8 speed = 10; // Sets the initial speed
```

### Mathematical Operators
The compiler strictly enforces standard mathematical order of operations (precedence).

| Operator | Function | Hardware Implementation |
| :---: | :--- | :--- |
| **`+`** | Addition | Compiles to inline `ADD B` |
| **`-`** | Subtraction | Compiles to inline `SUB B` |
| **`*`** | Multiplication | Pushes to stack, invokes standard library `CALL __sys_mul` |
| **`/`** | Division | *Not yet implemented by the compiler* |

### Relational Operators
Used strictly within conditional statements. They evaluate to a boolean representation in the accumulator (`0x01` for true, `0x00` for false).

| Operator | Description | Supported Types |
| :---: | :--- | :--- |
| **`==`** | Equal to | `uint8`, `bool` |
| **`!=`** | Not equal to | `uint8`, `bool` |

*(Note: Greater-than and less-than operators are not currently supported by the AST generator).*

---

## Control Flow

CFlat provides three primary control structures, all of which use curly braces `{}` to define code blocks. 

### Conditional Branching (`if` / `else`)
Evaluates an expression using the CPU's Zero flag (`JZ`).
```
if (condition_met == false) {
    total = total + 10;
} else {
    total = total - 1;
}
```

### The `while` Loop
Continues executing the block as long as the condition evaluates to `true`.
```
while (keep_going != false) {
    total = total * 2;
    if (total == 58) {
        break; // Immediately exits the closest loop
    }
}
```

### The `for` Loop
A syntactic sugar implementation. The compiler automatically "desugars" this into a standard `while` loop behind the scenes. It requires an initialization, a relational condition, and a step operation.
```
uint8 step;
for (step = 1; step != limit; step = step + 1) {
    total = total + (step * factor);
}
```

---

## Architectural Limitations & Behaviors

### 8-Bit Overflow Limit
Because `uint8` limits values to `255`, operations that exceed this boundary (e.g., `150 + 150`) will silently overflow within the ALU, dropping the carry bit, as the compiler does not implement `ADC` (Add with Carry) logic for multi-byte arithmetic yet.

### No Procedures or Functions
All code in CFlat currently exists in the global scope. Standard C-like function definitions and modular `return` statements are unsupported. Code executes linearly from top to bottom until the underlying assembly injects a `HLT` (Halt) instruction at the end of the script.