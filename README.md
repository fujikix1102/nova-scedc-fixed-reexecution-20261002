# NOVA SCEDC Fixed Re-execution

This repository contains a reproducible SCEDC seismic waveform/phase-pick audit.

## Scope

- Four SCEDC events
- Four stations where available
- Fixed BHZ preprocessing and STA/LTA trigger contract
- SHA-256 verification for every waveform and phase file
- formal_pass: false is enforced

## Reproduction

Run:

```bash
python -m pip install -r requirements.txt
python third_party_reexecution/run_scedc_fixed_phase_parity_v1.py
```

GitHub Actions performs the same input, runner, and output checks on Ubuntu 24.04.

This is an exploratory numerical re-execution. It is not a certified seismic location result, instrument calibration, or third-party human validation.

## Evidence and reporting

Before running, verify all input SHA-256 values. Report the operating system, Python and dependency versions, runner revision, input hashes, output hash, record count, test result, and failure reason. Automated Actions execution is not human third-party reproduction.

External calibration and independent human execution are separate evidence requirements. Keep formal_pass=false unless they are established for this exact bundle.
