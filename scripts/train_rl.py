"""Train PPO on the reach task; requires requirements-rl.txt."""
from pathlib import Path
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from xlerobot_twin import XLeRobotReachEnv

env = make_vec_env(XLeRobotReachEnv, n_envs=1, seed=42)
model = PPO("MlpPolicy", env, verbose=1, n_steps=1024, batch_size=64, tensorboard_log="outputs/tensorboard")
model.learn(total_timesteps=100_000)
Path("outputs/models").mkdir(parents=True, exist_ok=True)
model.save("outputs/models/ppo_reach")
