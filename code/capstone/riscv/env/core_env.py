"""env/core_env.py -- driver, monitor, and scoreboard for the RV32I core, in step with the ISS."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge
from models.rv32i_model import BEQ, RV32I

WORDS = 64                                  # words in each memory (SPEC.md, Memory map)
HALT = BEQ(0, 0, 0)                         # a branch to itself: the program stops here


class CoreEnv:
    def __init__(self, dut):
        self.dut = dut
        self.iss = None                     # the reference; load() makes it
        self.watch = None                   # coverage hook: watch(word, iss)
        self.clocked = False
        self.checked = 0                    # instructions compared so far

    async def load(self, program, data=None, regs=None):
        """Driver: put a program in by the back door, then let reset go."""
        d = self.dut
        if not self.clocked:
            cocotb.start_soon(Clock(d.clk, 10, units="ns").start())
            self.clocked = True
        d.dbg_sel.value = 0
        d.dbg_dmem_idx.value = 0
        d.rst_n.value = 0
        for i in range(WORDS):              # no-ops while reset is low: the core
            d.u_imem.mem[i].value = 0       #   still runs the word at pc in reset
        await RisingEdge(d.clk)
        await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        words = (list(program) + [0] * WORDS)[:WORDS]
        data = (list(data or []) + [0] * WORDS)[:WORDS]
        regs = [0] + (list(regs or []) + [0] * 32)[1:32]
        for i in range(WORDS):
            d.u_imem.mem[i].value = words[i]
            d.u_dmem.mem[i].value = data[i]
        for i in range(32):                 # the register file has no reset: a
            d.u_core.regs[i].value = regs[i]  # register nobody wrote is X, not 0
        d.rst_n.value = 1
        self.iss = RV32I(words)             # the reference starts from the same state
        self.iss.dmem, self.iss.regs = list(data), list(regs)

    async def run(self, n, name="run"):
        """Run n instructions. After each one, compare the core with the ISS."""
        for k in range(n):
            pc = self.iss.pc                # the instruction about to run
            if self.watch:                  # monitor: tell coverage what is about to run
                self.watch(self.iss.imem[(pc >> 2) % WORDS], self.iss)
            self.iss.step()                 # the reference runs it first
            await RisingEdge(self.dut.clk)  # the core runs it on this edge
            await FallingEdge(self.dut.clk)  # its new state has settled by here
            self.check(f"{name}: instruction {k} at pc {pc:#x}")
            self.checked += 1

    def check(self, where):
        """Scoreboard: every register against the ISS, read by the back door."""
        for i in range(1, 32):
            got = int(self.dut.u_core.regs[i].value)
            want = self.iss.reg(i)
            assert got == want, f"{where}: x{i} = {got:#010x}, the ISS says {want:#010x}"

    def state(self):
        """All architectural state, by the back door: (registers, data memory, pc)."""
        d = self.dut
        return ([int(d.u_core.regs[i].value) for i in range(1, 32)],
                [int(d.u_dmem.mem[i].value) for i in range(WORDS)],
                int(d.u_core.pc.value))

    @property
    def halted(self):
        """True when the next instruction is the halt."""
        return self.iss.imem[(self.iss.pc >> 2) % WORDS] == HALT
