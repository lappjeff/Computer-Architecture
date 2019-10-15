"""CPU functionality."""

import sys
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * \
            0xFF  # Random Access MEMORY - has 0xFF hex, aka  256 bits - Each index should contain an instruction, like ADD or LDI along with whatever params it needs following it
        self.reg = [0] * 0x08  # registries - 8 registries
        self.pc = 0
        self.sp = 7
        self.reg[7] = 0xF4
        self.mar = 0  # Memory Address Register, holds the MEMORY ADDRESS we're reading or writing
        self.mdr = 0  # Memory Data Register, holds the VALUE to write or the VALUE just read
        self.branch_table = {
            "alu_ops": {
                MUL: "MUL"
            },
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            HLT: self.handle_hlt,
            PUSH: self.handle_push,
            POP: self.handle_pop
        }

    def ram_read(self, address):
        self.mar = address
        self.mdr = self.ram[self.mar]
        return self.mdr

    def ram_write(self, address, value):
        """
        Value - value to insert at address
        Address - address in ram to insert param value at
        """
        self.mar = address
        self.mdr = value
        self.ram[self.mar] = self.mdr

    def handle_ldi(self, address, value):
        self.reg[address] = value

    def handle_prn(self, address, *args):
        value = self.reg[address]
        print(value)

    def handle_push(self, address, *args):
        # index of register with desired value, retreived from RAM
        reg_index = address
        # value of register that we want to copy over to stack
        value = self.reg[reg_index]
        # decrement value stored in R7(starts as 0xF4 -- 244)
        self.reg[self.sp] -= 1
        # write register value to stack at the index number found in R7
        self.ram_write(self.reg[self.sp], value)

    def handle_pop(self, address, *args):
        # index of register for popped stack value to be inserted at
        reg_index = address
        # value to insert at register index
        value = self.ram_read(self.reg[self.sp])
        # insert value at reg_index
        self.reg[reg_index] = value
        # reduce size of stack
        self.reg[self.sp] += 1

    def handle_hlt(self):
        sys.exit(1)

    def load(self, file_path):
        """Load a .ls8 file from given path and insert into memory."""

        try:
            address = 0

            with open(file_path) as f:
                for line in f:
                    # split line at hash symbol
                    comment_split = line.split('#')

                    # convert from binary string to number and strips all surrounding whitespace
                    binary_string = comment_split[0].strip()
                    try:
                        num = int(binary_string, base=2)
                    except ValueError:
                        continue
                    self.ram_write(address, num)
                    address += 1
        except FileNotFoundError:
            print(
                f"File could not be found. Please make sure you are using a valid file path")
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        while running is True:
            lr = self.ram_read(self.pc)
            if lr == HLT:
                self.branch_table[lr]()
            elif lr in self.branch_table:

                address = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)

                self.branch_table[lr](address, value)
                self.pc += (lr >> 6) + 1

            elif lr in self.branch_table["alu_ops"]:
                # op key from branch_table nested alu_ops table
                op = self.branch_table["alu_ops"][lr]
                # registry a
                reg_a = self.ram_read(self.pc + 1)
                # registry b
                reg_b = self.ram_read(self.pc + 2)

                # call alu operation with above vars
                self.alu(op, reg_a, reg_b)
                self.pc += (lr >> 6) + 1
            else:
                print(f"Invalid command {lr}")
                self.pc += 1
