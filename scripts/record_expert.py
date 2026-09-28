"""Generate scripted reach demonstrations using differential IK in MuJoCo."""

from __future__ import annotations

import argparse
from pathlib import Path

import mujoco
import numpy as np

from xlerobot_twin import XLeRobotReachEnv
from xlerobot_twin.env import ARM_ACTUATORS

RIGHT_JOINTS = ("Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R")
LEFT_JOINTS = ("Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L")


def expert_action(env: XLeRobotReachEnv) -> np.ndarray:
    """Return a normalized action from a damped least-squares IK controller."""
    action = np.zeros(env.action_space.shape, dtype=np.float32)
    cube = env.data.xpos[env.model.body("target_cube").id]
    use_right = bool(cube[1] >= env.data.qpos[1])
    ee_site = env.right_ee if use_right else env.left_ee
    joint_names = RIGHT_JOINTS if use_right else LEFT_JOINTS
    ee = env.data.site_xpos[ee_site]
    error = cube - ee

    # Move the base into the arm workspace first. Yaw correction points the robot
    # toward the target and remains deliberately conservative.
    base_position = env.data.qpos[:3]
    heading = 2.0 * np.arctan2(env.data.qpos[6], env.data.qpos[3])
    target_heading = np.arctan2(cube[1] - base_position[1], cube[0] - base_position[0])
    heading_error = np.arctan2(np.sin(target_heading - heading), np.cos(target_heading - heading))
    action[1] = np.clip(2.0 * heading_error, -0.6, 0.6)
    if env.base_enabled and np.linalg.norm(error[:2]) > 0.16:
        action[0] = 0.8

    jacp = np.zeros((3, env.model.nv))
    jacr = np.zeros((3, env.model.nv))
    mujoco.mj_jacSite(env.model, env.data, jacp, jacr, ee_site)
    dofs = [int(env.model.jnt_dofadr[env.model.joint(name).id]) for name in joint_names]
    jacobian = jacp[:, dofs]
    damping = 1e-3
    delta = jacobian.T @ np.linalg.solve(jacobian @ jacobian.T + damping * np.eye(3), error)

    for name, change in zip(joint_names, delta):
        action_index = 2 + ARM_ACTUATORS.index(name)
        action[action_index] = np.clip(2.0 * change / 0.025, -1.0, 1.0)
    return action


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("datasets/expert/reach"))
    parser.add_argument("--seed", type=int, default=100)
    parser.add_argument("--max-attempts", type=int, help="Defaults to ten attempts per requested episode")
    parser.add_argument("--images", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    successes = 0
    attempts = 0
    max_attempts = args.max_attempts or args.episodes * 10
    env = XLeRobotReachEnv(render_mode="rgb_array" if args.images else None, domain_randomization=True)
    while successes < args.episodes and attempts < max_attempts:
        observation, _ = env.reset(seed=args.seed + attempts)
        observations, actions, rewards, images = [], [], [], []
        terminated = truncated = False
        info = {}
        while not (terminated or truncated):
            action = expert_action(env)
            observations.append(observation)
            actions.append(action)
            if args.images:
                images.append(env.render())
            observation, reward, terminated, truncated, info = env.step(action)
            rewards.append(reward)
        payload = {
            "observation": np.asarray(observations, dtype=np.float32),
            "action": np.asarray(actions, dtype=np.float32),
            "reward": np.asarray(rewards, dtype=np.float32),
            "task": np.asarray("Reach the cube with either gripper"),
            "success": np.asarray(bool(info.get("success", False))),
        }
        success = bool(info.get("success", False))
        attempts += 1
        if success:
            if args.images:
                payload["neck_rgb"] = np.asarray(images, dtype=np.uint8)
            np.savez_compressed(args.output / f"episode_{successes:05d}.npz", **payload)
            successes += 1
        print(f"attempt={attempts} steps={len(rewards)} success={success} saved={successes}")
    env.close()
    rate = successes / attempts if attempts else 0.0
    print(f"saved={args.output} episodes={successes} attempts={attempts} controller_success_rate={rate:.1%}")
    if successes != args.episodes:
        raise SystemExit(f"Only generated {successes}/{args.episodes} successful demonstrations.")


if __name__ == "__main__":
    main()
