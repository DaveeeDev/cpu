from cpu import CPU

cpu = CPU()

test_program = [
    # Initialise RAM Address 0x2000 with value 5
    0x01, 0x05,        # LDA #05
    0x03, 0x00, 0x20,  # STA 0x2000
    
    # Initialise B with value 3
    0x01, 0x03,        # LDA #03
    0x0F,              # TAB
    
    # Load A with value from previous RAM Address 0x2000
    0x02, 0x00, 0x20,  # LDA 0x2000
    
    # Subtract B from A (A = 5 - 3 = 2)
    0x06,              # SUB B
    
    # Increment and test register transfers (A = 2, B = 3, X = 3)
    0x11,              # INCA
    0x0D,              # TAX
    0x12,              # DECA
    0x0E,              # TXA
    0x0F,              # TAB
    
    # Add B to A (A = 2 + 3 = 5)
    0x04,              # ADD B
    
    # XOR A with B (A = 5 ^ 3 = 6)
    0x09,              # XOR B
    
    # JC should not jump, if it does, it will jump to the crash address 0x0050
    0x0C, 0x50, 0x00,  # JC 0x0050
    
    # JMP to success loop at address 0x0024
    0x0A, 0x19, 0x00,  # JMP 0x0019
    
    # success loop
    0x0A, 0x19, 0x00,  # JMP 0x0019
    
    # crash address (should never be reached)
    0x00,              # NOP
]

cpu.load_program(0x0000, test_program)

for i in range(38 + 8):  # 38 microsteps for main program + 8 microsteps for 2 success loop iterations
    print(f"Cycle {i:02d} | ", end="")
    cpu.tick()
    cpu.print_state()

print("\n--- READ VALUE FROM RAM ---")
print(f"RAM[0x2000]: {cpu.ram[0x2000]:02X} (Expected: 05)")