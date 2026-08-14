#!/usr/bin/env python3
import os
import subprocess

DRIVER_DIR = "/sys/bus/usb/drivers/uvcvideo"
LED_NAME = "asus::camera"
INTERFACES = ["3-7:1.0", "3-7:1.1"]

def toggle_camera():
    unbind_path = os.path.join(DRIVER_DIR, "unbind")
    bind_path = os.path.join(DRIVER_DIR, "bind")
    
    # Check if the camera is currently active (bound to the driver)
    first_interface_path = os.path.join(DRIVER_DIR, INTERFACES[0])
    is_active = os.path.exists(first_interface_path)

    if is_active:
        # Cut connection (Hardware kill) & turn LED ON
        try:
            for iface in INTERFACES:
                if os.path.exists(os.path.join(DRIVER_DIR, iface)):
                    with open(unbind_path, "w") as f:
                        f.write(iface)
            subprocess.run(["brightnessctl", "-d", LED_NAME, "set", "1", "-q"], check=False)
            print("Camera disabled (LED ON).")
        except Exception as e:
            print(f"Error disabling camera: {e}")
    else:
        # Restore connection & turn LED OFF
        try:
            for iface in INTERFACES:
                bus_iface_path = os.path.join("/sys/bus/usb/devices", iface)
                if os.path.exists(bus_iface_path) and not os.path.exists(os.path.join(DRIVER_DIR, iface)):
                    with open(bind_path, "w") as f:
                        f.write(iface)
            subprocess.run(["brightnessctl", "-d", LED_NAME, "set", "0", "-q"], check=False)
            print("Camera enabled (LED OFF).")
        except Exception as e:
            print(f"Error enabling camera: {e}")

if __name__ == "__main__":
    toggle_camera()
