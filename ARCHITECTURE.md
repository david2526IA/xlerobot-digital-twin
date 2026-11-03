# Architecture

```text
CAD and official assets
          |
          v
Canonical URDF and parameter manifest
          |
          +-------------------+
          |                   |
          v                   v
       MuJoCo             Isaac Lab
  validation and PPO   optional parity path
          |
          v
Episode telemetry contract
qpos qvel RGB action timestamps
          |
          v
Evaluation protocol and evidence
          |
          v
Hardware gate only after calibration and safety review
```

The canonical action vector has 16 entries: differential-base forward/turn,
six joints for each arm including grippers, and neck pan/tilt. The initial PPO
curriculum exposes only the four right-arm reach joints. This limits the first
experiment to a verifiable kinematic task before grasping, navigation or
bimanual coordination.

`calibration/model_parameters.yaml` records parameter provenance. Measurements
from a physical robot belong in ignored `calibration/measurements.yaml`; a
hardware bridge must consume only measured or reviewed values.
