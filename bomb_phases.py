#################################
# CSC 102 Defuse the Bomb Project
# GUI and Phase class definitions
# Team: Chevaughn H, Declan L, Jake C
#################################

from bomb_configs import *
from tkinter import *
import tkinter
from threading import Thread
from time import sleep
import os
import sys

MORSE = {
    0: ".---",
    1: "..--",
    2: "-..-",
    3: "--.."
}

#########
# classes
#########

class Lcd(Frame):
    def __init__(self, window):
        super().__init__(window, bg="black")
        window.attributes("-fullscreen", True)
        self._timer = None
        self._button = None
        self.setupBoot()

    def setupBoot(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=1)
        self._lscroll = Label(self, bg="black", fg="white",
                              font=("Courier New", 14),
                              text="", justify=LEFT)
        self._lscroll.grid(row=0, column=0, columnspan=3, sticky=W)
        self.pack(fill=BOTH, expand=True)

    def setup(self):
        self._ltimer = Label(self, bg="black", fg="#00ff00",
                             font=("Courier New", 18),
                             text="Time left: ")
        self._ltimer.grid(row=1, column=0, columnspan=3, sticky=W)

        self._lkeypad = Label(self, bg="black", fg="#00ff00",
                              font=("Courier New", 18),
                              text="Keypad phase: ")
        self._lkeypad.grid(row=2, column=0, columnspan=3, sticky=W)

        self._lwires = Label(
            self,
            bg="black",
            fg=wires_target["fg"],
            font=("Courier New", 18, "bold"),
            text="WIRES"
        )
        self._lwires.grid(row=3, column=0, columnspan=3, sticky=W)

        self._lbutton = Label(self, bg="black", fg="#00ff00",
                              font=("Courier New", 18),
                              text="Button phase: ")
        self._lbutton.grid(row=4, column=0, columnspan=3, sticky=W)

        self._ltoggles = Label(self, bg="black", fg="#00ff00",
                               font=("Courier New", 18),
                               text="Toggles phase: ")
        self._ltoggles.grid(row=5, column=0, columnspan=2, sticky=W)

        self._lstrikes = Label(self, bg="black", fg="#00ff00",
                               font=("Courier New", 18),
                               text="Strikes left: ")
        self._lstrikes.grid(row=5, column=2, sticky=W)


        if (SHOW_BUTTONS):
            self._bpause = tkinter.Button(self, bg="red", fg="white",
                                          font=("Courier New", 18),
                                          text="Pause", anchor=CENTER,
                                          command=self.pause)
            self._bpause.grid(row=6, column=0, pady=40)

            self._bquit = tkinter.Button(self, bg="red", fg="white",
                                         font=("Courier New", 18),
                                         text="Quit", anchor=CENTER,
                                         command=self.quit)
            self._bquit.grid(row=6, column=2, pady=40)

    def setTimer(self, timer):
        self._timer = timer

    def setButton(self, button):
        self._button = button

    def pause(self):
        if (RPi):
            self._timer.pause()

    def conclusion(self, success=False):
        self._lscroll["text"] = ""
        self._ltimer.destroy()
        self._lkeypad.destroy()
        self._lwires.destroy()
        self._lbutton.destroy()
        self._ltoggles.destroy()
        self._lstrikes.destroy()
        if (SHOW_BUTTONS):
            self._bpause.destroy()
            self._bquit.destroy()

        self._bretry = tkinter.Button(self, bg="red", fg="white",
                                      font=("Courier New", 18),
                                      text="Retry", anchor=CENTER,
                                      command=self.retry)
        self._bretry.grid(row=1, column=0, pady=40)

        self._bquit = tkinter.Button(self, bg="red", fg="white",
                                     font=("Courier New", 18),
                                     text="Quit", anchor=CENTER,
                                     command=self.quit)
        self._bquit.grid(row=1, column=2, pady=40)

    def retry(self):
        os.execv(sys.executable, ["python3"] + [sys.argv[0]])
        exit(0)

    def quit(self):
        if (RPi):
            self._timer._running = False
            self._timer._component.blink_rate = 0
            self._timer._component.fill(0)
            for pin in self._button._rgb:
                pin.value = True
        exit(0)


class PhaseThread(Thread):
    def __init__(self, name, component=None, target=None):
        super().__init__(name=name, daemon=True)
        self._component = component
        self._target = target
        self._defused = False
        self._failed = False
        self._value = None
        self._running = False


class Timer(PhaseThread):
    def __init__(self, component, initial_value, name="Timer"):
        super().__init__(name, component)
        self._value = initial_value
        self._paused = False
        self._min = ""
        self._sec = ""
        self._interval = 1

    def run(self):
        self._running = True
        while (self._running):
            if (not self._paused):
                self._update()
                self._component.print(str(self))
                sleep(self._interval)
                if (self._value == 0):
                    self._running = False
                self._value -= 1
            else:
                sleep(0.1)

    def _update(self):
        self._min = f"{self._value // 60}".zfill(2)
        self._sec = f"{self._value % 60}".zfill(2)

    def pause(self):
        self._paused = not self._paused
        self._component.blink_rate = (2 if self._paused else 0)

    def __str__(self):
        return f"{self._min}:{self._sec}"


