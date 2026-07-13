"""
Laptop MQTT controller using AI planning.
"""

import time

import paho.mqtt.client as mqtt

from config.config_loader import get_mqtt_broker_host, get_mqtt_broker_port
from executor.plan_executor import execute_plan
from knowledge_base import warehouse_kb as kb
from mqtt import topics
from planner.ai_planner import run_planner
from planner.problem_generator import generate_problem
from processor.context_processor import calculate_context


BROKER = get_mqtt_broker_host()
PORT = get_mqtt_broker_port()

MIN_SECONDS_BETWEEN_PLANS = 3


class LaptopController:
    def __init__(self):
        self.broker = BROKER
        self.port = PORT

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.sensor_state = {}
        self.last_published = {}
        self.last_context_signature = None
        self.last_planning_time = 0
        self.current_plan_text = "No plan generated yet"
        self.last_plan_text = "No previous plan"

    def connect(self):
        print(f"[MQTT] Connecting to broker at {self.broker}:{self.port}")
        self.client.connect(self.broker, self.port, keepalive=60)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"[MQTT] Connected: {reason_code}")

        client.subscribe("warehouse/sensors/#")
        print("[MQTT] Subscribed to warehouse/sensors/#")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        message = msg.payload.decode(errors="replace").strip()

        print(f"[SENSOR RECEIVED] {topic} -> {message}")

        self.update_sensor_state(topic, message)
        if topic == topics.SENSOR_BATTERY_STATUS:
            self.evaluate_system_state()
        

    def update_sensor_state(self, topic, message):
        if topic == topics.SENSOR_TEMPERATURE:
            sensor_name = "temperature"
        elif topic == topics.SENSOR_HUMIDITY:
            sensor_name = "humidity"
        elif topic == topics.SENSOR_GAS_STATUS:
            sensor_name = "gas_status"
        elif topic == topics.SENSOR_OCCUPANCY:
            sensor_name = "occupancy"
        elif topic == topics.SENSOR_BATTERY_STATUS:
            sensor_name = "battery_status"
        else:
            return

        self.sensor_state[sensor_name] = message
        kb.update_sensor_value(sensor_name, message)

    def enough_sensor_data(self):
        required_values = [
            "temperature",
            "humidity",
            "gas_status",
            "occupancy",
            "battery_status",
        ]

        for value in required_values:
            if value not in self.sensor_state:
                return False

        return True

    def evaluate_system_state(self):
        if not self.enough_sensor_data():
            return

        context = calculate_context(self.sensor_state)

        risk_level = context["risk_level"]
        battery_condition = context["battery_condition"]
        occupancy = context["occupancy"]

        self.publish_if_changed(topics.CONTEXT_RISK_LEVEL, risk_level)
        self.publish_if_changed(topics.CONTEXT_BATTERY_CONDITION, battery_condition)

        system_state = self.risk_to_system_state(risk_level)

        self.publish_if_changed(topics.CONTEXT_RISK_LEVEL, risk_level, retain=True)
        self.publish_if_changed(topics.CONTEXT_SYSTEM_STATE, system_state, retain=True)
        self.publish_if_changed(topics.CONTEXT_BATTERY_CONDITION, battery_condition, retain=True)

        print(
            f"[STATE] risk={risk_level} "
            f"battery_condition={battery_condition} "
            f"temperature={context['temperature']} "
            f"humidity={context['humidity']} "
            f"gas={context['gas_status']} "
            f"occupancy={context['occupancy']} "
            f"battery={context['battery_status']}"
        )

        context_signature = (
            risk_level,
            battery_condition,
            occupancy,
        )

        now = time.time()

        if context_signature == self.last_context_signature:
            return

        if now - self.last_planning_time < MIN_SECONDS_BETWEEN_PLANS:
            return

        self.last_context_signature = context_signature
        self.last_planning_time = now

        print("[SYSTEM] Context changed. Generating new PDDL problem...")

        generate_problem(context)

        plan = run_planner()

        if not plan:
            print("[SYSTEM] No plan found. Commands not updated.")
            return

        kb.set_latest_plan(plan)

        plan_text = "; ".join(plan)
        # self.publish_if_changed(topics.PLANNING_PLAN, plan_text)

        # execute_plan(plan, self.client)

        # Move the old current plan to last plan before updating
        self.last_plan_text = self.current_plan_text
        self.current_plan_text = plan_text

        self.publish_if_changed(topics.PLANNING_LAST_PLAN, self.last_plan_text, retain=True)
        self.publish_if_changed(topics.PLANNING_CURRENT_PLAN, self.current_plan_text, retain=True)

        # Keep old topic too, for compatibility
        self.publish_if_changed(topics.PLANNING_PLAN, self.current_plan_text, retain=True)

        self.publish_if_changed(topics.PLANNING_EXECUTION_STATUS, "EXECUTING", retain=True)

        execute_plan(plan, self.client)

        self.publish_if_changed(topics.PLANNING_EXECUTION_STATUS, "COMPLETED", retain=True)

    def publish_if_changed(self, topic, message):
        if self.last_published.get(topic) == message:
            return

        self.client.publish(topic, str(message))
        self.last_published[topic] = message

        print(f"[MQTT PUBLISHED] {topic} -> {message}")

    def run(self):
        self.connect()

        print("[SYSTEM] Laptop AI planner controller running")
        print("[SYSTEM] Press Ctrl+C to stop")

        try:
            self.client.loop_forever()

        except KeyboardInterrupt:
            print("\n[SYSTEM] Stopping laptop controller...")

        finally:
            self.client.disconnect()
            time.sleep(0.5)
            print("[SYSTEM] Laptop controller stopped")

    def risk_to_system_state(self, risk_level):
        risk_level = str(risk_level).upper()

        if risk_level == "HIGH":
            return "EMERGENCY"

        if risk_level == "MEDIUM":
            return "WARNING"

        return "NORMAL"
    
    def publish_if_changed(self, topic, message, retain=False):
        if self.last_published.get(topic) == message:
            return

        self.client.publish(topic, str(message), retain=retain)
        self.last_published[topic] = message

        print(f"[MQTT PUBLISHED] {topic} -> {message}")

def main():
    controller = LaptopController()
    controller.run()


if __name__ == "__main__":
    main()