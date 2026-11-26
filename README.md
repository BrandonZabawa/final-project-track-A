# final-project-track-A

V&V final project, Track A (RV32I core). Branch `trackA-RISCV-v1` holds the starting code.

## Layout (matches the course guide; run everything from `code/`)

```
code/
  lib/                  course lib: models/rv32i_model.py (the ISS), craft_mutate/ (the harness)
  capstone/riscv/       <- the track folder (the one you zip for Gradescope)
    Makefile            MODULE = test_smoke,test_final  (the one edited line)
    test_smoke.py       shipped smoke test, unchanged
    test_final.py       the tests printed in the guide (sections 3, 4, 5, 8)
    env/                core_env.py, stimulus.py, coverage.py, from the guide
    probe.py            the guide's ISS-only stimulus probe (+ TODO counters)
    test_yours.py       SCAFFOLD: skipped stubs with TODO comments for the guide's "Yours" tests
    mutants_mine.yaml   SCAFFOLD: format + ideas; your bugs go here
    lint_waivers.vlt    the guide's two waivers; two warnings left for you to explain
```

The env/test/probe files were typed in from the guide PDF. Compare them with the
official `final-guide-track-a-files.zip` from Webcourses and keep that version if they differ.
The test_yours.py stubs, the TODO comments, and the scaffold files were written with AI
help (comments and setup only); the test bodies and every "Yours" item are still open, and so are all the .md deliverables and REPORT.pdf.

## Run on eustis

```bash
source /opt/course/cocotb-env/bin/activate
cd code
export PYTHONPATH="$PWD/lib"
make -s -C capstone/riscv SIM=icarus
python -m craft_mutate.mutate --tb capstone/riscv --sim icarus \
    --pool capstone/riscv/mutants_released.yaml --dut-dir capstone/riscv
```

## CI

`.github/workflows/track-a.yml` runs the suite, the released pool and lint on every push.
Measured here (Icarus 12.0, cocotb 1.9.2): 5/5 tests pass, released pool 8/8, 4 lint warnings.
