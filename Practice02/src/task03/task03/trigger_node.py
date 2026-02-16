import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger


class TriggerNode(Node):
    def __init__(self):
        super().__init__('trigger_node')
        self.declare_parameter('service_name', '/trigger_service')
        self.declare_parameter('default_string', 'No service available')

        self.stored_string = self.get_parameter(
            'default_string'
        ).get_parameter_value().string_value

        self._fetch_trigger_response()

        srv_name = self.get_parameter(
            'service_name'
        ).get_parameter_value().string_value
        self.create_service(Trigger, srv_name, self._handle_request)
        self.get_logger().info(f'Providing service on "{srv_name}"')

    def _fetch_trigger_response(self):
        cli = self.create_client(Trigger, '/spgc/trigger')
        if not cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn('Could not reach /spgc/trigger')
            return

        future = cli.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future)
        result = future.result()
        if result is not None:
            self.stored_string = result.message
            self.get_logger().info(f'Trigger returned: "{self.stored_string}"')
        else:
            self.get_logger().warn('Trigger call returned no result')

    def _handle_request(self, request, response):
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
