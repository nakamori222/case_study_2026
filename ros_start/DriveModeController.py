import rclpy                                # ROS 2 Pythonクライアントライブラリ
from rclpy.node import Node                 # ノードクラスをインポート
from sobits_interfaces.srv import ModeCtrl  # ModeCtrlサービスインターフェースをインポート
from geometry_msgs.msg import Twist         # Twistメッセージをインポート
from nav_msgs.msg import Odometry

# DriveModeControllerクラスを定義し、Nodeクラスを継承
class DriveModeController(Node):
   def __init__(self):
       # 親クラスのコンストラクタを呼び出し、ノード名を'drive_mode_controller'に設定
       super().__init__('drive_mode_controller')
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
       self.is_stopped = False
       self.velocity = 0.0
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
       self.get_logger().info(f"x = {self.x}")

       if self.x <= 0.92: 
          if self.velocity < 0.2:
              self.velocity += 0.005
       else:
          if self.velocity > 0:
              self.velocity -= 0.005

       cmd_msg = Twist()
       cmd_msg.linear.x = self.velocity
       self.publisher.publish(cmd_msg)
          
 

# メイン関数
def main(args=None):
   # rclpyライブラリを初期化
   rclpy.init(args=args)
   
   drive_mode_controller = DriveModeController()# DriveModeControllerノードのインスタンスを作成
   # ノードが終了するまでスピン（実行）し続ける
   rclpy.spin(drive_mode_controller)
   # rclpyライブラリをシャットダウン
   rclpy.shutdown()

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == '__main__':
   main()