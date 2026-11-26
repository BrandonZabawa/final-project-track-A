"""env/coverage.py -- functional coverage for the RV32I core (cocotb-coverage)."""
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db

from env.core_env import HALT

R_TYPE = {(0, 0x00): "add", (0, 0x20): "sub", (7, 0x00): "and", (6, 0x00): "or", (4, 0x00): "xor"}
OTHERS = {(0x13, 0): "addi", (0x13, 7): "andi", (0x13, 6): "ori",
          (0x03, 2): "lw", (0x23, 2): "sw", (0x63, 0): "beq"}
NAMES = list(R_TYPE.values()) + list(OTHERS.values()) + ["jal"]
NO_DEST = ["sw", "beq"]                       # S and B types have no rd (SPEC.md table)


def kind_of(word):
    """The contract-table row an instruction word belongs to, or None."""
    opcode, funct3, funct7 = word & 0x7F, (word >> 12) & 7, word >> 25
    if opcode == 0x33:
        return R_TYPE.get((funct3, funct7))
    return "jal" if opcode == 0x6F else OTHERS.get((opcode, funct3))


@CoverPoint("rv.kind", xf=lambda kind, word: kind, bins=NAMES)
@CoverPoint("rv.dest", xf=lambda kind, word: (word >> 7) & 31 == 0, bins=[True, False],
            bins_labels=["x0", "other"])
@CoverCross("rv.kind_x_dest", items=["rv.kind", "rv.dest"],
            ign_bins=[(k, d) for k in NO_DEST for d in ("x0", "other")])
def sample_instr(kind, word):
    """Every instruction: which row of the table, and is its destination x0?"""


@CoverPoint("rv.beq_taken", xf=lambda taken, back: taken, bins=[True, False],
            bins_labels=["taken", "not taken"])
@CoverPoint("rv.beq_dir", xf=lambda taken, back: back, bins=[True, False],
            bins_labels=["backward", "forward"])
@CoverCross("rv.beq_taken_x_dir", items=["rv.beq_taken", "rv.beq_dir"])
def sample_beq(taken, back):
    """beq only: the outcome, and which way the target lies."""


# TODO (guide section 5, "Yours"): the model above never looks at operand values,
# immediates, or addresses. Add coverpoints your plan calls for, e.g.
#   rv.imm_corner  : imm in {-2048, -1, 0, 1, 2047} for I-type
#   rv.addr_wrap   : lw/sw effective address past word 63 (F15)
#   rv.rs1_eq_rs2  : beq with rs1 == rs2 vs. two different registers
# Write the sampling function the same way as sample_beq, call it from sample(),
# and expect the overall % to DROP -- that is progress (closure.md section 2).


def sample(word, iss):
    """The env calls this before each instruction: the word, and the state before it."""
    kind = kind_of(word)
    if kind is None or word == HALT:          # not in the table, or the halt
        return
    sample_instr(kind, word)
    if kind == "beq":
        rs1, rs2 = (word >> 15) & 31, (word >> 20) & 31
        sample_beq(iss.reg(rs1) == iss.reg(rs2), bool(word >> 31))  # bit 31: the offset's sign


def pct(name):
    return coverage_db[name].cover_percentage
