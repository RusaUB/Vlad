"""
in1 = 31, in2 = 33 , in3 = 35, in4 = 37
en1 = 40, en2 = 38, en3 = 36, en4 = 32

                    #########################
                    #                       #
                    #                       #
    #################                       ################## 
    #               #                       #                #
    # EN3 (forward) #                       #  IN2 (forward) #
    # EN4 (back)    #                       #  IN1 (back)    #
    #               #                       #                #
    #################                       ################## 
                    #                       #
                    #                       #
                    #                       #
                    #                       #
    #################                       #################
    #               #                       #               #
    # EN1 (BACK)    #                       # IN3 (forward) #
    # EN2 (forward) #                       # IN4 (back)    #
    #               #                       #               #
    #################                       #################
                    #                       #
                    #                       # 
                    #########################
"""

import RPi.GPIO as GPIO
import time
import socket
import threading
import time

GPIO.setwarnings(False)

IN1 = 31
IN2 = 33 
IN3 = 35 
IN4 = 37

EN1 = 40 
EN2 = 38 
EN3 = 36 
EN4 = 32

servoPin = 8

right_top_wheel = { 'forward' : IN2, 'back' : IN1  }
right_bottom_wheel = { 'forward' : IN4, 'back' : IN3  }

left_top_wheel = { 'forward' : EN3, 'back' : EN4  }
left_bottom_wheel = { 'forward' : EN1, 'back' : EN2  }

GPIO.setmode(GPIO.BOARD)

GPIO.setup(IN1,GPIO.OUT)
GPIO.setup(IN2,GPIO.OUT)
GPIO.setup(IN3,GPIO.OUT)
GPIO.setup(IN4,GPIO.OUT)

GPIO.setup(EN1,GPIO.OUT)
GPIO.setup(EN2,GPIO.OUT)
GPIO.setup(EN3,GPIO.OUT)
GPIO.setup(EN4,GPIO.OUT)

GPIO.setup(servoPin,GPIO.OUT)

pwmServo = GPIO.PWM(servoPin,50)
pwmServo.start(0)

# Create PWM objects
pwm = {
    IN1: GPIO.PWM(IN1, 100),
    IN2: GPIO.PWM(IN2, 100),
    IN3: GPIO.PWM(IN3, 100),
    IN4: GPIO.PWM(IN4, 100),
    EN1: GPIO.PWM(EN1, 100),
    EN2: GPIO.PWM(EN2, 100),
    EN3: GPIO.PWM(EN3, 100),
    EN4: GPIO.PWM(EN4, 100)
}

for motor in pwm.values():
    motor.start(0)

def rotate_servo():
	pwmServo.ChangeDutyCycle(2)

def move_forward():
    pwm[right_top_wheel['forward']].ChangeDutyCycle(50)
    pwm[right_bottom_wheel['forward']].ChangeDutyCycle(50)
    pwm[left_top_wheel['forward']].ChangeDutyCycle(50)
    pwm[left_bottom_wheel['forward']].ChangeDutyCycle(50)

def move_back():
    pwm[right_top_wheel['back']].ChangeDutyCycle(50)
    pwm[right_bottom_wheel['back']].ChangeDutyCycle(50)
    pwm[left_top_wheel['back']].ChangeDutyCycle(50)
    pwm[left_bottom_wheel['back']].ChangeDutyCycle(50)

def diagonal_up_right_move():
    pwm[right_bottom_wheel['back']].ChangeDutyCycle(50)
    pwm[left_top_wheel['forward']].ChangeDutyCycle(50)

def right_move():
    pwm[right_top_wheel['back']].ChangeDutyCycle(50)
    pwm[right_bottom_wheel['forward']].ChangeDutyCycle(50)
    pwm[left_top_wheel['forward']].ChangeDutyCycle(50)
    pwm[left_bottom_wheel['back']].ChangeDutyCycle(50)
    
def diagonal_bottom_right_move():
    pwm[right_top_wheel['back']].ChangeDutyCycle(50)
    pwm[left_bottom_wheel['back']].ChangeDutyCycle(50)    
    
def left_move():
    pwm[right_top_wheel['forward']].ChangeDutyCycle(50)
    pwm[right_bottom_wheel['back']].ChangeDutyCycle(50)
    pwm[left_top_wheel['back']].ChangeDutyCycle(50)
    pwm[left_bottom_wheel['forward']].ChangeDutyCycle(50)

def diagonal_up_left_move():
    pwm[right_top_wheel['forward']].ChangeDutyCycle(50)
    pwm[left_bottom_wheel['forward']].ChangeDutyCycle(50)

def diagonal_bottom_left_move():
    pwm[right_bottom_wheel['back']].ChangeDutyCycle(50)
    pwm[left_top_wheel['back']].ChangeDutyCycle(50)

def stop_motors():
    for motor in pwm.values():
        motor.ChangeDutyCycle(0)


def execute_command(command):
    stop_motors()
    if command == 'z':
        move_forward()
    elif command == 's':
        move_back()
    elif command == 'q':
        left_move()
    elif command == 'd':
        right_move()
    elif command == 'a':
        diagonal_up_left_move()
    elif command == 'e':
        diagonal_up_right_move()
    elif command == 'w':
        diagonal_bottom_left_move()
    elif command == 'c':
        diagonal_bottom_right_move()
    elif command == 'm':
        rotate_servo()
    elif command == 'x':
        stop_motors()
    else:
        print("Invalid command! Enter 'f' for forward, 'b' for back, or 's' to stop.")

def handle_client(client_socket):
    while True:
        # Receive commands from the Django application
        command = client_socket.recv(1024).decode()
        if not command:
            break

        print(f"Received command: {command}")
        execute_command(command)

    client_socket.close()

# Create a socket server
server_ip = '0.0.0.0'  # Listen on all available interfaces
server_port = 12345  # Use the same port as in the Django application
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_ip, server_port))
server_socket.listen(5)

try:
    while True:
        print("Waiting for a connection...")
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")

        # Handle the connection in a separate thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

except KeyboardInterrupt:
    for motor in pwm.values():
        motor.stop()
    GPIO.cleanup()
    server_socket.close()
