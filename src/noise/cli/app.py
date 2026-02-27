import pyaudio
import numpy as np
import math
import sys
import time

# --- Configuration ---
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
BAR_WIDTH = 50
THRESHOLD = 85  # Default "Loud" level

# ANSI Colors for the terminal
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def get_color(db):
    if db < 60:
        return GREEN
    elif db < THRESHOLD:
        return YELLOW
    return RED

def draw_terminal_gauge(db):
    """Creates a visual ASCII bar based on dB level."""
    # Map 0-100 dB to the bar width
    filled_length = int(BAR_WIDTH * min(db, 100) / 100)
    bar = "█" * filled_length + "-" * (BAR_WIDTH - filled_length)
    
    color = get_color(db)
    alert = f" {BOLD}!! LOUD !!{RESET}" if db >= THRESHOLD else "          "
    
    # \r returns the cursor to the start of the line
    sys.stdout.write(f"\r{color}[{bar}] {db:>5.1f} dB{RESET}{alert}")
    sys.stdout.flush()

def meter():
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)
        
        print(f"{BOLD}Noise Monitor Started{RESET}")
        print(f"Threshold set to: {RED}{THRESHOLD} dB{RESET}")
        print("Press Ctrl+C to stop.\n")

        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)
            
            # RMS Calculation
            rms = np.sqrt(np.mean(samples.astype(float)**2))
            
            if rms > 0:
                # Digital decibel calculation
                db = 20 * math.log10(rms)
            else:
                db = 0
                
            draw_terminal_gauge(db)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Monitoring stopped by user.{RESET}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()