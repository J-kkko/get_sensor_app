import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from udp_client import UDPSensorClient
from sensor_ui import SensorUI
from typing import List

class SensorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ui = SensorUI()
        self.client = UDPSensorClient()
        
        # 数据记录
        self.time_counter = 0
        self.history = [[], [], [], []]  # 四个传感器的历史数据
        
        # 连接信号
        self._connect_signals()
        
    def _connect_signals(self):
        """连接所有信号和槽"""
        # UI信号
        self.ui.signals.connect_clicked.connect(self._on_connect)
        self.ui.signals.disconnect_clicked.connect(self._on_disconnect)
        self.ui.signals.start_clicked.connect(self._on_start)
        self.ui.signals.stop_clicked.connect(self._on_stop)
        
        # 定时器用于更新图表
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_chart)
        self.timer.setInterval(100)  # 每100ms更新一次图表
        
    def _on_connect(self, host: str, port: int):
        """处理连接请求"""
        if self.client.connect(host, port):
            self.ui.set_connected_state(True)
            
    def _on_disconnect(self):
        """处理断开连接请求"""
        self._on_stop()
        self.client.close()
        self.ui.set_connected_state(False)
        
    def _on_start(self):
        """开始接收数据"""
        if self.client.start_receiving(self._on_data_received):
            self.ui.set_monitoring_state(True)
            self.timer.start()
            
    def _on_stop(self):
        """停止接收数据"""
        self.client.stop_receiving()
        self.ui.set_monitoring_state(False)
        self.timer.stop()
        
    def _on_data_received(self, data: List[float]):
        """处理接收到的传感器数据"""
        self.ui.update_sensor_data(data)
        
        # 记录历史数据，限制每个传感器最多保存1000个数据点
        MAX_HISTORY = 1000
        for i, value in enumerate(data):
            self.history[i].append(value)
            if len(self.history[i]) > MAX_HISTORY:
                self.history[i].pop(0)  # 移除最旧的数据点
        
        print(f"接收到数据: {data}")  # 添加调试信息
            
    def _update_chart(self):
        """更新图表显示"""
        self.time_counter += 1
        if len(self.history[0]) > 0:
            # 使用所有四个传感器的数据
            last_data = [self.history[i][-1] for i in range(4)]
            self.ui.update_chart(last_data, self.time_counter)
            print(f"更新图表: 时间={self.time_counter}, 数据={last_data}")
            
    def run(self):
        """运行应用程序"""
        self.ui.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = SensorApp()
    app.run()