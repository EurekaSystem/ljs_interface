# LJS Skill Demo

This demo runs the **LJS scanning skill** using Docker, ROS2, and a Keyence LJ-X scanner.

The skill acquires a scan from the configured scanner and generates two output files:

* `Face_<face_id>.tif`
* `Face_<face_id>_luminance.tif`

Both files are saved inside the destination folder:

```text
/opt/scans/<scan_id>/
```

## Input structure

To run the skill test, you must enable the client script by modifying `src/ljs/setup.py`, adding the following line in the `entry_points` section:

```python
'cli = ' + NAME + '.ljs_client:main'
```

Example:

```python
entry_points={
    'console_scripts': [
        'cli = ' + NAME + '.ljs_client:main'
    ],
}
```

## Build Docker image

From the project root:

```bash
docker build -t <docker_name> .
```

## Run the skill server

Start the container with the scans directory mounted:

```bash
docker run -v /opt/scans:/opt/scans <docker_name> ros2 launch ljs_skill ljs.launch.py
```

## Run the skill test client

In a second terminal, run the client:

```bash
docker run -v /opt/scans:/opt/scans <docker_name> ros2 run ljs cli
```

## Demo parameters

Required parameters:

| Parameter | Type   | Description                      |
| --------- | ------ | -------------------------------- |
| scan_id   | string | Identifier of the scanned object |
| face_id   | int8   | Identifier of the object side    |

Example:

```text
1 = front
2 = back
3 = left
4 = right
```

## Scan_id and face_id configuration

The client uses a `scan_id` and a `face_id` to identify the object and the side to be scanned.

Example in the client code:

```python
goal_msg.scan_id = "10"
goal_msg.face_id = 1
```

This means the generated files will be stored in:

```text
/opt/scans/10/
```

and will correspond to face `1` of the scanned object.

## Expected output

After successful execution, the following files will be generated inside:

```text
/opt/scans/<scan_id>/
```

Output files:

```text
Face_<face_id>.tif
Face_<face_id>_luminance.tif
```

Example:

```text
/opt/scans/10/

├── Face_1.tif
└── Face_1_luminance.tif
```

## Important notes

* The scanner IP address must be configured correctly.
* The scanner must be connected and reachable from the container.
* The `scan_id` and `face_id` values must be valid.
* If you change `scan_id` or `face_id`, you must update the client accordingly.
