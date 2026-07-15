class CPU:
    def __init__(self):
        self.ram = [0x00] * 65536  # 64 KB RAM
        self.data_bus = 0x00       # 8-Bit
        self.addr_bus = 0x0000     # 16-Bit
        
        self.regs = {
            "A": 0x00,      # Accumulator
            "B": 0x00,      # ALU Secondary Input Register
            "X": 0x00,      # Index and General Purpose Register
            "IR": 0x00,     # Instruction Register
            "PC": 0x0000,   # Program Counter
            "MAR": 0x0000,  # Memory Address Register
            "T": 0,         # Microstep-Counter (0 to 4)
            "C": 0,         # Carry-Flag
            "Z": 0          # Zero-Flag
        }

    # Helper: loads a program into RAM at a given start address
    def load_program(self, start_addr, byte_array):
        for i, byte in enumerate(byte_array):
            self.ram[start_addr + i] = byte

    # Helper: loads a program from a binary file into RAM at a given start address
    def load_from_file(self, start_addr, filename):
        with open(filename, "rb") as file:
            byte_data = file.read()
            for i, byte in enumerate(byte_data):
                self.ram[start_addr + i] = byte


    def alu(self, val_a, val_b, op):
        result = 0
        c_out = self.regs["C"]
        
        if op == "ADD":
            result = val_a + val_b
            c_out = 1 if result > 255 else 0
        if op == "ADC":
            result = val_a + val_b + self.regs["C"]
            c_out = 1 if result > 255 else 0
        if op == "SUB":
            result = val_a - val_b
            c_out = 1 if result < 0 else 0
        if op == "AND":
            result = val_a & val_b
        if op == "OR":
            result = val_a | val_b
        if op == "XOR":
            result = val_a ^ val_b
        if op == "NOT":
            result = ~val_a
        
        result = result & 0xFF  # mask to 8 bits
        z_out = 1 if result == 0 else 0
        
        return result, c_out, z_out


    def tick(self):
        # Every virtual control signal is initially set to False or None
        PC_OE = False     # PC Output Enable
        MAR_OE = False    # MAR Output Enable
        A_OE = False      # A Output Enable
        B_OE = False      # B Output Enable
        X_OE = False      # X Output Enable
        RAM_OE = False    # RAM Output Enable
        RAM_WE = False    # RAM Write Enable
        IR_LD = False     # Load Instruction Register
        A_LD = False      # Load Register A
        B_LD = False      # Load Register B
        X_LD = False      # Load Register X
        PC_LD = False     # Load Program Counter
        MAR_L_LD = False  # Load Low Byte of MAR
        MAR_H_LD = False  # Load High Byte of MAR
        PC_INC = False    # Increment Program Counter
        A_INC = False     # Increment Register A
        A_DEC = False     # Decrement Register A
        RESET_T = False   # Reset Microstep Counter
        ALU_OP = None     # ALU Operation
        
        T = self.regs["T"]
        opcode = self.regs["IR"]
        
        # FETCH
        if T == 0:
            PC_OE = True   # PC sets the address bus to the next instruction
            RAM_OE = True  # RAM writes opcode to the data bus
            IR_LD = True   # IR reads the opcode from the data bus
            PC_INC = True  # PC increments to point to the next instruction
            
        # EXECUTE
        elif T > 0:
            # NOP (1-Byte 1-Cycle)
            if opcode == 0x00:
                RESET_T = True  # Reset Microstep Counter for next instruction
            # LDA #imm (2-Byte 2-Cycle)
            elif opcode == 0x01:
                if T == 1:
                    PC_OE = True    # PC sets the address bus to the data byte
                    RAM_OE = True   # RAM writes the data byte to the data bus
                    A_LD = True     # Register A reads the data byte
                    PC_INC = True   # PC increments to point to the next instruction
                    RESET_T = True  # Reset Microstep Counter for next instruction
            # LDA [addr] (3-Byte 4-Cycle)
            elif opcode == 0x02:
                if T == 1:
                    PC_OE = True     # PC sets the address bus to the low byte of the address
                    RAM_OE = True    # RAM writes the low byte of the address to the data bus
                    MAR_L_LD = True  # MAR reads the low byte off the address bus
                    PC_INC = True    # PC increments to point to the next instruction
                elif T == 2:
                    PC_OE = True     # PC sets the address bus to the high byte of the address
                    RAM_OE = True    # RAM writes the high byte of the address to the data bus
                    MAR_H_LD = True  # MAR reads the high byte off the address bus
                    PC_INC = True    # PC increments to point to the next instruction
                elif T == 3:
                    MAR_OE = True    # MAR sets the address bus to the address
                    RAM_OE = True    # RAM writes the data byte at the address to the data bus
                    A_LD = True      # Register A reads the data byte off the data bus
                    RESET_T = True   # Reset Microstep Counter for next instruction
            # STA [addr] (3-Byte, 4-Cycle)
            elif opcode == 0x03:
                if T == 1:
                    # Fetch Low-Byte
                    PC_OE = True
                    RAM_OE = True
                    MAR_L_LD = True
                    PC_INC = True
                elif T == 2:
                    # Fetch High-Byte
                    PC_OE = True
                    RAM_OE = True
                    MAR_H_LD = True
                    PC_INC = True
                elif T == 3:
                    # Write A to RAM
                    MAR_OE = True
                    A_OE = True
                    RAM_WE = True
                    RESET_T = True
            # ADD B (1-Byte 2-Cycle)
            elif opcode == 0x04:
                if T == 1:
                    ALU_OP = "ADD"  # ALU adds A and B, stores result in A, updates flags
                    RESET_T = True  # Reset Microstep Counter for next instruction
            # ADC B (1-Byte 2-Cycle)
            elif opcode == 0x05:
                if T == 1:
                    ALU_OP = "ADC"
                    RESET_T = True
            # SUB B (1-Byte 2-Cycle)
            elif opcode == 0x06:
                if T == 1:
                    ALU_OP = "SUB"
                    RESET_T = True
            # AND B (1-Byte 2-Cycle)
            elif opcode == 0x07:
                if T == 1:
                    ALU_OP = "AND"
                    RESET_T = True
            # OR B (1-Byte 2-Cycle)
            elif opcode == 0x08:
                if T == 1:
                    ALU_OP = "OR"
                    RESET_T = True
            # XOR B (1-Byte 2-Cycle)
            elif opcode == 0x09:
                if T == 1:
                    ALU_OP = "XOR"
                    RESET_T = True
            # NOTA (1-Byte 2-Cycle)
            elif opcode == 0x0A:
                if T == 1:
                    ALU_OP = "NOT"
                    RESET_T = True
            # JMP [addr] (3-Byte 3-Cycle)
            elif opcode == 0x0B:
                if T == 1:
                    PC_OE = True
                    RAM_OE = True
                    MAR_L_LD = True
                    PC_INC = True
                elif T == 2:
                    PC_OE = True
                    RAM_OE = True
                    MAR_H_LD = True
                    PC_INC = True
                elif T == 3:
                    PC_LD = True
                    RESET_T = True
            # JZ [addr] (3-Byte 4-Cycle)
            elif opcode == 0x0C:
                if T == 1:
                    PC_OE = True
                    RAM_OE = True
                    MAR_L_LD = True
                    PC_INC = True
                elif T == 2:
                    PC_OE = True
                    RAM_OE = True
                    MAR_H_LD = True
                    PC_INC = True
                elif T == 3:
                    if self.regs["Z"] == 1:
                        PC_LD = True
                    RESET_T = True
            # JC [addr] (3-Byte 4-Cycle)
            elif opcode == 0x0D:
                if T == 1:
                    PC_OE = True
                    RAM_OE = True
                    MAR_L_LD = True
                    PC_INC = True
                elif T == 2:
                    PC_OE = True
                    RAM_OE = True
                    MAR_H_LD = True
                    PC_INC = True
                elif T == 3:
                    if self.regs["C"] == 1:
                        PC_LD = True
                    RESET_T = True
            # TAX (1-Byte 2-Cycle)
            elif opcode == 0x0E:
                if T == 1:
                    A_OE = True
                    X_LD = True
                    RESET_T = True
            # TXA (1-Byte 2-Cycle)
            elif opcode == 0x0F:
                if T == 1:
                    X_OE = True
                    A_LD = True
                    RESET_T = True
            # TAB (1-Byte 2-Cycle)
            elif opcode == 0x10:
                if T == 1:
                    A_OE = True
                    B_LD = True
                    RESET_T = True
            # TBA (1-Byte 2-Cycle)
            elif opcode == 0x11:
                if T == 1:
                    B_OE = True
                    A_LD = True
                    RESET_T = True
            # INCA (1-Byte 2-Cycle)
            elif opcode == 0x12:
                if T == 1:
                    A_INC = True
                    RESET_T = True
            # DECA (1-Byte 2-Cycle)
            elif opcode == 0x13:
                if T == 1:
                    A_OE = True
                    A_DEC = True
                    RESET_T = True
            else:
                RESET_T = True

        # Fill address bus
        if PC_OE:
            self.addr_bus = self.regs["PC"]
        elif MAR_OE:
            self.addr_bus = self.regs["MAR"]
            
        # Fill data bus
        if A_OE:
            self.data_bus = self.regs["A"]
        elif B_OE:
            self.data_bus = self.regs["B"]
        elif X_OE:
            self.data_bus = self.regs["X"]
        elif RAM_OE:
            self.data_bus = self.ram[self.addr_bus]

        # Write to RAM
        if RAM_WE:
            self.ram[self.addr_bus] = self.data_bus

        # Load registers from data bus
        if IR_LD: self.regs["IR"] = self.data_bus
        if A_LD:  self.regs["A"] = self.data_bus
        if B_LD:  self.regs["B"] = self.data_bus
        if X_LD:  self.regs["X"] = self.data_bus
        
        # Load MAR from data bus
        if MAR_L_LD:
            self.regs["MAR"] = (self.regs["MAR"] & 0xFF00) | self.data_bus
        if MAR_H_LD:
            self.regs["MAR"] = (self.regs["MAR"] & 0x00FF) | (self.data_bus << 8)

        # Perform ALU operation if specified
        if ALU_OP:
            result, c, z = self.alu(self.regs["A"], self.regs["B"], ALU_OP)
            self.regs["A"] = result
            self.regs["C"] = c
            self.regs["Z"] = z

        # Update registers
        if A_INC:
            self.regs["A"] = (self.regs["A"] + 1) & 0xFF
        elif A_DEC:
            self.regs["A"] = (self.regs["A"] - 1) & 0xFF
        if PC_LD:
            self.regs["PC"] = self.regs["MAR"]
        elif PC_INC:
            self.regs["PC"] = (self.regs["PC"] + 1) & 0xFFFF
        if RESET_T:
            self.regs["T"] = 0
        else:
            self.regs["T"] += 1

    def print_state(self):
        print(f"T:{self.regs['T']} | PC:{self.regs['PC']:04X} | IR:{self.regs['IR']:02X} | "
              f"A:{self.regs['A']:02X} | B:{self.regs['B']:02X} | X:{self.regs['X']:02X} | "
              f"MAR:{self.regs['MAR']:04X} | Z:{self.regs['Z']} C:{self.regs['C']}")