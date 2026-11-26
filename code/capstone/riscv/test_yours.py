"""test_yours.py -- the guide's open "Yours" tests, as stubs to fill in.

HOW TO USE
  * Each test below is skipped (skip=True) so the suite stays green.
  * When you start one: delete `skip=True`, write the body, run
        make -s -C capstone/riscv SIM=icarus TESTCASE=<test_name>
    (from code/, PYTHONPATH set) to run just that test.
  * Every helper you need already exists:
        env = CoreEnv(dut)                 # driver + monitor + scoreboard
        await env.load(program, data=..., regs=...)   # back-door load, then reset
        await env.run(n, "name")           # n instructions, each checked vs. the ISS
        env.state()                        # (regs x1..x31, dmem[0..63], pc)
        env.halted                         # True when the next word is HALT
        env.iss                            # the reference model, after load()
  * Closest worked example for almost all of these: test_loop_backward in test_final.py.
  * When one passes, add its row to vplan.md section 4 (test -> feature IDs).

Scaffold only: the comments and setup were written with AI help; the test bodies are yours.
"""
import os
import random

import cocotb
from models.rv32i_model import ADD, ADDI, BEQ, JAL, LW, SW  # noqa: F401  (use what you need)

from env.core_env import HALT, WORDS, CoreEnv  # noqa: F401
from env.coverage import kind_of, sample  # noqa: F401

SEED = int(os.environ.get("SEED", "0xC0FFEE"), 0)


# ---------------------------------------------------------------------------
# 1. F12 -- jal with a NEGATIVE offset (guide section 6)
# ---------------------------------------------------------------------------
@cocotb.test(skip=True)
async def test_jal_backward(dut):
    """F12: jal jumps backward and links pc + 4. Finds jal_backward_wrong."""
    # WHY: no program in the suite jumps backward with jal, so the bug
    #      jal_backward_wrong in the guide's mutants_mine.yaml survives (a REACHABILITY gap).
    #
    # TODO 1  Make env, attach coverage (env.watch = sample), like test_loop_backward.
    # TODO 2  Write a short program in which a JAL has a negative offset.
    #         Pitfall: a backward jump can loop forever. Plan the layout so that
    #         after jumping back, execution reaches HALT. Idea: start with a
    #         forward jump over a block, put the backward JAL after it, and make
    #         the block it lands in lead to HALT. Draw the addresses (0x00, 0x04, ...)
    #         as comments, the way test_loop_backward does.
    # TODO 3  Check that rd != x0, so the link value (pc + 4) is actually compared.
    # TODO 4  await env.run(<number of instructions you expect>, "jal_back")
    # TODO 5  assert env.halted, with a message.
    # CHECK   Add the jal_backward_wrong entry to mutants_mine.yaml and confirm the
    #         harness now reports it [found].


# ---------------------------------------------------------------------------
# 2. F14 -- x0 reads 0 and ignores writes
# ---------------------------------------------------------------------------
@cocotb.test(skip=True)
async def test_x0_hardwired(dut):
    """F14: every instruction kind that writes rd, with rd = x0, leaves x0 = 0."""
    # WHY: SPEC.md, Register model. The scoreboard checks x1..x31 only (see
    #      CoreEnv.check, range(1, 32)), so a write to x0 is NOT caught today.
    #      Is that a reachability gap or an observability gap? (Answer it in FINDINGS.md.)
    #
    # TODO 1  Build a program with one instruction of each kind that has an rd
    #         (add sub and or xor addi andi ori lw jal) all writing rd = 0.
    #         Pitfall: jal changes pc. Use a small offset (e.g. 4) so it falls through.
    # TODO 2  After each instruction (or at the end), read x0 by the back door:
    #         int(dut.u_core.regs[0].value). Decide: compare with 0, or also check
    #         that later instructions READING x0 get 0 (e.g. ADD(5, 0, 0)).
    # TODO 3  Assert, with a message naming the instruction.
    # THINK   Should CoreEnv.check() start at 0 instead of 1? What breaks if it does?


