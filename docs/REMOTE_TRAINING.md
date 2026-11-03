# Training the Simulation Protocol on Another Computer

The full sim-to-real comparison is intentionally deferred. This repository
contains the protocol and configuration, but no long-run result is claimed
until it is executed on a suitable machine and the resulting evidence is
recorded.

## 1. Clone and prepare

Use Python 3.12 and a clean virtual environment. A CUDA-capable NVIDIA GPU is
recommended for the full PPO runs, but the commands can also run on CPU for
small checks.

```bash
git clone https://github.com/david2526IA/xlerobot-digital-twin.git
cd xlerobot-digital-twin
python3.12 -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux
source .venv/bin/activate
```

Install the RL environment and validate the repository before training:

```bash
python -m pip install --upgrade pip
pip install -r requirements-rl.txt
pip install -e .
python scripts/validate_twin.py
python scripts/smoke_env.py
pytest -q
```

Stop here if validation fails. Do not start a long run with an unverified
MuJoCo model or a modified action contract.

## 2. Run the experiment protocol

The canonical configuration is `configs/sim2real_baseline.yaml`. It specifies:

- three training seeds for each condition;
- three held-out evaluation seeds;
- 20 evaluation episodes per evaluation seed;
- 100,000 PPO timesteps per training run;
- a nominal condition and a domain-randomized condition;
- a hardware gate that remains disabled.

Run the nominal baseline first:

```bash
python scripts/run_sim2real_protocol.py \
  --condition nominal \
  --output-dir outputs/sim2real
```

Then run the randomized condition with the same protocol:

```bash
python scripts/run_sim2real_protocol.py \
  --condition randomized \
  --output-dir outputs/sim2real
```

On Windows PowerShell, replace the line-continuation backslash with a backtick
or put each command on one line.

## 3. What the protocol saves

Each condition creates `outputs/sim2real/<condition>/` containing:

- one PPO checkpoint and run manifest for every training seed;
- one JSON metrics file for every checkpoint/evaluation-seed pair;
- `summary.json` with the complete protocol record.

Keep these files together with the commit SHA, Python/PyTorch versions and GPU
name. Do not compare runs that used different task definitions, action modes,
evaluation seeds or episode counts.

## 4. Record results honestly

Copy only small summaries to `results/`. For each condition report the number
of training seeds, number of held-out episodes, mean and variability of success
rate, the exact commit, command, device and relevant training settings. Label
the result as **simulation only**.

The protocol does not permit hardware execution. `hardware_gate.allowed` must
remain `false` until physical calibration, an emergency-stop check, watchdog
check and low-speed suspended test are documented.

## 5. Optional smoke check

For a quick installation check, not a scientific result:

```bash
python scripts/run_sim2real_protocol.py \
  --config configs/sim2real_smoke.yaml \
  --condition nominal \
  --output-dir outputs/sim2real_smoke
```

This tiny run is also exercised by CI. It must never be reported as the
100,000-step experiment.
