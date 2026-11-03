# Phase 0 audit

Date: 2026-11-02

## Available evidence

- The repository includes a v0.4 URDF, MuJoCo model, parameter provenance,
  gamepad teleoperation, simulated episode export, PPO/CEM scripts and CI.
- Local hardware inventory reports an NVIDIA GeForce RTX 5070 Laptop GPU with
  8 GB VRAM and Isaac Lab 2.7 installed.
- The current calibration file is an example template. No physical measurement
  record or real robot deployment evidence was found.

## Decision

Proceed with a simulation-only MVP: compare a nominal PPO run against a
domain-randomized PPO run on the same right-arm reach protocol. Do not enable
the hardware gate.

## Backlog

1. Run and record the nominal baseline on three training seeds.
2. Run the randomized variant with identical evaluation seeds.
3. Generate a compact results table and label all evidence as simulated.
4. Populate measurements only after a physical calibration session.
5. Review the hardware safety gate before any robot command is connected.
