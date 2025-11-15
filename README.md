# J Tech Matrix Raw Integration for Home Assistant

A lightweight, reliable Home Assistant integration for controlling **J Tech HDMI matrix switches** using raw TCP commands over port 5000.

Some J Tech matrix models **do not implement the JSON or HTTP API** used by the official integration and instead only respond to telnet-style ASCII commands. This integration is built specifically for those models.

---

## Why This Integration Exists

The official J Tech integration by AlexOwl:

[https://github.com/AlexOwl/jtechdigital-ha](https://github.com/AlexOwl/jtechdigital-ha)

uses the `pyjtechdigital` library and expects a functional JSON login API.
However, many matrix units:

* Return `None` or malformed JSON
* Produce HTTP 500 responses
* Accept connections on port 5000 only
* Respond only to raw ASCII commands such as:

  ```txt
  #video_d out5 source=5
  ```

Since these commands **do** work through PuTTY, netcat, or telnet, this integration replaces the entire API layer with a direct TCP interface.

---

## How This Integration Works

* Connects to the matrix using a **persistent TCP connection**
* Sends commands in the device’s native telnet-style protocol
* Automatically reconnects if the matrix drops the connection
* Creates one entity per output in Home Assistant
* Selecting a source sends the routing command instantly
* Assumes **zero-based** input and output indexing:

  * Output 1 → `out0`
  * Input 1 → `source=0`

---

## Command Format Sent

Routing a single output:

```txt
#video_d out{output_zero_based} source={input_zero_based}
```

Example for Output 1 → Input 1:

```txt
#video_d out0 source=0
```

Routing an input to all outputs:

```txt
#video_d out255 source={input_zero_based}
```

These commands match exactly what the J Tech firmware expects.

---

## Installation

1. Copy the folder:

```
custom_components/jtech_raw_matrix
```

into your Home Assistant configuration directory.

2. Restart Home Assistant.

3. Go to:

**Settings → Devices and Services → Add Integration → J Tech Raw Matrix**

4. Enter your matrix’s IP or hostname (for example: `jtech.matrix`) and port (usually **5000**).

---

## Usage

Each matrix output will appear as a media player entity.
Choosing a source triggers the raw routing command immediately.

---

## Troubleshooting

* Only one controller can connect at a time

  * Close PuTTY or telnet before testing in Home Assistant
* If commands stop working intermittently, the matrix likely dropped the connection

  * The integration will reconnect automatically
* Use debug logs if needed:

```yaml
logger:
  logs:
    custom_components.jtech_raw_matrix: debug
```

---

## Credits

Built using the structure of the original J Tech integration by **AlexOwl**, but rewritten to support matrix units that rely on raw TCP control instead of the JSON API.

---
