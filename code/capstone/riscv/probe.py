# probe.py -- measure YOUR programs on the ISS alone, before you simulate.
# Save next to test_final.py (code/capstone/riscv/). Course env active:  python probe.py
import random
import sys
from collections import Counter
sys.path.insert(0, "../../lib")              # the path the Makefile gives cocotb
from models.rv32i_model import RV32I
from env.core_env import HALT
from env.coverage import kind_of
from env.stimulus import Instr, random_program, random_state

random.seed(1)
it, seen = Instr(), Counter()
for _ in range(20):
    words = random_program(it, pool=random.choice([4, 8, 32]))
    iss = RV32I(words)
    iss.dmem, regs = random_state()
    iss.regs = [0] + regs[1:]
    while words[iss.pc >> 2] != HALT:
        word = words[iss.pc >> 2]
        kind = kind_of(word)
        rs1, rs2 = (word >> 15) & 31, (word >> 20) & 31
        seen["instructions run"] += 1
        seen[kind] += 1
        if kind == "beq":
            taken = iss.reg(rs1) == iss.reg(rs2)
            seen["beq taken" if taken else "beq not taken"] += 1
            seen["beq taken, two different registers"] += taken and rs1 != rs2
        # TODO (guide section 4, "Yours"): add one counter per corner in your plan, e.g.
        #   seen["imm at an end of its range"]  -- imm == -2048 or 2047 (decode the word)
        #   seen["lw reads a word sw wrote"]    -- keep a set of word indexes stored so far
        #   seen["address past word 63"]        -- (iss.reg(rs1) + imm) >> 2 >= 64 for lw/sw
        # Then reshape VALUES / shape_c in env/stimulus.py until no counter is zero.
        iss.step()
for name, n in seen.items():
    print(f"{name:36s} {n:5d}")
