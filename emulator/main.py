from cpu import CPU

cycles = 0
max_cycles = 100

cpu = CPU()

binary_file_path = "assembler/programs/stack_test.bin"

cpu.load_from_file(0x0200, binary_file_path)

while cpu.running and cycles < max_cycles:
    print(f"Cycle {cycles:02d} | ", end="")
    cpu.tick()
    cpu.print_state()
    cycles += 1

if cycles == max_cycles:
    print("Max cycles reached. Halting execution. Code Execution may be incomplete.")

cpu.dump_ram(0x01F0, 0x10, "STACK")  # dump stack
cpu.dump_ram(0x8000, 0x10)           # dump RAM