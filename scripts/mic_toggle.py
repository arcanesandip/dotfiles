#!/usr/bin/env python3
import subprocess

def toggle_mic():
    # Check current mute state using wpctl (PipeWire standard)
    res = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"], capture_output=True, text=True, check=False)
    is_muted = "[MUTED]" in res.stdout

    if is_muted:
        # Unmute audio and turn off mic-mute LED
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "0"], check=False)
        subprocess.run(["brightnessctl", "-d", "platform::micmute", "set", "0", "-q"], check=False)
    else:
        # Mute audio and turn on mic-mute LED
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "1"], check=False)
        subprocess.run(["brightnessctl", "-d", "platform::micmute", "set", "1", "-q"], check=False)

if __name__ == "__main__":
    toggle_mic()
