import rclpy                                # ROS 2 Pythonクライアントライブラリ
from rclpy.node import Node                 # ノードクラスをインポート
from sobits_interfaces.srv import ModeCtrl  # ModeCtrlサービスインターフェースをインポート
from geometry_msgs.msg import Twist         # Twistメッセージをインポート
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion #クォータニオンからロールピッチヨーを求める。



def quaternion_to_yaw(quaternion):
    q = quaternion
    quaternion_list = [q.x, q.y, q.z, q.w]
    roll, pitch, yaw = euler_from_quaternion(quaternion_list)
    
    return yaw





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

       self.x = None
       self.y = None
       self.angle = None
       self.is_stopped = False
       self.velocity = 0.0
       
       self.waypoint_flag = 0
       self.waypoint = [[1.0, 0], [1.0, 1.0], [2.0, 2.0], [0.0, 0.0]]

       # 'mode_ctrl'という名前でModeCtrlサービスを作成し、コールバック関数を設定
       self.srv = self.create_service(ModeCtrl, 'mode_ctrl', self.mode_ctrl_callback)
       # サービスが利用可能になるまで待機
       self.get_logger().info('Waiting for service...')


   # サービスリクエストを処理するコールバック関数
   def mode_ctrl_callback(self, request, response):  
       msg = Twist()                   # Twist型メッセージのインスタンスを作成   
       response.response = True
       msg.linear.x = self.velocity          # メッセージの線形速度を設定
       self.publisher.publish(msg)  # メッセージをパブリッシュ                     
       # レスポンスを返す
       return response

   def odom_callback(self, msg):
       self.x = msg.pose.pose.position.x
       self.y = msg.pose.pose.position.y
       self.angle = quaternion_to_yaw(msg.pose.pose.orientation)
       self.get_logger().info(f"angle = {self.angle}")

       if self.x <= 0.92: 
          if self.velocity < 0.2:
              self.velocity += 0.005
       else:
          if self.velocity > 0:
              self.velocity -= 0.005

       cmd_msg = Twist()
       cmd_msg.angular.z = self.velocity

       #cmd_msg.angular.z ヨーに値を足すと左回転する。ロール ピッチ の方向に値を発行しても意味はない
       #cmd_mag.linear.x 足すとまっすぐ動く。二輪のタイヤで真横に動けず、頭足の方にも動けないのでx以外に値を発行しても意味がない
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