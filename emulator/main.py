from cpu import CPU

cpu = CPU()

cpu.load_from_file(0x0000, "assembler/test_program.bin")

for i in range(80):
    print(f"Cycle {i:02d} | ", end="")
    cpu.tick()
    cpu.print_state()

print("\n--- READ VALUE FROM RAM ---")
print(f"RAM[0x8000]: {cpu.ram[0x8000]:02X} (Expected: 42)")