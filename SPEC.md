# Sim to Real Robotics Pipeline Specification

## Objective

Build a reproducible pipeline for an XLeRobot 0.4 differential-drive mobile
manipulator: validate a CAD-derived digital twin, train and compare nominal and
domain-randomized policies in simulation, then prepare a safety-gated transfer
to real hardware.

## MVP scope

The MVP is simulation-first. It includes a fixed reach task, a documented PPO
baseline, a domain-randomized variant, held-out simulation evaluation and an
evidence package. Real deployment is explicitly out of scope until calibration
measurements and safety checks are recorded.

## System boundary

- Robot model: XLeRobot 0.4 dual-wheel base, two SO-101 arms, neck and camera.
- Simulator: MuJoCo is the training baseline; Isaac Lab is an optional parity
  path, not a claimed validation target.
- Policy task: right-arm tabletop reach before grasping or mobile manipulation.
- Data: simulated episodes only unless a separately documented hardware session
  is approved.

## Acceptance criteria

1. A clean environment runs validation, training and evaluation commands.
2. The nominal and randomized policies share task, horizon, action contract and
   held-out seed protocol.
3. Results report seed count, episode count, success rate and conditions; no
   unmeasured physical performance is claimed.
4. The hardware gate requires a populated calibration record, speed limits,
   watchdog, emergency stop and progressive test evidence.

## Risks

- The repository contains a CAD-derived model, not an upstream-certified v0.4
  URDF; masses, friction, latency and camera parameters are provisional.
- An 8 GB laptop GPU is suitable for small PPO experiments, not large-scale
  Isaac Lab or foundation-policy training.
- Hardware identifiers and raw camera recordings may be sensitive and remain
  outside version control.

## Non-goals

This project does not claim autonomous physical deployment, a calibrated grasp
policy, VR validation, or real-world sim-to-real transfer before measurements
exist.
