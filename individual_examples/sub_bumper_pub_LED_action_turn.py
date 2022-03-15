import sys
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from irobot_create_msgs.msg import HazardDetectionVector

from irobot_create_msgs.msg import LedColor
from irobot_create_msgs.msg import LightringLeds

from rclpy.action import ActionClient
from irobot_create_msgs.action import RotateAngle


class ColorPalette():
    """ Helper Class to define frequently used colors"""

    def __init__(self):
        self.red = LedColor(red=255, green=0, blue=0)
        self.green = LedColor(red=0, green=255, blue=0)
        self.blue = LedColor(red=0, green=0, blue=255)
        self.yellow = LedColor(red=255, green=255, blue=0)
        self.pink = LedColor(red=255, green=0, blue=255)
        self.cyan = LedColor(red=0, green=255, blue=255)
        self.purple = LedColor(red=127, green=0, blue=255)
        self.white = LedColor(red=255, green=255, blue=255)
        self.grey = LedColor(red=189, green=189, blue=189)
        self.tufts_blue = LedColor(red=98, green=166, blue=10)
        self.tufts_brown = LedColor(red=94, green=75, blue=60)


class BumperLEDTurn(Node):
    def __init__(self):
        super().__init__('bumper_turn')
        self.cp = ColorPalette()

        self.lights_publisher = self.create_publisher(
            LightringLeds, '/cmd_lightring', 10)

        self.subscription = self.create_subscription(
            HazardDetectionVector, '/hazard_detection', self.listener_callback, qos_profile_sensor_data)

        self._action_client = ActionClient(self, RotateAngle, '/rotate_angle')

        # Initialize the structure of the message we are publishing to the LEDs
        self.lightring = LightringLeds()
        self.lightring.override_system = True

    def listener_callback(self, msg):
        for detection in msg.detections:
            det = detection.header.frame_id
            lightring = LightringLeds()
            lightring.override_system = True

            if det != "base_link":
                print(det)
                if det == "bump_right":
                    light_list = [self.cp.blue, self.cp.blue, self.cp.blue,
                                  self.cp.blue, self.cp.blue, self.cp.blue]
                    self.send_goal(angle=-1.57)
                elif det == "bump_left":
                    light_list = [self.cp.red, self.cp.red, self.cp.red,
                                  self.cp.red, self.cp.red, self.cp.red]
                    self.send_goal(angle=1.57)
                elif det == "bump_front_left":
                    light_list = [self.cp.pink, self.cp.pink, self.cp.pink,
                                  self.cp.pink, self.cp.pink, self.cp.pink]
                    self.send_goal(angle=1.57)
                elif det == "bump_front_right":
                    light_list = [self.cp.cyan, self.cp.cyan, self.cp.cyan,
                                  self.cp.cyan, self.cp.cyan, self.cp.cyan]
                    self.send_goal(angle=-1.57)
                elif det == "bump_front_center":
                    light_list = [self.cp.white, self.cp.white, self.cp.white,
                                  self.cp.white, self.cp.white, self.cp.white]

                current_time = self.get_clock().now()

                self.lightring.header.stamp = current_time.to_msg()
                self.lightring.leds = light_list
                
                self.lights_publisher.publish(self.lightring)

    def send_goal(self, angle=1.57, max_rotation_speed=0.5):
        goal_msg = RotateAngle.Goal()
        goal_msg.angle = angle
        goal_msg.max_rotation_speed = max_rotation_speed

        self._action_client.wait_for_server()

        self._send_goal_future = self._action_client.send_goal_async(goal_msg)

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted :)')


def main(args=None):
    rclpy.init(args=args)

    dance = BumperLEDTurn()
    try:
        rclpy.spin(dance)
    except KeyboardInterrupt:
        print('Caught keyboard interrupt')
    except BaseException:
        print('Exception:', file=sys.stderr)
    finally:
        print("Done")
        rclpy.shutdown()


if __name__ == '__main__':
    main()
