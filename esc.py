import RPi.GPIO as GPIO
import time

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set the GPIO pin for the ESC signal
esc_pin = 5

# Set the ESC signal pin as an output
GPIO.setup(esc_pin, GPIO.OUT)

# Create a PWM instance with a frequency of 50Hz (standard for ESC)
pwm = GPIO.PWM(esc_pin, 50)
pwm.start(0)

try:
    while True:
        val = float(input("Enter duty cycle value (0-100): "))
        pwm.ChangeDutyCycle(val)

except KeyboardInterrupt:
    pass

finally:
    # Cleanup GPIO settings
    pwm.stop()
    GPIO.cleanup()
