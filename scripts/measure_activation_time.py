#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Log
from lifecycle_msgs.msg import TransitionEvent
import time
import os
import csv
from datetime import datetime
from functools import partial

class ActivationTimeMonitor(Node):
    """
    指定されたライフサイクルノードがactive状態になるまでの時間を計測し、
    個別にCSVファイルへ追記するノード。
    """
    def __init__(self):
        super().__init__('activation_time_monitor')

        # パラメータの宣言と取得
        self.declare_parameter('target_nodes', [''])
        self.declare_parameter('output_file_path', '/tmp/activation_times.csv')

        self.target_nodes = set(self.get_parameter('target_nodes').get_parameter_value().string_array_value)
        self.output_file = self.get_parameter('output_file_path').get_parameter_value().string_value

        self.logged_nodes = set()
        self.start_time = time.time()

        # 各ターゲットノードのライフサイクルイベントを購読
        for node_name in self.target_nodes:
            if node_name: # 空のノード名を無視
                self.create_subscription(
                    TransitionEvent,
                    f'/{node_name}/transition_event',
                    partial(self.listener_callback, node_name=node_name),
                    10)

        self.get_logger().info(f'Monitoring activation for nodes: {self.target_nodes}')

    def listener_callback(self, msg: TransitionEvent, node_name: str):
        # 'activating' から 'active' への遷移を検知
        if msg.goal_state.label == 'active' and msg.start_state.label == 'activating' and node_name not in self.logged_nodes:
            end_time = time.time()
            duration = end_time - self.start_time
            self.get_logger().info(f'Node "{node_name}" became active in {duration:.4f} seconds.')
            self.logged_nodes.add(node_name)

            # 結果をCSVファイルに追記
            # ファイルパスのディレクトリが存在しない場合は作成
            output_dir = os.path.dirname(self.output_file)
            os.makedirs(output_dir, exist_ok=True)

            file_exists = os.path.isfile(self.output_file)
            with open(self.output_file, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                if not file_exists:
                    csv_writer.writerow(['timestamp', 'node_name', 'activation_time_sec'])
                timestamp = datetime.now().isoformat()
                csv_writer.writerow([timestamp, node_name, f'{duration:.4f}'])

            # すべてのターゲットノードのログを記録したら終了
            if self.logged_nodes.issuperset(self.target_nodes):
                self.get_logger().info('All target nodes have been logged. Shutting down.')
                self.destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = ActivationTimeMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

if __name__ == '__main__':
    main()