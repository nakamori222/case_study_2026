import rclpy                                # ROS 2 Pythonクライアントライブラリ
import math
from rclpy.node import Node                 # ノードクラスをインポート
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState

# OdometrySobitLightクラスを定義し、Nodeクラスを継承
class OdometrySobitLight(Node):
   def __init__(self):
       # 親クラスのコンストラクタを呼び出し、ノード名を'odometry_sobit_light'に設定
       super().__init__('odometry_sobit_light')

       self.joint_sub = self.create_subscription(
            JointState,
            '/sobit_light/joint_states',
            self.joint_callback,
            10) #jointのデータを購読する 5/28

       self.wheel_vel_l = 0.0
       self.wheel_vel_r = 0.0

       self.wheel_r = 0.03 #タイヤ半径 3cm
       self.tred_r = 0.1 #トレッド半径（ロボ中心からタイヤまでの距離） 10cm
       
       self.angle = 0 #シータに当たるもの、向いている方向
       self.x = 0
       self.y = 0

       self.last_time = None
       

       # サービスが利用可能になるまで待機
       self.get_logger().info('Waiting for service...')
       
   def joint_callback(self, msg):
       # 配列の0番目が左輪(base_l_drive_wheel_joint)、1番目が右輪(base_r_drive_wheel_joint)
       self.wheel_vel_l = msg.velocity[0]
       self.wheel_vel_r = msg.velocity[1]
       
       #時間計測
       current_time = self.get_clock().now()

       if self.last_time is None:
           self.last_time = current_time
           return

       dt = (current_time - self.last_time).nanoseconds / 1e9
       self.last_time = current_time

       vel = (self.wheel_vel_r + self.wheel_vel_l) / 2
       dif_vel = (self.wheel_vel_r - self.wheel_vel_l) / 2

       self.angle = self.angle + (self.wheel_r / self.tred_r) * dif_vel * dt
       self.x += (self.wheel_r * vel * math.cos(self.angle)) * dt
       self.y += (self.wheel_r * vel * math.sin(self.angle)) * dt

       self.angle = math.atan2(math.sin(self.angle), math.cos(self.angle))
       
       # 試しにターミナルに現在のホイールの角速度を表示してみる
       self.get_logger().info(f"x =  {self.x:.4f}, y = : {self.y:.4f} ang = {self.angle} rad")
 

# メイン関数
def main(args=None):
   # rclpyライブラリを初期化
   rclpy.init(args=args)
   
   odometry_sobit_light = OdometrySobitLight()# OdometrySobitLightノードのインスタンスを作成
   # ノードが終了するまでスピン（実行）し続ける
   rclpy.spin(odometry_sobit_light)
   # rclpyライブラリをシャットダウン
   rclpy.shutdown()

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == '__main__':
   main()