from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QGroupBox, QFormLayout, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QColor
from typing import List

class SensorSignals(QObject):
    """自定义信号类"""
    connect_clicked = pyqtSignal(str, int)
    disconnect_clicked = pyqtSignal()
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()

class SensorUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.signals = SensorSignals()
        self.setWindowTitle("传感器数据监控")
        self.setGeometry(100, 100, 800, 600)
        self.sensor_names = ["酒精传感器", "空气质量传感器", "湿度传感器", "辐射传感器"]
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件"""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 连接控制区域
        connection_group = QGroupBox("连接设置")
        connection_layout = QFormLayout()
        
        self.host_input = QLineEdit("0.0.0.0")
        self.port_input = QLineEdit("8080")
        self.connect_btn = QPushButton("连接")
        self.disconnect_btn = QPushButton("断开")
        self.start_btn = QPushButton("开始检测")
        self.stop_btn = QPushButton("停止检测")
        self.disconnect_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        
        # 主机地址和端口号放在同一行
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("主机地址:"))
        input_layout.addWidget(self.host_input)
        input_layout.addSpacing(10)
        input_layout.addWidget(QLabel("端口号:"))
        input_layout.addWidget(self.port_input)
        input_layout.setSpacing(5)
        connection_layout.addRow(input_layout)
        
        # 按钮行布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.setSpacing(10)
        connection_layout.addRow(btn_layout)
        
        connection_group.setLayout(connection_layout)
        
        # 图表区域 - 4个传感器2x2布局，每个图表上方显示当前数值
        self.sensor_labels = [
            QLabel("0.00"), QLabel("0.00"), 
            QLabel("0.00"), QLabel("0.00")
        ]
        self.chart_views = []
        
        # 创建主图表容器和网格布局
        chart_container = QWidget()
        main_chart_layout = QGridLayout()
        chart_container.setMinimumSize(800, 600)
        
        colors = [
            QColor(255, 100, 100),  # 红
            QColor(100, 255, 100),  # 绿
            QColor(100, 100, 255),  # 蓝
            QColor(255, 200, 50)    # 黄
        ]
        
        for i in range(4):
            row = i // 2
            col = i % 2
            
            # 创建数值标签
            value_label = self.sensor_labels[i]
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
            
            # 创建单个图表容器和布局
            single_chart_container = QWidget()
            chart_layout = QVBoxLayout()
            chart_layout.addWidget(QLabel(f"{self.sensor_names[i]} 当前值:"))
            chart_layout.addWidget(value_label)
            
            chart_view = QChartView()
            chart_view.setMinimumSize(350, 250)
            chart = QChart()
            chart.setTitle(f"{self.sensor_names[i]} 数据趋势")
            
            chart.setAnimationOptions(QChart.SeriesAnimations) # 启用图表动画效果
            chart.legend().hide()
            
            series = QLineSeries()
            series.setUseOpenGL(True)  # 启用GPU加速
            series.setColor(colors[i])
            chart.addSeries(series)
            
            axis_x = QValueAxis()
            axis_x.setTitleText("时间")
            axis_x.setRange(0, 100)
            
            axis_y = QValueAxis()
            axis_y.setTitleText("数值")
            axis_y.setRange(0, 100)
            
            chart.addAxis(axis_x, Qt.AlignBottom)
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_x)
            series.attachAxis(axis_y)
            
            chart_view.setChart(chart)
            chart_layout.addWidget(chart_view)
            single_chart_container.setLayout(chart_layout)
            
            # 将单个图表容器添加到主网格布局
            main_chart_layout.addWidget(single_chart_container, row, col)
            
            self.chart_views.append({
                'view': chart_view,    # 存储图表视图对象（用于显示）
                'series': series,      # 存储折线系列对象（用于更新数据点）
                'axis_x': axis_x,      # 存储X轴对象（可动态调整范围）
                'axis_y': axis_y       # 存储Y轴对象（可动态调整范围）
            })

        # 设置主图表容器布局
        chart_container.setLayout(main_chart_layout)
        
        # 组合所有组件
        main_layout.addWidget(connection_group)
        main_layout.addWidget(chart_container)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 连接信号
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        self.disconnect_btn.clicked.connect(self.signals.disconnect_clicked.emit)
        self.start_btn.clicked.connect(self.signals.start_clicked.emit)
        self.stop_btn.clicked.connect(self.signals.stop_clicked.emit)


    def _on_connect_clicked(self):
        """处理连接按钮点击事件"""
        host = self.host_input.text()
        try:
            port = int(self.port_input.text())
            self.signals.connect_clicked.emit(host, port)
        except ValueError:
            print("端口号必须是数字")

    def update_sensor_data(self, data: List[float]):
        """更新传感器数据显示"""
        for i, value in enumerate(data):
            self.sensor_labels[i].setText(f"{value:.2f}")
            
    def update_chart(self, data: List[float], time_index: int):
        """更新图表数据，每个传感器一个独立图表"""
        # 确保不会超出图表数量
        for i, value in enumerate(data):
            if i < len(self.chart_views):
                chart_data = self.chart_views[i]
                # 打印调试信息
                print(f"更新图表 {i+1}: 时间={time_index}, 值={value}")
                
                # 添加数据点
                chart_data['series'].append(time_index, value)
                
                # 自动调整X轴范围
                if time_index > chart_data['axis_x'].max():
                    chart_data['axis_x'].setRange(0, time_index + 10)
                
                # 自动调整Y轴范围（可选）
                current_min = chart_data['axis_y'].min()
                current_max = chart_data['axis_y'].max()
                if value < current_min:
                    chart_data['axis_y'].setMin(value - 10)
                if value > current_max:
                    chart_data['axis_y'].setMax(value + 10)

    def set_connected_state(self, connected: bool):
        """更新连接状态UI"""
        self.host_input.setEnabled(not connected)
        self.port_input.setEnabled(not connected)
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)
        self.start_btn.setEnabled(connected)
        self.stop_btn.setEnabled(False)

    def set_monitoring_state(self, monitoring: bool):
        """更新监测状态UI"""
        self.start_btn.setEnabled(not monitoring)
        self.stop_btn.setEnabled(monitoring)