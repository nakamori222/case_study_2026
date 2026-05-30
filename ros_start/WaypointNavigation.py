#角度を合わせて直進し、目的地に行くプログラム
#P制御のような、角度を修正する機能などはない
#自己位置推定はオドメトリのみを用いた

import rclpy                                # ROS 2 Pythonクライアントライブラリ
from rclpy.node import Node                 # ノードクラスをインポート
from sobits_interfaces.srv import ModeCtrl  # ModeCtrlサービスインターフェースをインポート
from geometry_msgs.msg import Twist         # Twistメッセージをインポート
from nav_msgs.msg import Odometry
from math import sqrt, atan2, pi


# WaypointNavigationクラスを定義し、Nodeクラスを継承
class WaypointNavigation(Node):
    def __init__(self):
        # 親クラスのコンストラクタを呼び出し、ノード名を'way_point_navigation'に設定
        super().__init__('way_point_navigation')
        # '/sobit_light/manual_control/cmd_vel'という名前のトピックにTwist型メッセージをパブリッシュするパブリッシャーを作成
        self.publisher = self.create_publisher(Twist,                                           
                        '/sobit_light/manual_control/cmd_vel', 
                        10) 

        self.subscription = self.create_subscription(
            Odometry,
            '/sobit_light/odometry/odometry',
            self.odom_callback,
            10) #サブスクライバーを追加した 4/30

        self.frequency = 60.0
        timer_period = 1.0 / self.frequency  # 0.2秒ごとに実行
        self.timer = self.create_timer(timer_period, self.navigate_control)

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.velocity = 0.0
        self.yaw_velocity = 0.0

        self.arrival_flag = False
        self.angleset_flag = False
        self.point_idx = 0
        self.waypoint = [[1, 1], [1, 0], [0, 0]]
        self.stop_count = 0



        # サービスが利用可能になるまで待機
        self.get_logger().info('Waiting for service...')

    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        
        # クォータニオンからヨー角（z軸まわりの回転角度 = ロボットの向き）への変換式
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        
        # self.angular にラジアン単位（-pi ～ +pi）で現在の角度を代入
        self.yaw = atan2(siny_cosp, cosy_cosp)

        #self.get_logger().info(f"x = {self.x}")
        #self.get_logger().info(f"yaw = {self.yaw}")

    def navigate_control(self):
        if self.point_idx < len(self.waypoint):        
            if self.angleset_flag == False: #角度を合わせる
                self.navigate_angular() 
            else:
                if self.stop_count < 180: #3秒待機
                        self.stop_count += 1
                        self.get_logger().info(f"待ってるよー{self.stop_count}")
                else:
                    if self.arrival_flag == False: #直進する
                        self.navigate_linear()
                    else:
                        if self.stop_count < 180: #3秒待機
                            self.stop_count += 1
                            #self.get_logger().info(f"待ってるよー{self.stop_count}")
                        
                        else:
                            self.stop_count = 0
                            self.point_idx += 1
                            self.arrival_flag = False
                            self.angleset_flag = False
                            self.get_logger().info(f"動きます")
        else:
            self.get_logger().info(f"どこ行くの？")


    def navigate_linear(self):
        point = self.waypoint[self.point_idx]
        dist = sqrt((point[0]-self.x) ** 2 + (point[1]-self.y) ** 2)
        self.get_logger().info(f"dist = {dist}")

        if dist > 0.08: 
            if self.velocity < 0.2:
                self.velocity += (0.2 / self.frequency) #周波数で割って急激に速度が変化しないようにした
        else:
            if self.velocity > 0:
                self.velocity -= (0.2 / self.frequency)
        
        if dist < 0.05 : #到着処理
            self.arrival_flag = True
            self.velocity = 0.0
            self.stop_count = 0

        cmd_msg = Twist()
        cmd_msg.linear.x = self.velocity
        self.publisher.publish(cmd_msg)

    def navigate_angular(self):
        point = self.waypoint[self.point_idx]
        angle = (atan2(point[1] - self.y, point[0] - self.x)) - self.yaw

        if abs(angle) > pi/12:
            if self.yaw_velocity < 0.3:
                self.yaw_velocity += (0.2 / self.frequency)
        else:
            if self.yaw_velocity > 0.02:
                self.yaw_velocity -= (0.05 /self.frequency)

        
        if abs(angle) < pi / 180:
            self.angleset_flag = True
            self.yaw_velocity = 0.0
            self.stop_count = 0

        cmd_msg = Twist()
        cmd_msg.angular.z = self.yaw_velocity
        self.publisher.publish(cmd_msg)


          
 

# メイン関数
def main(args=None):
   # rclpyライブラリを初期化
   rclpy.init(args=args)
   
   way_point_navigation = WaypointNavigation()# WaypointNavigationノードのインスタンスを作成
   # ノードが終了するまでスピン（実行）し続ける
   rclpy.spin(way_point_navigation)
   # rclpyライブラリをシャットダウン
   rclpy.shutdown()

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == '__main__':
   main()