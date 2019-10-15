"""CPU functionality."""

import sys
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * \
            0xFF  # Random Access MEMORY - has 0xFF hex, aka  256 bits - Each index should contain an instruction, like ADD or LDI along with whatever params it needs following it
        self.reg = [0] * 0x08  # registries - 8 registries
        self.pc = 0
        self.mar = 0  # Memory Address Register, holds the MEMORY ADDRESS we're reading or writing
        self.mdr = 0  # Memory Data Register, holds the VALUE to write or the VALUE just read
        self.branch_table = {
            LDI: self.handle_ldi,
            PRN: self.handle_prn,
            HLT: self.handle_hlt
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

    def handle_ldi(self, address=None):
        address = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[address] = value
        # self.pc += 3

    def handle_prn(self):
        address = self.ram[self.pc + 1]
        value = self.reg[address]
        print(value)
        # self.pc += 2

    def handle_hlt(self):
        sys.exit(1)

    def load(self, file_path):
        """Load a program into memory."""

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

        #  program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        # elif op == "SUB": etc
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
            # print(lr)
            if lr in self.branch_table:
                self.branch_table[lr]()
                self.pc += (lr >> 6) + 1
            elif lr == HLT:
                running = False
            else:
                print(f"Invalid command {lr}")
                self.pc += 1
