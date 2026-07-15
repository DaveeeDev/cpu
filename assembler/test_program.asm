LDA #10
TAB
LDA #05
ADD B
TAX
DECA
TAB
TXA
SUB B
    
TAB
TBA
INCA
OR B
NOTA
TAB
AND B
XOR B
JZ [0x001B]
    
; Error Loop 1, zero flag not set
LDA #0xEE
JMP [0x0016]

LDA #0xFF
TAB
LDA #0x02
ADD B
JC [0x0029]
    
; Error Loop 2, carry flag not set
LDA #0xEE
JMP [0x0024]

LDA #0x42
STA [0x8000]
LDA #0x00
LDA [0x8000]
    
; Success Loop
JMP [0x0033]