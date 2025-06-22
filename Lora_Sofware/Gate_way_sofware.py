import sys
import serial
import serial.tools.list_ports
import datetime
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QFileDialog, QLabel, QComboBox, QSpinBox
)
from PyQt5.QtCore import QTimer

class LoRaMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoRa Gateway Data Logger")
        self.resize(700, 500)

        self.ser = None
        self.data = []
        self.last_save_time = {}
        self.sample_interval = 20  # mặc định 20 giây

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_data)

    def init_ui(self):
        layout = QVBoxLayout()

        # COM + Sample Time
        config_layout = QHBoxLayout()
        self.com_selector = QComboBox()
        self.refresh_com_ports()
        config_layout.addWidget(QLabel("COM Port:"))
        config_layout.addWidget(self.com_selector)

        self.sample_input = QSpinBox()
        self.sample_input.setRange(1, 3600)
        self.sample_input.setValue(20)
        config_layout.addWidget(QLabel("Sample time (s):"))
        config_layout.addWidget(self.sample_input)

        self.connect_btn = QPushButton("Kết nối")
        self.connect_btn.clicked.connect(self.connect_serial)
        config_layout.addWidget(self.connect_btn)

        layout.addLayout(config_layout)

        self.status_label = QLabel("Chưa kết nối COM")
        layout.addWidget(self.status_label)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['Node ID', 'Thời gian', 'Nhiệt độ (°C)', 'Độ ẩm (%)'])
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu Excel")
        save_btn.clicked.connect(self.save_excel)
        btn_layout.addWidget(save_btn)

        clear_btn = QPushButton("Xoá Dữ Liệu")
        clear_btn.clicked.connect(self.clear_data)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def refresh_com_ports(self):
        self.com_selector.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_selector.addItem(port.device)

    def connect_serial(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connect_btn.setText("Kết nối")
            self.status_label.setText("Đã ngắt kết nối")
            self.timer.stop()
            return

        try:
            port = self.com_selector.currentText()
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.sample_interval = self.sample_input.value()
            self.status_label.setText(f"Kết nối {port} thành công. Lấy mẫu mỗi {self.sample_interval}s")
            self.connect_btn.setText("Ngắt")
            self.timer.start(100)  # đọc COM mỗi 100ms
        except Exception as e:
            self.status_label.setText(f"Lỗi kết nối: {e}")

    def read_data(self):
        try:
            if not self.ser or not self.ser.is_open:
                return

            line = self.ser.readline().decode(errors='ignore').strip()
            if line.startswith("Node:"):
                parts = line.split(',')
                node = parts[0].split(':')[1].strip()
                temp = float(parts[1].split(':')[1].replace('C', '').strip())
                humi = float(parts[2].split(':')[1].replace('%', '').strip())
                now_dt = datetime.datetime.now()
                now_str = now_dt.strftime("%d/%m/%Y %H:%M:%S")

                last_time = self.last_save_time.get(node, None)
                if last_time is None or (now_dt - last_time).total_seconds() >= self.sample_interval:
                    self.data.append([node, now_str, temp, humi])
                    self.update_table(node, now_str, temp, humi)
                    self.last_save_time[node] = now_dt
                    self.status_label.setText(f"Đã ghi từ Node {node}")
                else:
                    wait = self.sample_interval - int((now_dt - last_time).total_seconds())
                    self.status_label.setText(f"Đã nhận từ Node {node}, chờ {wait}s")
        except Exception as e:
            self.status_label.setText(f"Lỗi: {e}")

    def update_table(self, node, timestamp, temp, humi):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(node)))
        self.table.setItem(row, 1, QTableWidgetItem(timestamp))
        self.table.setItem(row, 2, QTableWidgetItem(f"{temp:.1f}"))
        self.table.setItem(row, 3, QTableWidgetItem(f"{humi:.1f}"))

    def save_excel(self):
        if self.data:
            df = pd.DataFrame(self.data, columns=["Node ID", "Thời gian", "Nhiệt độ (°C)", "Độ ẩm (%)"])
            file_name, _ = QFileDialog.getSaveFileName(self, "Lưu file", "", "Excel (*.xlsx)")
            if file_name:
                df.to_excel(file_name, index=False)
                self.status_label.setText(f"Đã lưu vào {file_name}")

    def clear_data(self):
        self.data = []
        self.table.setRowCount(0)
        self.status_label.setText("Đã xoá dữ liệu")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoRaMonitor()
    window.show()
    sys.exit(app.exec_())
