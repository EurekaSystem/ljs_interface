# LJS SKILL

## Overview

The `ljs package` implements a ROS 2 lifecycle-based skill for interfacing with an external LJS scanning device. It provides a structured interface to a Keyence scanner, handling its initialization, activation, scanning, and shutdown through the ROS 2 lifecycle state machine.
For each scan, the skill produces two output files: one containing depth data, used to represent the 3D structure of the scanned scene, and one containing luminance data, which captures intensity information useful for visual inspection and analysis.

---

## Requirements

- ROS 2
- Python 3
- `colcon` build system

This skill requires a Keyence scanner and its IP address.

### Dependencies

All required ROS dependencies are declared in the `package.xml` files.  
External dependencies for the scanner device are located in the `ljs_lib` directory.

### Compatible hardware

This skill requires  one of the following Keyence scanners:
- LJ-X8020
- LJ-X8060
- LJ-X8080
- LJ-X8200
- LJ-X8300
- LJ-X8400
- LJ-X8900

---

## Build the Package

Source your ROS 2 environment and build the workspace:

```bash
source /opt/ros/<your_ros2_version>/setup.bash
cd <your_workspace>
colcon build
source install/setup.bash
```

---

## Run the Skill

```bash
ros2 launch ljs_skill ljs.launch.py
```

### Expected Output

```bash
Initialising...
Skill ljs started, but not yet configured.
Skill ljs is configured, but not yet active.
Skill ljs is active and running.
Skill ljs: performing background task...
```

---

## Architecture

- ROS 2 lifecycle node
- Action server: `ljs_scan`
- Hardware interface: `LJSDriver`

Main logic:

```bash
ljs_skill_impl.py
```

---

## Execution Requirements

### Input Parameters

The following parameters are part of the custom action interface `ljs_skill_msgs/action/Ljs`:

- **scan_id** (`string`)

  Uniquely identifies the object to be scanned.

- **face_id** (`int8`)

  Uniquely identifies the side of the object to be scanned.

  Example:
  - `1` = front
  - `2` = back
  - `3` = left
  - `4` = right

### Device

- `LJS device IP`

---

## Output Files

The `scan()` method generates the following files inside the destination folder:

```text
/opt/scans/<scan_id>/
├── Face_<face_id>.tif
└── Face_<face_id>_luminance.tif
```

- **Face_<face_id>.tif**: contains the geometric information of the 3D scan; each pixel represents the height or distance of the acquired point relative to a reference plane.

- **Face_<face_id>_luminance.tif**: contains the reflected light intensity information of the scanned surface; each pixel encodes the reflected light intensity of the acquired point.

---

## Testing the Skill

You can test the skill using a simple ROS 2 action client.

### Example Action Client

```python
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from ljs_skill_msgs.action import Ljs


class Act_cli(Node):

    def __init__(self):
        super().__init__('act_cli')
        self._action_client = ActionClient(self, Ljs, 'ljs_scan')

    def send_goal(self):
        goal_msg = Ljs.Goal()
        goal_msg.scan_id = "10"
        goal_msg.face_id = 1

        # Waiting server
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Server not ready!')
            return

        # Send goal
        self.get_logger().info('Goal sent')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, self._send_goal_future)
        self.goal_response_callback(self._send_goal_future)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result()
        result_msg = result.result
        t_result = result_msg.result

        self.get_logger().info(
            'Result: ' +
            str(t_result.error_code) +
            " --- " +
            t_result.error_msg
        )

        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    action_client = Act_cli()
    action_client.send_goal()

    rclpy.spin(action_client)


if __name__ == '__main__':
    main()
```

### Expected Output

```bash
Goal sent
Goal accepted
```

---

## Important Notes

- Action names must match between server and client.
- The device ID must be configured correctly.
- After modifying messages(`ljs_skill_msgs`), rebuild the workspace:

```bash
colcon build
source install/setup.bash
```

---

## Customization

### Modify Skill Logic

Edit:

```text
ljs_skill_impl.py
```

This file controls:

- Goal handling
- Execution logic
- Returned results

### Modify Action Interface

Edit the action definition:

```text
ljs_skill_msgs/action/Ljs.action
```

You can customize:

- Goal fields (input)
- Result fields (output)
- Feedback messages

### Change Action Name

If needed, update the action name:

- In the server (`ljs_skill_impl.py`)
- In the client (`ljs_scan` → your custom name)

---

## Common Failure Cases

- **Action server not available (`ljs_scan` missing)**
  - Node not launched correctly
  - Lifecycle node not transitioned to ACTIVE state
  - Runtime or build errors during startup

- **Goal rejected by the action server**
  - Invalid `scan_id` or `face_id`
  - Scanner is currently busy with another acquisition

- **No output files generated after scan**
  - Missing or incorrect output directory permissions
  - Scan execution interrupted or failed
  - Misconfigured destination path

- **ROS 2 action communication failure**
  - Mismatch between action names (server/client)
  - Workspace not sourced correctly
  - `ljs_skill_msgs` not rebuilt after modifications

---

This work has been supported by the project “Agile, human-centric, and Real-tIme enabled open SourcE technologies advancing industrial HRI in Europe” (ARISE), which received funding from the European Union’s Horizon Europe research and innovation program under grant agreement No. 101135784.