import rclpy
import cv2
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy import qos as QOS

CAMERA_FPS = 10.0
CAMERA_FRAME_WIDTH = 640    # pixels
CAMERA_FRAME_HEIGHT = 480   # pixels


class CameraPublisher(Node):

    def __init__(self):
        self.cnt = 0
        self.bridge = CvBridge()
        
        # open camera and set dimensions
        self.cap = cv2.VideoCapture('/dev/video0')#, cv2.CAP_V4L)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
        
        super().__init__('camera_publisher')
        
        # create QoS profile for publisher
        qos_profile = QOS.qos_profile_system_default
        qos_profile.reliability = QOS.QoSReliabilityPolicy.BEST_EFFORT
        qos_profile.history = QOS.QoSHistoryPolicy.KEEP_LAST
        qos_profile.depth = 5
        qos_profile.durability = QOS.QoSDurabilityPolicy.VOLATILE
        
        self.publisher = self.create_publisher(Image, 'camera_image', qos_profile)
        timer_period = 1.0 / CAMERA_FPS  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        # take frame
        ret, frame = self.cap.read()
        if ret == True:
            # send image to topic
            try:
                self.publisher.publish(self.bridge.cv2_to_imgmsg(frame))
            except CvBridgeError as e:
                print(e)
            
            # debug counter
            self.get_logger().info('Publishing: frame %d' % self.cnt)
            self.cnt += 1
            if self.cnt > 9999:
                self.cnt = 0


def main(args=None):
    rclpy.init(args=args)

    camera_publisher = CameraPublisher()

    rclpy.spin(camera_publisher)

    camera_publisher.cap.release()
    camera_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
