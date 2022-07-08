import rclpy
import cv2
from pyfakewebcam import pyfakewebcam
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from sensor_msgs.msg import Image
from rclpy import qos as QOS
import os

IMG_W = 640
IMG_H = 480

class CameraSubscriber(Node):

    def __init__(self):
        self.cnt = 0
        self.bridge = CvBridge()
        super().__init__('camera_subscriber')
        self.fpy = pyfakewebcam.FakeWebcam('/dev/video2', IMG_W, IMG_H)
        # create QoS profile for subscriber
        qos_profile = QOS.qos_profile_system_default
        qos_profile.reliability = QOS.QoSReliabilityPolicy.BEST_EFFORT
        qos_profile.history = QOS.QoSHistoryPolicy.KEEP_LAST
        qos_profile.depth = 5
        qos_profile.durability = QOS.QoSDurabilityPolicy.VOLATILE
        
        self.subscription = self.create_subscription(Image, 'camera_image', self.listener_callback, qos_profile)
        

    def listener_callback(self, msg : Image):
        # debug counter
        self.get_logger().info('I heard: frame %d' % self.cnt)
        self.cnt += 1
        if self.cnt > 9999:
            self.cnt = 0
        
        # receive and show image from topic
        try:
            frame = self.bridge.imgmsg_to_cv2(msg)
            vflip_frame = cv2.flip(frame, -1) # flip received image vertically and horizontally
            cv2.imshow("camera", vflip_frame)
            fakecam_frame = cv2.cvtColor(vflip_frame, cv2.COLOR_BGR2RGB)
            self.fpy.schedule_frame(fakecam_frame)
        except CvBridgeError as e:
            print(e)
        
        cv2.waitKey(1)


def main(args=None):
    os.system("modprobe v4l2loopback devices=2")

    rclpy.init(args=args)

    camera_subscriber = CameraSubscriber()

    rclpy.spin(camera_subscriber)

    camera_subscriber.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
