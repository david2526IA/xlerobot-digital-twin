from xlerobot_twin.teleop import (
    A, B, LB, RB, START, DPAD_RIGHT,
    GamepadState, TeleopController, shaped_axis,
)


def state(*, buttons=(), axes=(0, 0, 0, 0, -1, -1)):
    values = [0] * 15
    for button in buttons:
        values[button] = 1
    return GamepadState(tuple(values), tuple(axes))


def test_deadman_and_estop_are_safe():
    controller = TeleopController()
    assert controller.update(state(axes=(0, -1, 0, 0, -1, -1)), 0.02).forward == 0
    assert controller.update(state(buttons=(A,), axes=(0, -1, 0, 0, -1, -1)), 0.02).forward == 1
    assert controller.update(state(buttons=(A, B)), 0.02).estop
    assert controller.update(state(buttons=(A,)), 0.02).estop
    home = controller.update(state(buttons=(A, START)), 0.02)
    assert home.home and not home.estop


def test_arm_modes_cover_both_arms_and_grippers():
    controller = TeleopController()
    axes = (0.8, -0.7, 0.6, -0.5, -1.0, 1.0)
    command = controller.update(state(buttons=(A, LB, RB, DPAD_RIGHT), axes=axes), 0.02)
    assert command.mode == "left+right arm"
    assert set(command.joint_velocity) == {
        "Rotation_L", "Pitch_L", "Elbow_L", "Wrist_Pitch_L", "Wrist_Roll_L", "Jaw_L",
        "Rotation_R", "Pitch_R", "Elbow_R", "Wrist_Pitch_R", "Wrist_Roll_R", "Jaw_R",
    }
    assert command.joint_velocity["Jaw_L"] > 0
    assert command.joint_velocity["Wrist_Roll_R"] > 0


def test_deadzone_curve():
    assert shaped_axis(0.10) == 0
    assert 0 < shaped_axis(0.5) < 0.5
