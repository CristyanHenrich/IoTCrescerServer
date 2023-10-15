from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

SERVO_PIN = 18
INITIAL_ROTATION = 90

GPIO.setmode(GPIO.BCM)

LED_PINS = {
	1: 11,
	2: 12,
	3: 13,
	4: 15,
	5: 16,
}

GPIO.setup(SERVO_PIN, GPIO.OUT)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

for pin in LED_PINS.values():
	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)
	
def setServoAngle(angle):
	duty = float(angle) / 18.0 + 1.90
	GPIO.output(SERVO_PIN, True)
	pwm.ChangeDutyCycle(duty)
	time.sleep(2)
	GPIO.output(SERVO_PIN, False)
	pwm.ChangeDutyCycle(0)

@app.route('/led', methods=['POST'])
def control_led():
	data = request.get_json()
	action = data.get('action')
	led_number = data.get('led_number')
	
	if led_number not in LED_PINS:
		return jsonify({"error": "Invalid LED number"}),
			
	if action == 'on':
		GPIO.output(LED_PINS[led_number], GPIO.HIGH)
		return jsonify({"message": f"LED {led_number} Ligado"})
	elif action == 'off':
		GPIO.output(LED_PINS[led_number], GPIO.LOW)
		return jsonify({"message": f"LED {led_number} Desligado"})
	else:
		return jsonify({"error": "Ação Invalida"})
		
@app.route('/servo', methods=['POST'])
def control_servo():
	data = request.get_json()
	rotation = data.get('rotation', INITIAL_ROTATION)
	
	try:
		setServoAngle(rotation)
		setServoAngle(INITIAL_ROTATION)
		return jsonify({"message": f"Servo movido para {rotation} e retornado para posição inicial."})
	except Exception as e:
		return jsonify({"error": f"Erro ao controlar servo: {str(e)}"}), 500
		
if __name__ == '__main__':
	try:
		app.run(host='0.0.0.0', port=5000)
	finally:
		GPIO.cleanup()