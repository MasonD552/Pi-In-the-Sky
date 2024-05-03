# type: ignore
import board
import busio
import digitalio
import time
import storage

# Initialize the motor
motor_pin = board.GP13 # MOTOR PIN = GP13
motor = digitalio.DigitalInOut(motor_pin)
motor.direction = digitalio.Direction.OUTPUT

    while True:
        motor.value = True
        time.sleep(10)
        motor.value = False
        time.sleep(2)
        