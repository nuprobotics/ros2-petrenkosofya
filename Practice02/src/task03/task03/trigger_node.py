import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class TriggerNode(Node):
    def __init__(self):
        super().__init__('trigger_node')
        self.declare_parameter('service_name', '/trigger_service')
        self.declare_parameter('default_string', 'No service available')

        service_name = self.get_parameter('service_name').get_parameter_value().string_value
        self.default_string = self.get_parameter('default_string').get_parameter_value().string_value

        self.stored_string = self.default_string

        self.client = self.create_client(Trigger, '/spgc/trigger')
        self.call_trigger_service()

        self.srv = self.create_service(Trigger, service_name, self.service_callback)
        self.get_logger().info(
            f'Service "{service_name}" ready, stored string: "{self.stored_string}"'
        )

    def call_trigger_service(self):
        if self.client.wait_for_service(timeout_sec=5.0):
            request = Trigger.Request()
            future = self.client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            if future.result() is not None:
                self.stored_string = future.result().message
                self.get_logger().info(
                    f'Received from /spgc/trigger: "{self.stored_string}"'
                )
            else:
                self.get_logger().warn('Service call to /spgc/trigger failed')
        else:
            self.get_logger().warn(
                'Service /spgc/trigger not available, using default string'
            )

    def service_callback(self, request, response):
        response.success = True
        response.message = self.stored_string
        return response


def main(args=None):
    rclpy.init(args=args)
    node = TriggerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
