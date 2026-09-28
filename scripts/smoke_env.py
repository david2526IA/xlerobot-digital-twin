"""Run a random episode and save one neck-camera image when rendering is available."""
from pathlib import Path
from xlerobot_twin import XLeRobotReachEnv

env = XLeRobotReachEnv(render_mode="rgb_array")
obs, info = env.reset(seed=7)
total = 0.0
for _ in range(25):
    obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
    total += reward
    if terminated or truncated:
        break
image = env.render()
if image is not None:
    from PIL import Image
    out = Path("outputs") / "neck_rgb_smoke.png"
    out.parent.mkdir(exist_ok=True)
    Image.fromarray(image).save(out)
    print(f"Saved {out}")
print(f"reward={total:.3f} info={info}")
env.close()
