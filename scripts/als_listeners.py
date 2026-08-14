#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ALS Daemon: Continuous curve interpolation, hysteresis, and manual override."""

import subprocess
import sys
import os
import time
import threading
import argparse
import logging
import shutil
import signal

POLL_INTERVAL = 0.5         # Seconds between sensor checks
EMA_ALPHA = 0.3             # Lux smoothing factor (0 < alpha <= 1)
STEP_SIZE = 1.0             # Percentage change per transition step
STEP_INTERVAL = 0.03        # Seconds between transition steps
OVERRIDE_DRIFT = 0.4        # Fractional lux shift required to break manual override pause
MIN_CHANGE_THRESHOLD = 3.0  # Minimum % difference required to trigger an automated shift

# Calibrated continuous curve (Lux -> Screen Brightness %)
# Tailored for low-range IIO sensors (~3.5 lux indoor baseline maps to ~35%)
LUX_CURVE = [
    (0.0,   10.0),
    (3.5,   35.0),
    (15.0,  60.0),
    (50.0,  85.0),
    (200.0, 100.0)
]

latest_lux = None
lux_lock = threading.Lock()
shutdown_event = threading.Event()


def setup_logging(debug_mode):
    level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        level=level,
        stream=sys.stderr
    )


def get_system_brightness():
    """Query current brightness via brightnessctl CSV output."""
    try:
        res = subprocess.run(["brightnessctl", "-m"], capture_output=True, text=True, check=True)
        parts = res.stdout.strip().split(",")
        if len(parts) >= 4:
            return float(parts[3].strip().rstrip("%"))
    except Exception as e:
        logging.debug(f"Failed to fetch system brightness: {e}")
    return 50.0


def apply_brightness(value):
    subprocess.run(["brightnessctl", "set", f"{round(value, 1)}%", "-q"], check=False)


def interpolate_brightness(lux):
    """Calculate continuous brightness percentage using piecewise linear interpolation."""
    if lux <= LUX_CURVE[0][0]:
        return LUX_CURVE[0][1]
    if lux >= LUX_CURVE[-1][0]:
        return LUX_CURVE[-1][1]

    for i in range(len(LUX_CURVE) - 1):
        x0, y0 = LUX_CURVE[i]
        x1, y1 = LUX_CURVE[i + 1]
        if x0 <= lux <= x1:
            return y0 + (lux - x0) * (y1 - y0) / (x1 - x0)
            
    return 50.0


def control_loop():
    global latest_lux
    current_brightness = get_system_brightness()
    last_commanded_brightness = current_brightness
    smoothed_lux = None

    manual_override = False
    lux_at_override = None

    logging.info(f"Pro ALS Daemon started. Initial brightness: {current_brightness:.1f}%")

    while not shutdown_event.is_set():
        time.sleep(POLL_INTERVAL)

        with lux_lock:
            raw_lux = latest_lux

        if raw_lux is None:
            continue

        # 1. Smooth sensor input
        if smoothed_lux is None:
            smoothed_lux = raw_lux
        else:
            smoothed_lux = (EMA_ALPHA * raw_lux) + ((1.0 - EMA_ALPHA) * smoothed_lux)

        # 2. Check for manual user override
        actual_now = get_system_brightness()
        if abs(actual_now - last_commanded_brightness) > 1.5:
            if not manual_override:
                manual_override = True
                lux_at_override = smoothed_lux
                logging.info(f"Manual override detected ({actual_now}%). Pausing auto-brightness.")

        # If overridden, check if ambient lighting has shifted enough to resume control
        if manual_override:
            if lux_at_override and abs(smoothed_lux - lux_at_override) > (lux_at_override * OVERRIDE_DRIFT):
                manual_override = False
                logging.info("Ambient light shifted significantly. Resuming auto-brightness control.")
            else:
                continue

        # 3. Calculate continuous target
        desired_target = interpolate_brightness(smoothed_lux)

        # 4. Magnitude Hysteresis Check (Skip tiny fluctuations)
        if abs(desired_target - current_brightness) < MIN_CHANGE_THRESHOLD:
            continue

        logging.info(f"Lighting shift detected (Lux: {smoothed_lux:.1f}). Transitioning: {current_brightness:.1f}% -> {desired_target:.1f}%")

        # 5. Smooth Transition Execution
        while not shutdown_event.is_set():
            current_brightness = get_system_brightness()
            diff = desired_target - current_brightness

            if abs(diff) < STEP_SIZE:
                current_brightness = desired_target
                apply_brightness(current_brightness)
                last_commanded_brightness = current_brightness
                logging.info(f"Transition complete. Settled at {current_brightness:.1f}%.")
                break
            else:
                current_brightness += STEP_SIZE if diff > 0 else -STEP_SIZE
                apply_brightness(current_brightness)
                last_commanded_brightness = current_brightness
                time.sleep(STEP_INTERVAL)


def control_loop_supervisor():
    while not shutdown_event.is_set():
        try:
            control_loop()
        except Exception as e:
            logging.error(f"Control loop crashed: {e}. Restarting in 2 seconds...")
            time.sleep(2.0)
        else:
            break


def sensor_watchdog():
    global latest_lux
    while not shutdown_event.is_set():
        logging.info("Spawning monitor-sensor stream...")
        process = None
        try:
            process = subprocess.Popen(
                ["monitor-sensor"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1
            )

            if process.stdout is None:
                raise RuntimeError("monitor-sensor produced no stdout pipe")

            for line in process.stdout:
                if shutdown_event.is_set():
                    break
                if "Light changed:" in line:
                    try:
                        lux_str = line.split("Light changed:")[1].split("(")[0].strip()
                        lux_val = float(lux_str)
                        with lux_lock:
                            latest_lux = lux_val
                    except (IndexError, ValueError):
                        continue

            process.wait(timeout=5)
        except Exception as e:
            logging.error(f"Sensor watchdog error: {e}")
        finally:
            if process is not None and process.poll() is None:
                process.terminate()

        if shutdown_event.is_set():
            break

        logging.warning("monitor-sensor stream disconnected. Restarting in 3 seconds...")
        time.sleep(3.0)


def handle_shutdown_signal(signum, frame):
    logging.info(f"Received signal {signum}. Shutting down gracefully...")
    shutdown_event.set()


def main():
    parser = argparse.ArgumentParser(description="Production-Grade ALS Backlight Daemon")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()

    setup_logging(args.debug)

    if not shutil.which("monitor-sensor") or not shutil.which("brightnessctl"):
        logging.error("Required dependencies ('monitor-sensor' or 'brightnessctl') missing from PATH.")
        sys.exit(1)

    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)

    worker = threading.Thread(target=control_loop_supervisor, daemon=True)
    worker.start()

    try:
        sensor_watchdog()
    except KeyboardInterrupt:
        shutdown_event.set()

    logging.info("ALS Daemon terminated.")
    sys.exit(0)


if __name__ == "__main__":
    main()
