"""test_final.py -- Track A final-project suite, built step by step in the track guide.

STARTING FLOOR: these tests are the ones printed in the Track A field guide
(sections 3, 4, 5 and 8). Every "Yours" item in the guide is still open.
"""
import os
import random

import cocotb
from cocotb_coverage.coverage import coverage_db
from models.rv32i_model import ADD, ADDI, BEQ, LW, SW

from env.core_env import HALT, CoreEnv
from env.coverage import pct, sample
from env.stimulus import Instr, random_program, random_state

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = int(os.environ.get("SEED", "0xC0FFEE"), 0)   # the default is the seed you report
PROGRAMS = 30
TABLE_OPCODES = {0x33, 0x13, 0x03, 0x23, 0x63, 0x6F}  # the six opcodes the 12 rows use


@cocotb.test()
async def test_first_program(dut):
    """F1, F6, F9, F10: add, addi, lw, sw through the new environment."""
    env = CoreEnv(dut)
    await env.load([ADDI(1, 0, 7), ADD(2, 1, 1), SW(2, 0, 16), LW(3, 0, 16), HALT])
    await env.run(8, "first")
    dut._log.info(f"checked {env.checked} instructions against the ISS")


@cocotb.test()
async def test_random_programs(dut):
    """F1-F12: constrained-random programs, every instruction checked against the ISS."""
    random.seed(SEED)                       # pyvsc draws from Python's random module
    env, it, curve = CoreEnv(dut), Instr(), []
    env.watch = sample                      # coverage sees every instruction
    for p in range(PROGRAMS):
        words = random_program(it, pool=random.choice([4, 8, 32]))
        data, regs = random_state()
        await env.load(words, data=data, regs=regs)
        while not env.halted:               # run to the halt in the last word
            await env.run(1, f"seed {SEED:#x} program {p}")
        curve.append(f"{p + 1},{env.checked},{pct('rv.kind_x_dest'):.1f},"
                     f"{pct('rv.beq_taken_x_dir'):.1f}")
    dut._log.info(f"checked {env.checked} instructions against the ISS")
    with open(os.path.join(HERE, "curve.csv"), "w") as fh:
        fh.write("programs,instructions,kind_x_dest,beq_taken_x_dir\n" + "\n".join(curve) + "\n")


@cocotb.test()
async def test_loop_backward(dut):
    """F11: beq backward, taken and then not taken: the two cells random cannot reach."""
    env = CoreEnv(dut)
    env.watch = sample
    await env.load([ADDI(1, 0, 1),          # 0x00  x1 = 1
                    ADD(2, 2, 1),           # 0x04  x2 = x2 + 1     (1, then 2)
                    BEQ(2, 1, -4),          # 0x08  back to 0x04 while x2 == x1
                    HALT])                  # 0x0C
    await env.run(6, "loop")
    assert env.halted, "the loop did not end at the halt"
    coverage_db.report_coverage(dut._log.info, bins=True)
    coverage_db.export_to_yaml(filename=os.path.join(HERE, "coverage.yml"))


@cocotb.test()
async def test_outside_the_table(dut):
    """F13: SPEC.md says a word outside the table is a no-op. Measure it."""
    random.seed(SEED)
    env, changed = CoreEnv(dut), []
    for opcode in sorted(set(range(128)) - TABLE_OPCODES):
        word = (random.getrandbits(25) << 7) | opcode      # any other bits
        await env.load([ADDI(1, 0, 7), word, HALT],
                       data=[random.getrandbits(32) for _ in range(64)],
                       regs=[random.getrandbits(32) for _ in range(32)])
        await env.run(1, "setup")
        regs, mem, pc = env.state()
        await env.run(1, f"word {word:#010x}")
        if env.state() != (regs, mem, pc + 4):             # a no-op moves pc by 4, only
            changed.append(f"{word:#010x}")
    dut._log.info(f"{len(changed)} of 122 opcodes outside the table changed state: {changed}")
    assert not changed, f"not a no-op: {changed}"