# ---------------------------------------------------------------------------
# 3. F15 -- memory index = (addr >> 2) mod 64
# ---------------------------------------------------------------------------
@cocotb.test(skip=True)
async def test_memory_wrap(dut):
    """F15: an address past word 63 wraps to (addr >> 2) % 64, for sw and lw."""
    # WHY: SPEC.md, Memory map. Random stimulus almost never forms such an address
    #      (add a counter to probe.py to prove it).
    #
    # TODO 1  Put a base address in a register that points past 63 words
    #         (e.g. 64 * 4 = 0x100 lands on word 0 -- pick one or two cases).
    # TODO 2  SW a known value through it; LW it back through the wrapped
    #         address AND through the plain address it aliases.
    # TODO 3  After the run, compare dmem with env.state()[1] -- the scoreboard does
    #         not compare memory on its own (guide section 3, "Yours").
    # TODO 4  Add an unaligned case too? The guide's risk list asks if it is legal.
    #         If you add it, say in vplan.md what you decided and why.


# ---------------------------------------------------------------------------
# 4. F16 -- reset returns pc to 0
# ---------------------------------------------------------------------------
@cocotb.test(skip=True)
async def test_reset_pc(dut):
    """F16: after running somewhere, a reset brings pc back to 0."""
    # TODO 1  Load and run a few instructions so pc is no longer 0.
    # TODO 2  Load again (load() pulses rst_n) -- or drive dut.rst_n yourself.
    #         Pitfall: load() also rewrites memories; decide whether that is OK here.
    # TODO 3  Check int(dut.u_core.pc.value) == 0 right after reset is released,
    #         before any instruction runs.
    # THINK   Guide risk: while rst_n is low the core still executes the word at pc.
    #         Can you write a test that shows that? It belongs in the risk list.


# ---------------------------------------------------------------------------
# 5. F13 part 2 -- table opcodes with funct3/funct7 outside the table (guide section 8)
# ---------------------------------------------------------------------------
@cocotb.test(skip=True)
async def test_outside_the_table_subcodes(dut):
    """F13: words with a table opcode but an unlisted funct3/funct7 are no-ops."""
    # WHY: test_outside_the_table only sweeps the 122 unused OPCODES. A word can
    #      use opcode 0x33 or 0x13 (or 0x03, 0x23, 0x63) with a funct3/funct7 the
    #      table does not list. kind_of(word) returns None for exactly these words.
    #
    # TODO 1  Copy test_outside_the_table's loop structure.
    # TODO 2  Instead of looping over opcodes, loop over (opcode, funct3, funct7)
    #         combinations; keep only those where kind_of(word) is None.
    #         Pitfall: for 0x33 funct7 is 7 bits (128 values) x 8 funct3 -- that is
    #         ~1000 words; measure run time and stay well under 90 s in total.
    #         Sampling is fine if you say how many you sampled.
    # TODO 3  Same check: env.state() before vs. after == (regs, mem, pc + 4).
    # TODO 4  Log "<n> of <m> changed state" -- that line goes in the report's
    #         security verdict.
    # THINK   If the core and the ISS BOTH change state on such a word, the
    #         scoreboard stays quiet. What does the ISS do with these words?
    #         (Read RV32I.step() in lib/models/rv32i_model.py.)


# ---------------------------------------------------------------------------
# 6. Scoreboard gap -- is a wrong sw caught? (guide section 3, "Yours")
# ---------------------------------------------------------------------------
@cocotb.test(skip=True)
async def test_store_is_checked(dut):
    """F10: a store whose value is never loaded back is still compared."""
    # WHY: CoreEnv.check() compares registers only. A sw that writes the wrong
    #      word is caught only if something later loads it.
    #
    # TODO 1  Program: a few SWs to different words, then HALT -- no LW.
    # TODO 2  Run it, then compare env.state()[1] with env.iss.dmem.
    # TODO 3  Decide: fix it here only, or extend CoreEnv.check() (in env/core_env.py)
    #         to compare dmem and pc after every instruction? Measure the run-time
    #         cost of each choice, and write the decision in vplan.md.
    # CHECK   Write a mutant in mutants_mine.yaml that breaks only sw, and show the
    #         before/after found/total.
