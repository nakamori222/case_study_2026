import rclpy                                # ROS 2 Pythonクライアントライブラリ
from rclpy.node import Node                 # ノードクラスをインポート
from sobits_interfaces.srv import ModeCtrl  # ModeCtrlサービスインターフェースをインポート
import time

# IntervalModeChangerクラスを定義し、Nodeクラスを継承
class IntervalModeChanger(Node):
   def __init__(self):
       # 親クラスのコンストラクタを呼び出し、ノード名を'interval_mode_changer'に設定
       super().__init__('interval_mode_changer')
       # 'mode_ctrl'という名前でModeCtrlサービスクライアントを作成
       self.client = self.create_client(ModeCtrl, 'mode_ctrl')
       # サービスが利用可能になるまで１秒ごとに繰り返す
       while not self.client.wait_for_service(timeout_sec=1.0):
           self.get_logger().info('Service not available, waiting again...')
       # リクエストオブジェクトを作成
       self.request = ModeCtrl.Request()


   # サービスリクエストを送信する関数
   def send_request(self, mode):
       # リクエストのモードを設定
       self.request.mode = mode
       # 非同期でサービスを呼び出し、将来の結果を取得
       self.future = self.client.call_async(self.request)
       # 結果が得られたときに呼び出されるコールバック関数を設定
       self.future.add_done_callback(self.response_callback)


   # レスポンスを処理するコールバック関数
   def response_callback(self, future):
       try:
           response = future.result()
           self.get_logger().info(f'Response: {response.response}')
       except Exception as e:
           self.get_logger().error(f'Service call failed: {e}')


# メイン関数
def main(args=None):
   # rclpyライブラリを初期化
   rclpy.init(args=args)
   # IntervalModeChangerノードのインスタンスを作成
   interval_mode_changer = IntervalModeChanger()
   # 最後にリクエストを送信した時間を記録
   last_request_time = time.time()  
   # 初期モードを設定
   mode = 1 
   # 時間を計測しながらスピン
   # ROS 2が動作している間ループを継続
   while rclpy.ok():                                
       # ノードを0.1秒間スピンして、コールバックを処理
       rclpy.spin_once(interval_mode_changer, timeout_sec=0.1)
       # 現在の時間を取得
       current_time = time.time()
       # 3秒ごとにモードを変更
       if current_time - last_request_time >= 3.0:
           if mode == 1:
               mode = 2
           elif mode == 2:
               mode = 1
           interval_mode_changer.send_request(mode) # モード変更リクエストを送信
           last_request_time = current_time         # 最後にリクエストを送信した時間を更新
           interval_mode_changer.get_logger().info(f'Sent mode: {mode}, Time: {int(last_request_time)}')
   # ノードを破棄
   interval_mode_changer.destroy_node()
   # rclpyライブラリをシャットダウン
   rclpy.shutdown()

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == '__main__':
   main()