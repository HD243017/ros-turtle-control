import rclpy as rp
from rclpy.node import Node

from turtlesim.msg import Pose
from geometry_msgs.msg import Twist

from std_srvs.srv import Empty

class TurtleController(Node):
	def __init__(self):
		super().__init__("turtle_controller")

		self.current_pose = None

		self.subscription = self.create_subscription(
			Pose,
			'/turtle1/pose',
			self.pose_callback,
			10
			)

		self.publisher = self.create_publisher(
			Twist,
			'/turtle1/cmd_vel',
			10
			)

		self.reset_client = self.create_client(
			Empty,
			'/reset'
			)
	def pose_callback(self, msg):
		self.current_pose = msg

	def move_turtle(self, linear_x, angular_z):
		msg = Twist()
		msg.linear.x = float(linear_x)
		msg.angular.z = float(angular_z)
		self.publisher.publish(msg)

	def reset_turtle(self):
		if self.reset_client.wait_for_service(timeout_sec=1.0):
			req = Empty.Request()
			self.reset_client.call_async(req)
		else:
			self.get_logger().warn("Reset service not available")


def main(args=None):
	rp.init(args=args)
	node = TurtleController()
	rp.spin(node)
	node.destroy_node()
	rp.shutdown()

if __name__ == '__main__':
	main()