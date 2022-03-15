import sys
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from irobot_create_msgs.msg import HazardDetectionVector

from irobot_create_msgs.msg import LedColor
from irobot_create_msgs.msg import LightringLeds


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


class BumperLightChange(Node):

    def __init__(self):
        super().__init__('bumper_light_change')
        self.cp = ColorPalette()

        self.lights_publisher = self.create_publisher(
            LightringLeds, '/cmd_lightring', 10)

        self.subscription = self.create_subscription(
            HazardDetectionVector, '/hazard_detection', self.listener_callback, qos_profile_sensor_data)

        self.lightring = LightringLeds()
        self.lightring.override_system = True

    def listener_callback(self, msg):
        '''
        This function is called every time self.subscription gets a message
        from the Robot. It then changes color based on that message.
        '''
        for detection in msg.detections:
            det = detection.header.frame_id

            if det != "base_link":
                print(det)
                if det == "bump_right":
                    light_list = [self.cp.blue, self.cp.blue, self.cp.blue,
                                  self.cp.blue, self.cp.blue, self.cp.blue]
                elif det == "bump_left":
                    light_list = [self.cp.red, self.cp.red, self.cp.red,
                                  self.cp.red, self.cp.red, self.cp.red]
                elif det == "bump_front_left":
                    light_list = [self.cp.pink, self.cp.pink, self.cp.pink,
                                  self.cp.pink, self.cp.pink, self.cp.pink]
                elif det == "bump_front_right":
                    light_list = [self.cp.cyan, self.cp.cyan, self.cp.cyan,
                                  self.cp.cyan, self.cp.cyan, self.cp.cyan]
                elif det == "bump_front_center":
                    light_list = [self.cp.white, self.cp.white, self.cp.white,
                                  self.cp.white, self.cp.white, self.cp.white]

                current_time = self.get_clock().now()

                self.lightring.header.stamp = current_time.to_msg()
                self.lightring.leds = light_list
                
                self.lights_publisher.publish(self.lightring)
            # self.get_logger().info('I heard: "%s"' % msg)


def main(args=None):
    rclpy.init(args=args)

    bumper_light = BumperLightChange()
    try:
        rclpy.spin(bumper_light)
    except KeyboardInterrupt:
        print('\nCaught keyboard interrupt')
    finally:
        print("Done")
        rclpy.shutdown()


if __name__ == '__main__':
    main()
