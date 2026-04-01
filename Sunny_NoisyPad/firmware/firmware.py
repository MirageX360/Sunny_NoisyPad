# Hamza's NoisyPad
# "Make some noise for Noisy Boy!!"" /ref (real steel)
# For Blueprint MacroPad Project
# Using KMK
# Features: 12 keys, OLED display with volume and time

import board
import time
import busio
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.modules.media_keys import MediaKeys
from kmk.modules.encoder import EncoderHandler
from kmk.scanners import DiodeOrientation
from kmk.extensions.display import Display, TextDisplay, SSD1306

keyboard = KMKKeyboard()
keyboard.modules.append(MediaKeys())

# Matris Pins for my 4x3 design (12 keys total)
keyboard.col_pins = (board.GP0, board.GP1, board.GP2, board.GP3) # creates 4 columns
keyboard.row_pins = (board.GP4, board.GP5, board.GP6,) # creates 3 rows
# This changes diode orientation if they are reversed
keyboard.diode_orientation = DiodeOrientation.COL2ROW 

# Controlling volume using the rotary encoder
encoder_handler = EncoderHandler()
keyboard.modules.append(encoder_handler)
encoder_handler.pins = ((board.GP7, board.GP8, False))
# Actions: (Left and right rotation for increase/decrease in vol)
encoder_handler.map = [((KC.VOLD, KC.VOLU),)]

# OLED Display (using the 0.91 inch SSD1306)
i2c = busio.I2C(scl=board.GP9, sda=board.GP10)
display = Display(
    display=SSD1306(i2c=i2c, device_address=0x3C, width=128, height=32),
    # The OLED displays a startup message, volume bar, and time
    entries=[
        TextDisplay(text="Hamza Wali", x=0, y=0, show=True),
        TextDisplay(text="", x=0, y=12, show=True),
        TextDisplay(text="", x=0, y=24, show=True),
    ])
keyboard.extensions.append(display)

# Function for OLED: Change Volume
def change_volume(vol_percent):
    # Showing the volume bar using blocks
    blocks = int(vol_percent / 10)
    bar = "■" * blocks + "□" * (10 - blocks)
    display.entries[1].text = f"VOL: [{bar}] {vol_percent}%"
    display.entries[1].show = True

# Function for OLED: Show Time
def show_time():
    t = time.localtime()
    # Convert timezone to CST (UTC-6)
    hour_cst = (t.tm_hour - 6) % 24
    display.entries[2].text = f"{hour_cst:02d}:{t.tm_min:02d}"
    display.entries[2].show = True

# Keymap layout:
# - Save, Copy, Paste, BrightnessUp]
# - Delete, Win+4, Lock, BrightnessDown]
# - Undo, Redo, Mute/Unmute, Enter]
keyboard.keymap = [
    [
        KC.LCTL(KC.S), KC.LCTL(KC.C), KC.LCTL(KC.V), KC.BRIGHTNESS_UP,
        KC.DELETE,     KC.LGUI(KC.N4),KC.LGUI(KC.L), KC.BRIGHTNESS_DOWN,
        KC.LCTL(KC.Z), KC.LCTL(KC.Y), KC.MUTE,       KC.ENTER
    ]]

# Encoder Callback for OLED
current_volume = 50  # Tracking the volume (with placeholder at 50%)
change_volume(current_volume) # Show current volume on OLED
def oled_encoder_callback(encoder, direction):
    global current_volume
    if direction == -1:
        current_volume = max(0, current_volume - 5) # Volume decrease
        keyboard.modules[0].volume_down()
    elif direction == 1:
        current_volume = min(100, current_volume + 5) # Volume Increase
        keyboard.modules[0].volume_up()
    
    # Change the volume bar on the OLED to show updated volume
    change_volume(current_volume)

encoder_handler.on_turn = oled_encoder_callback

# Continously displaying the time
def main_loop():
    show_time()
    time.sleep(1)
keyboard.on_main_loop = main_loop

# Starting the keyboard!
if __name__ == '__main__':
    keyboard.go()