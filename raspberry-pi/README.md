# SCIoT Hardware - Raspberry Pi

## Raspberry Pi Setup

**Model:** Raspberry Pi Model B+  
**OS:** Raspberry Pi OS Lite (32-bit)  
**Hostname:** `SCIOT`  
**Username:** `group29`  
**Password:** `SCIOT29-group`

### WiFi Connection (SSH)

**SSID:** `Redmi`  
**Password:** `eevvaann`

SSH into the Pi:
```bash
ssh group29@SCIOT.local
# or
ssh group29@<IP_ADDRESS>
```

## Project Structure

```
sciot_project/
├── main.py               # Main orchestrator
├── hardware/
│   ├── grove_inputs.py   # Grove sensors (DHT)
│   ├── grove_outputs.py  # Grove actuators (Buzzer)
│   └── pi_direct.py      # GPIO control (Fan, Servo, RGB LED, MQ-2)
```

## Running the System

```bash
# Run the main program
python3 main.py
```