# Instruction Set Architecture (ISA) Reference

This document outlines the custom 8-bit instruction set for our Von Neumann CPU. The architecture uses a variable instruction length (1, 2, or 3 bytes) to support a full 16-bit address space while keeping the core data bus 8-bit.

## Register Overview
*   **A**: Accumulator (8-bit) - Primary register for ALU operations.
*   **B**: Auxiliary Register (8-bit) - Secondary ALU input.
*   **X**: Index / General Purpose Register (8-bit) - Fast temporary storage.
*   **PC**: Program Counter (16-bit).
*   **MAR**: Memory Address Register (16-bit) - Holds target addresses for memory access.

## Instruction Table

| Assembly | Bytes | Cycles | Opcode | Byte 2 | Byte 3 | Description |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`NOP`** | 1 | 2 | `0x00` | - | - | No Operation |
| **`LDA #imm`** | 2 | 2 | `0x01` | `Value` | - | Load 8-bit immediate value into A |
| **`LDA [addr]`** | 3 | 4 | `0x02` | `ADRL` | `ADRH` | Load 8-bit value from 16-bit memory address into A |
| **`STA [addr]`** | 3 | 4 | `0x03` | `ADRL` | `ADRH` | Store 8-bit value from A to 16-bit memory address |
| **`ADD B`** | 1 | 2 | `0x04` | - | - | Add B to A (A = A + B) |
| **`ADC B`** | 1 | 2 | `0x05` | - | - | Add B to A with Carry (A = A + B + Carry) |
| **`SUB B`** | 1 | 2 | `0x06` | - | - | Subtract B from A (A = A - B) |
| **`AND B`** | 1 | 2 | `0x07` | - | - | Bitwise AND between A and B (A = A & B) |
| **`OR B`** | 1 | 2 | `0x08` | - | - | Bitwise OR between A and B (A = A \| B) |
| **`XOR B`** | 1 | 2 | `0x09` | - | - | Bitwise XOR between A and B (A = A ^ B) |
| **`NOTA`** | 1 | 2 | `0x0A` | - | - | Bitwise NOT A |
| **`JMP [addr]`** | 3 | 4 | `0x0B` | `ADRL` | `ADRH` | Unconditional jump to 16-bit address |
| **`JZ [addr]`** | 3 | 4 | `0x0C` | `ADRL` | `ADRH` | Jump to 16-bit address if Zero flag is set (Z = 1) |
| **`JC [addr]`** | 3 | 4 | `0x0D` | `ADRL` | `ADRH` | Jump to 16-bit address if Carry flag is set (C = 1) |
| **`TAX`** | 1 | 2 | `0x0E` | - | - | Transfer A to X (X = A) |
| **`TXA`** | 1 | 2 | `0x0F` | - | - | Transfer X to A (A = X) |
| **`TAB`** | 1 | 2 | `0x10` | - | - | Transfer A to B (B = A) |
| **`TBA`** | 1 | 2 | `0x11` | - | - | Transfer B to A (A = B) |
| **`INCA`** | 1 | 2 | `0x12` | - | - | Increment A by 1 (A = A + 1) |
| **`DECA`** | 1 | 2 | `0x13` | - | - | Decrement A by 1 (A = A - 1) |
| **`HLT`** | 1 | 2 | `0xFF` | - | - | Halt CPU |

*Note: `ADRL` refers to the lower 8 bits of the 16-bit address, and `ADRH` refers to the upper 8 bits (Little Endian format).*