from cpu import CPU

cpu = CPU()

cpu.load_from_file(0x0000, "assembler/programs/multiplication.bin")

for i in range(120):
    print(f"Cycle {i:02d} | ", end="")
    cpu.tick()
    cpu.print_state()

cpu.dump_ram(0x8000, 16)