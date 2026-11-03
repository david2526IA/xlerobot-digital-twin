# Limitations

- The XLeRobot 0.4 URDF is reconstructed from official CAD and controller
  references. It is not an official upstream URDF and is not a physical twin.
- Wheel geometry, mass distribution, servo dynamics, friction, camera
  intrinsics/extrinsics and end-to-end latency remain unmeasured locally.
- Current policies are simulation artifacts. They must not command a physical
  robot directly.
- Isaac Lab is installed locally, but no Isaac Lab task or performance result is
  reported by this repository yet.
- A laptop RTX 5070 with 8 GB VRAM constrains batch size, parallel environments
  and model choice. Results must document the actual configuration used.
- The reach task is not grasping, navigation, collision-free planning or a
  general manipulation benchmark.
