from cpu import CPU

cycles = 0
max_cycles = 1000
cpu = CPU()

cpu.load_from_file(0x0000, "assembler/programs/multiplication.bin")

while cpu.running and cycles < max_cycles:
    print(f"Cycle {cycles:02d} | ", end="")
    cpu.tick()
    cpu.print_state()
    cycles += 1

cpu.dump_ram(0x8000, 16)