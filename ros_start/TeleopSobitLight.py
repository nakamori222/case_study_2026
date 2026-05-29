import sys
import termios
import tty
import rclpy                                # ROS 2 Pythonクライアントライブラリ
from rclpy.node import Node                 # ノードクラスをインポート
from geometry_msgs.msg import Twist         # Twistメッセージをインポート
from std_msgs.msg import String

def get_key(settings):
    tty.setraw(sys.stdin.fileno())  # カノニカルモード解除
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

# TeleopSobitLightクラスを定義し、Nodeクラスを継承
class TeleopSobitLight(Node):
    def __init__(self):
        # 親クラスのコンストラクタを呼び出し、ノード名を'teleop_sobit_light'に設定
        super().__init__('teleop_sobit_light')
        
        # ターミナル設定の保存 (get_keyで必要)
        self.settings = termios.tcgetattr(sys.stdin)
        
        # 速度の初期値を設定
        self.velocity = 0.0 #しっかりfloat型で定義すること
        self.yaw_velocity = 0.0

        # パブリッシャーの作成
        self.publisher = self.create_publisher(Twist, '/sobit_light/manual_control/cmd_vel', 10) 
        self.telepublisher_ = self.create_publisher(String, 'keyboard_input', 10)
        
        self.get_logger().info('キーボード入力待ちノードが起動しました。Qで終了します。')

    def run(self):
        msg = String()
        msg_twist = Twist()
        try:
            while rclpy.ok():
                # キーボード入力を監視
                key = get_key(self.settings)
                
                if key == "i":
                    if self.velocity < 2.0:
                        self.velocity += 0.05

                if key == "k":
                    if self.velocity > -2.0:
                        self.velocity -= 0.05
                
                if key == "j":
                    if self.yaw_velocity < 1.0:
                        self.yaw_velocity += 0.02

                if key == "l":
                    if self.yaw_velocity > -1.0:
                        self.yaw_velocity -= 0.02
             
                if key == "s": #強制ストップ
                    self.velocity = 0.0
                    self.yaw_velocity = 0.0
                     
                msg_twist.linear.x = self.velocity
                msg_twist.angular.z = self.yaw_velocity
                self.publisher.publish(msg_twist) #速度を発行

                if key == "p": #速度確認
                    self.get_logger().info(f'velocity = {self.velocity}')
                    self.get_logger().info(f'yaw_velocity = {self.yaw_velocity}')
                
                 
                

                # 押されたキーをログに表示
                self.get_logger().info(f'Pressed: {key}')

                # 'q' または 'Q' が押されたら終了
                if key.lower() == 'q':
                    break
                
                rclpy.spin_once(self, timeout_sec=0.1)

        except Exception as e:
            self.get_logger().error(f'エラーが発生しました: {e}')
        finally:
            # ターミナルの設定を元に戻す
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

# メイン関数
def main(args=None):
    # rclpyライブラリを初期化
    rclpy.init(args=args)
   
    teleop_sobit_light = TeleopSobitLight() # TeleopSobitLightノードのインスタンスを作成
   
    # ★修正: spin()の代わりに、自作したrun()ループを実行する
    teleop_sobit_light.run()
   
    # rclpyライブラリをシャットダウン
    rclpy.shutdown()

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == '__main__':
    main()