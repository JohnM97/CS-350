#
# Thermostat - This is the Python code used to demonstrate
# the functionality of the thermostat that we have prototyped throughout
# the course. 
#
# This code works with the test circuit that was built for module 7.
#
# Functionality:
#
# The thermostat has three states: off, heat, cool
#
# The lights will represent the state that the thermostat is in.
#
# If the thermostat is set to off, the lights will both be off.
#
# If the thermostat is set to heat, the Red LED will be fading in 
# and out if the current temperature is blow the set temperature;
# otherwise, the Red LED will be on solid.
#
# If the thermostat is set to cool, the Blue LED will be fading in 
# and out if the current temperature is above the set temperature;
# otherwise, the Blue LED will be on solid.
#
# One button will cycle through the three states of the thermostat.
#
# One button will raise the setpoint by a degree.
#
# One button will lower the setpoint by a degree.
#
# The LCD display will display the date and time on one line and
# alternate the second line between the current temperature and 
# the state of the thermostat along with its set temperature.
#
# The Thermostat will send a status update to the TemperatureServer
# over the serial port every 30 seconds in a comma delimited string
# including the state of the thermostat, the current temperature
# in degrees Fahrenheit, and the setpoint of the thermostat.
#
#------------------------------------------------------------------
# Change History
#------------------------------------------------------------------
# Version   |   Description
#------------------------------------------------------------------
#    1          Initial Development
#------------------------------------------------------------------

from time import sleep
from datetime import datetime
from statemachine import StateMachine, State
import board
import adafruit_ahtx0
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
import serial
from gpiozero import Button, PWMLED
from threading import Thread
from math import floor

DEBUG = True

# Set up I2C connection to the AHT20 temperature/humidity sensor
i2c = board.I2C()
thSensor = adafruit_ahtx0.AHTx0(i2c)

# Configure the UART serial port for status updates
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Configure GPIO pins for LEDs (PWM-enabled)
redLight = PWMLED(18)
blueLight = PWMLED(23)

class ManagedDisplay():
    # Handles the 16x2 LCD initialization and update logic
    def __init__(self):
        self.lcd_rs = digitalio.DigitalInOut(board.D17)
        self.lcd_en = digitalio.DigitalInOut(board.D27)
        self.lcd_d4 = digitalio.DigitalInOut(board.D5)
        self.lcd_d5 = digitalio.DigitalInOut(board.D6)
        self.lcd_d6 = digitalio.DigitalInOut(board.D13)
        self.lcd_d7 = digitalio.DigitalInOut(board.D26)
        self.lcd_columns = 16
        self.lcd_rows = 2
        self.lcd = characterlcd.Character_LCD_Mono(self.lcd_rs, self.lcd_en,
                    self.lcd_d4, self.lcd_d5, self.lcd_d6, self.lcd_d7,
                    self.lcd_columns, self.lcd_rows)
        self.lcd.clear()

    def cleanupDisplay(self):
        self.lcd.clear()
        self.lcd_rs.deinit()
        self.lcd_en.deinit()
        self.lcd_d4.deinit()
        self.lcd_d5.deinit()
        self.lcd_d6.deinit()
        self.lcd_d7.deinit()

    def clear(self):
        self.lcd.clear()

    def updateScreen(self, message):
        self.lcd.clear()
        self.lcd.message = message

screen = ManagedDisplay()

# [ ... All your initial comments and imports remain unchanged ... ]

