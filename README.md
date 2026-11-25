# final-project-track-A

V&V final project, Track A (RV32I core). Branch `trackA-RISCV-v1` holds the starting code.

## Layout (matches the course guide; run everything from `code/`)

```
code/
  lib/                  <- MISSING: copy the course lib/ here (models/rv32i_model.py, craft_mutate/)
  capstone/riscv/       <- the track folder (the one you zip for Gradescope)
    Makefile            MODULE = test_smoke,test_final  (the one edited line)
    test_smoke.py       shipped smoke test, unchanged
    test_final.py       the tests printed in the guide (sections 3, 4, 5, 8)
    env/                core_env.py, stimulus.py, coverage.py, from the guide
    probe.py            the guide's ISS-only stimulus probe
```

The env/test/probe files were typed in from the guide PDF. Compare them with the
official `final-guide-track-a-files.zip` from Webcourses and keep that version if they differ.
Every "Yours" item in the guide is still open, and so are all the .md deliverables and REPORT.pdf.

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
It fails at its first step until `code/lib/` is committed.
