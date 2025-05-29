import socket
import threading
from datetime import datetime
from typing import Callable, Optional, List, Tuple

class UDPSensorClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_thread = None
        self.running = False
        self.callback = None
        self.server_address = None
        self.time_index = 0  # 用于图表X轴的时间索引

    def connect(self, host: str, port: int) -> bool:
        """连接到AP热点(UDP服务器)"""
        try:
            self.server_address = (host, port)
            self.socket.bind(('0.0.0.0', 8080))  # 绑定到任意可用端口
            print(f"连接到服务器 {host}:{port}")
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False

    def start_receiving(self, callback: Callable[[List[float]], None]) -> bool:
        """开始接收数据"""
        if not self.running and self.server_address:
            self.callback = callback
            self.running = True
            self.data_count = 0  # 重置计数器
            self.receive_thread = threading.Thread(
                target=self._receive_loop, 
                daemon=True
            )
            self.receive_thread.start()
            return True
        return False

    def stop_receiving(self):
        """停止接收数据"""
        self.running = False
        if self.receive_thread:
            self.receive_thread.join()

    def _receive_loop(self):
        """接收数据的循环"""
        buffer_size = 1024
        while self.running:
            try:
                data, addr = self.socket.recvfrom(buffer_size)
                current_time = datetime.now()
                
                # 打印原始数据
                print(f"[{current_time.strftime('%H:%M:%S.%f')[:-3]}] 收到原始数据: {data}")
                
                # 解析数据
                sensor_data = self._parse_data(data.decode('utf-8'))
                if sensor_data and self.callback:
                    self.time_index += 1  # 递增时间索引
                    print(f"处理数据 [时间索引:{self.time_index}]: {sensor_data}")
                    # 调用回调函数，传递传感器数据
                    self.callback(sensor_data)
            except Exception as e:
                print(f"接收数据错误: {e}")

    def _parse_data(self, data_str: str) -> Optional[List[float]]:
        """解析传感器数据字符串"""
        try:
            parts = [x.strip() for x in data_str.split(',')]
            if len(parts) == 4:
                values = [float(part) for part in parts]
                print(f"解析成功: {values}")
                return values
            else:
                print(f"数据格式错误: 期望4个值，实际收到{len(parts)}个值")
        except (ValueError, AttributeError) as e:
            print(f"数据解析错误: {e}")
        return None

    def close(self):
        """关闭连接"""
        self.stop_receiving()
        self.socket.close()