"""env/stimulus.py -- constrained-random programs for the RV32I core (pyvsc)."""
import random

import vsc
from models.rv32i_model import ADD, ADDI, AND, ANDI, BEQ, JAL, LW, OR, ORI, SUB, SW, XOR

from env.core_env import HALT

K_LW, K_SW, K_BEQ, K_JAL = 8, 9, 10, 11       # kinds 0-4 are R type, 5-7 are I type
LAST = 63                                     # the halt goes in the last word
VALUES = [0, 1, 0xFFFFFFFF]                   # starting values: add the ones that matter


@vsc.randobj
class Instr:
    """One instruction from the 12-row contract table in SPEC.md."""

    def __init__(self):
        self.kind = vsc.rand_uint8_t()        # which row of the table
        self.rd = vsc.rand_bit_t(5)
        self.rs1 = vsc.rand_bit_t(5)
        self.rs2 = vsc.rand_bit_t(5)
        self.imm = vsc.rand_int16_t()         # signed; legal_c narrows it to 12 bits
        self.hop = vsc.rand_int8_t()          # branch or jump distance, in instructions
        self.pool = vsc.uint8_t(32)           # not rand: the test sets these two
        self.left = vsc.uint8_t(LAST)         #   before each randomize()

    @vsc.constraint
    def legal_c(self):                        # the contract: what is legal at all
        self.kind < 12
        self.imm >= -2048
        self.imm <= 2047

    @vsc.constraint
    def shape_c(self):                        # your choices: where the run spends its time
        self.rd < self.pool                   # a small pool makes instructions
        self.rs1 < self.pool                  #   use each other's results
        self.rs2 < self.pool
        self.hop > 0                          # forward only, and never past
        self.hop <= self.left                 #   the halt: every program ends
        self.hop <= 4

    def word(self):
        """Encode this instruction with the course assembler."""
        k, rd, rs1, rs2 = int(self.kind), int(self.rd), int(self.rs1), int(self.rs2)
        imm, offset = int(self.imm), 4 * int(self.hop)
        if k < 5:
            return (ADD, SUB, AND, OR, XOR)[k](rd, rs1, rs2)
        if k < 8:
            return (ADDI, ANDI, ORI)[k - 5](rd, rs1, imm)
        if k == K_LW:
            return LW(rd, rs1, imm)
        if k == K_SW:
            return SW(rs2, rs1, imm)
        if k == K_BEQ:
            return BEQ(rs1, rs2, offset)
        return JAL(rd, offset)


def random_program(it, pool=32):
    """63 random instructions and then the halt, as a list of words."""
    words = []
    it.pool = pool                            # how many registers this program uses
    for slot in range(LAST):
        it.left = LAST - slot                 # feed the state in: how far the halt is
        it.randomize()
        words.append(it.word())
    return words + [HALT]


def random_state():
    """Starting (data memory, registers), drawn from VALUES so that values meet again."""
    return ([random.choice(VALUES) for _ in range(64)],
            [random.choice(VALUES) for _ in range(32)])
