#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: Chevaughn H, Declan L, Jake C
#################################

from bomb_configs import *
from bomb_phases import *

###########
# functions
###########

def bootup(n=0):
    gui._lscroll["text"] = boot_text.replace("\x00", "")
    gui.setup()

    if RPi:
        setup_phases()
        check_phases()


def setup_phases():
    global timer, keypad, wires, button, toggles

    # timer
    timer = Timer(component_7seg, COUNTDOWN)
    gui.setTimer(timer)

    # keypad
    keypad = Keypad(component_keypad, keypad_target)

    # wires
    wires = Wires(component_wires, wires_target)

    # button
    button = Button(component_button_state, component_button_RGB,
                    button_target, button_color, timer)
    gui.setButton(button)

    # toggles
    toggles = Toggles(component_toggles, toggles_target)

    # start all threads
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()


def check_phases():
    global active_phases

    # TIMER
    if timer._running:
        gui._ltimer["text"] = f"Time left: {timer}"
    else:
        # time expired → explode
        turn_off()
        gui.after(100, gui.conclusion, False)
        return

    # KEYPAD
    if keypad._running:
        gui._lkeypad["text"] = f"Combination: {keypad}"
        if keypad._defused:
            keypad._running = False
            active_phases -= 1
        elif keypad._failed:
            strike()
            keypad._failed = False
            keypad._value = ""

    # WIRES
    if wires._running:
        gui._lwires["text"] = f"Wires: {wires}"
        if wires._defused:
            wires._running = False
            active_phases -= 1
        elif wires._failed:
            strike()
            wires._failed = False

    # BUTTON
    if button._running:
        gui._lbutton["text"] = f"Button: {button}"
        if button._defused:
            button._running = False
            active_phases -= 1
        elif button._failed:
            strike()
            button._failed = False

    # TOGGLES
    if toggles._running:
        gui._ltoggles["text"] = f"Toggles: {toggles}"
        if toggles._defused:
            toggles._running = False
            active_phases -= 1
        elif toggles._failed:
            strike()
            toggles._failed = False

    # strikes on GUI
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"

    # too many strikes → explode
    if strikes_left == 0:
        turn_off()
        gui.after(1000, gui.conclusion, False)
        return

    # all phases defused → success
    if active_phases == 0:
        turn_off()
        gui.after(100, gui.conclusion, True)
        return

    # check again after delay
    gui.after(100, check_phases)


def strike():
    global strikes_left
    strikes_left -= 1

    # speed up the timer by removing 15 seconds from the live value
    timer._value = max(0, timer._value - 15)


def turn_off():
    # stop all threads
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False    # safe even if already defused
    toggles._running = False

    # only touch hardware if on Pi
    if RPi:
        component_7seg.blink_rate = 0
        component_7seg.fill(0)
        for pin in button._rgb:
            pin.value = True


######
# MAIN
######

window = Tk()
gui = Lcd(window)

# must match the number of phases you decrement in check_phases (4 here)
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES  

gui.after(100, bootup)
window.mainloop()