class Keypad(PhaseThread):
    def __init__(self, component, target, name="Keypad"):
        super().__init__(name, component, target)
        self._value = ""

    def run(self):
        self._running = True
        while (self._running):
            if (self._component.pressed_keys):
                while (self._component.pressed_keys):
                    try:
                        key = self._component.pressed_keys[0]
                    except:
                        key = ""
                    sleep(0.1)
                self._value += str(key)
                if (self._value == self._target):
                    self._defused = True
                elif (self._value != self._target[0:len(self._value)]):
                    self._failed = True
            sleep(0.1)

    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return self._value


class Wires(PhaseThread):
    def __init__(self, component, target, name="Wires"):
        super().__init__(name, component, target)

        self._color_name = target["color_name"]
        self._sequence = target["sequence"]

        self._value = []
        self._previous_states = []

    def run(self):
        self._running = True

        self._previous_states = [pin.value for pin in self._component]

        while (self._running):
            current_states = [pin.value for pin in self._component]

            for i in range(len(current_states)):
                if (self._previous_states[i] and not current_states[i]):
                    wire_number = i + 1
                    self._value.append(wire_number)

                    if (self._value != self._sequence[0:len(self._value)]):
                        self._failed = True
                        self._value = []

                    elif (self._value == self._sequence):
                        self._defused = True

            self._previous_states = current_states
            sleep(0.1)

    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return f"{self._color_name.upper()} wires: {self._value}"


class Button(PhaseThread):
    def __init__(self, component_state, component_rgb, target, color, timer, name="Button"):
        super().__init__(name, component_state, target)
        self._value = False
        self._pressed = False
        self._rgb = component_rgb
        self._color = color
        self._timer = timer

    def run(self):
        import bomb_configs
        self._running = True

        # set static LED color based on random choice
        self._rgb[0].value = False if self._color == "R" else True
        self._rgb[1].value = False if self._color == "G" else True
        self._rgb[2].value = False if self._color == "B" else True

        while (self._running):
            # read button state
            self._value = self._component.value

            # detect press → release
            if self._value:
                self._pressed = True
            else:
                if self._pressed:
                    # on release, confirm current toggle step
                    bomb_configs.toggle_progress += 1
                    self._pressed = False

            # Morse code signaling for current toggle
            step = bomb_configs.toggle_progress
            target_seq = bomb_configs.toggles_target

            if step >= len(target_seq):
                self._defused = True
                break

            current_toggle = target_seq[step]
            pattern = MORSE[current_toggle]

            for symbol in pattern:
                if symbol == ".":
                    # DOT = blue flash
                    self._rgb[0].value = True
                    self._rgb[1].value = True
                    self._rgb[2].value = False
                    sleep(0.3)
                elif symbol == "-":
                    # DASH = red flash
                    self._rgb[0].value = False
                    self._rgb[1].value = True
                    self._rgb[2].value = True
                    sleep(0.6)

                # off between signals
                self._rgb[0].value = True
                self._rgb[1].value = True
                self._rgb[2].value = True
                sleep(0.2)

            sleep(1)

    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return "Pressed" if self._value else "Released"


class Toggles(PhaseThread):
    def __init__(self, component, target, name="Toggles"):
        super().__init__(name, component, target)
        self._value = [False] * 4
        self._step = 0

    def run(self):
        import bomb_configs
        self._running = True

        while (self._running):
            self._value = [pin.value for pin in self._component]

            # Check if ANY switch that should NOT be on is currently ON
            wrong_switch_on = False
            for i, val in enumerate(self._value):
                if val and i != self._target[self._step]:
                    wrong_switch_on = True
                    break

            if wrong_switch_on:
                # Signal a strike and reset progress
                self._failed = True
                self._step = 0
                bomb_configs.toggle_progress = 0

                # Wait until ALL switches are back OFF before continuing
                while self._running:
                    self._value = [pin.value for pin in self._component]
                    if not any(self._value):
                        break
                    sleep(0.1)

            # Check if the correct switch for this step is ON
            elif self._value[self._target[self._step]]:
                sleep(0.2) 
                self._step += 1
                bomb_configs.toggle_progress = self._step

                if self._step >= len(self._target):
                    self._defused = True
                    break

                # Wait for that correct switch to be released before next step
                while self._running:
                    self._value = [pin.value for pin in self._component]
                    if not any(self._value):
                        break
                    sleep(0.1)

            sleep(0.1)

    def __str__(self):
        if (self._defused):
            return "DEFUSED"
        else:
            return f"Step {self._step}/4"
