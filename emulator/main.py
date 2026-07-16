import time
from cpu import CPU

cycles = 0
max_cycles = 1000

cpu = CPU()

binary_file_path = "assembler/programs/test.bin"
cpu.load_from_file(0x0200, binary_file_path)


def print_benchmark_results(runtime, cycles):
    print(f"\n--- Benchmark Results ---")
    print(f"Time Elapsed: {runtime:.3f} ms")
    print(f"Total Cycles: {cycles:,}")
    print(f"CPU Speed:    {(cycles / runtime * 1000):,.0f} cycles/second (Hz)")

start_time = time.perf_counter()

while cpu.running and cycles < max_cycles:
    print(f"Cycle {cycles:02d} | ", end="")
    cpu.print_state()
    cpu.tick()
    cycles += 1

if cycles == max_cycles:
    print("Max cycles reached. Halting execution. Code Execution may be incomplete.")

end_time = time.perf_counter()
runtime_ms = (end_time - start_time) * 1000
print_benchmark_results(runtime_ms, cycles)


cpu.dump_ram(0x01F0, 0x10, "STACK")  # dump stack
cpu.dump_ram(0x8000, 0x10)           # dump values