class TemperatureMachine(StateMachine):
    "A state machine designed to manage our thermostat"

    off = State(initial = True)
    heat = State()
    cool = State()
    setPoint = 72

    cycle = (
        off.to(heat) |
        heat.to(cool) |
        cool.to(off)
    )

    def on_enter_heat(self):
        # Set LED behavior when entering heat state
        self.updateLights()
        if(DEBUG):
            print("* Changing state to heat")

    def on_exit_heat(self):
        # Turn off red LED when exiting heat state
        redLight.off()

    def on_enter_cool(self):
        # Set LED behavior when entering cool state
        self.updateLights()
        if(DEBUG):
            print("* Changing state to cool")
    
    def on_exit_cool(self):
        # Turn off blue LED when exiting cool state
        blueLight.off()

    def on_enter_off(self):
        # Turn off both LEDs when entering off state
        redLight.off()
        blueLight.off()
        if(DEBUG):
            print("* Changing state to off")
    
    def processTempStateButton(self):
        if(DEBUG):
            print("Cycling Temperature State")
        self.cycle()

    def processTempIncButton(self):
        if(DEBUG):
            print("Increasing Set Point")
        self.setPoint += 1
        self.updateLights()
        # Show temporary message with new set point
        self._overrideDisplay(f"Target: {self.setPoint}F")

    def processTempDecButton(self):
        if(DEBUG):
            print("Decreasing Set Point")
        self.setPoint -= 1
        self.updateLights()
        # Show temporary message with new set point
        self._overrideDisplay(f"Target: {self.setPoint}F")

    def updateLights(self):
        temp = floor(self.getFahrenheit())
        redLight.off()
        blueLight.off()
    
        if(DEBUG):
            print(f"State: {self.current_state.id}")
            print(f"SetPoint: {self.setPoint}")
            print(f"Temp: {temp}")

        # Manage LED status based on current state and temp vs setPoint
        if self.current_state.id == 'heat':
            if temp < self.setPoint:
                redLight.pulse()
                blueLight.off()
            else:
                redLight.value = 1.0
                blueLight.off()
        elif self.current_state.id == 'cool':
            if temp > self.setPoint:
                blueLight.pulse()
                redLight.off()
            else:
                blueLight.value = 1.0
                redLight.off()
        else:
            redLight.off()
            blueLight.off()

    def run(self):
        myThread = Thread(target=self.manageMyDisplay)
        myThread.start()

    def getFahrenheit(self):
        t = thSensor.temperature
        return (((9/5) * t) + 32)
    
    def setupSerialOutput(self):
        output = f"{self.current_state.id},{floor(self.getFahrenheit())},{self.setPoint}"
        return output

    ##
    ## _overrideDisplay - Temporarily override LCD line 2 to show target temp
    ##
    def _overrideDisplay(self, override_text):
        current_time = datetime.now()
        lcd_line_1 = current_time.strftime("%m/%d %H:%M") + "\n"
        lcd_line_2 = override_text
        screen.updateScreen(lcd_line_1 + lcd_line_2)
        sleep(3)

    endDisplay = False

    def manageMyDisplay(self):
        counter = 1
        altCounter = 1
        while not self.endDisplay:
            if(DEBUG):
                print("Processing Display Info...")
    
            current_time = datetime.now()
            lcd_line_1 = current_time.strftime("%m/%d %H:%M") + "\n"

            if(altCounter < 6):
                lcd_line_2 = f"Temp: {floor(self.getFahrenheit())}F"
                altCounter += 1
            else:
                lcd_line_2 = f"{self.current_state.id.capitalize()} {self.setPoint}F"
                altCounter += 1
                if(altCounter >= 11):
                    self.updateLights()
                    altCounter = 1
    
            screen.updateScreen(lcd_line_1 + lcd_line_2)
    
            if(DEBUG):
                print(f"Counter: {counter}")
            if((counter % 30) == 0):
                ser.write((self.setupSerialOutput() + "\n").encode())
                counter = 1
            else:
                counter += 1
            sleep(1)

        screen.cleanupDisplay()

# Button setup remains unchanged
tsm = TemperatureMachine()
tsm.run()

greenButton = Button(24)
greenButton.when_pressed = tsm.processTempStateButton

redButton = Button(25)
redButton.when_pressed = tsm.processTempIncButton

blueButton = Button(12)
blueButton.when_pressed = tsm.processTempDecButton

repeat = True

while repeat:
    try:
        sleep(30)
    except KeyboardInterrupt:
        print("Cleaning up. Exiting...")
        repeat = False
        tsm.endDisplay = True
        sleep(1)
