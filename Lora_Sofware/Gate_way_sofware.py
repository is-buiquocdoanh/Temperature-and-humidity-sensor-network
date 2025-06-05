import sys
import serial
import serial.tools.list_ports
import datetime
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QFileDialog, QLabel,
    QHBoxLayout, QComboBox
)
from PyQt5.QtCore import QTimer

class LoRaMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LoRa Gateway Data Logger")
        self.resize(700, 500)

        self.ser = None  # chưa kết nối
        self.data = []
        self.last_save_time = {}

        self.init_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_data)

    def init_ui(self):
        layout = QVBoxLayout()

        # Dòng chọn COM
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Chọn cổng COM:"))
        self.com_box = QComboBox()
        self.refresh_com_ports()
        port_layout.addWidget(self.com_box)

        self.connect_btn = QPushButton("Kết nối")
        self.connect_btn.clicked.connect(self.connect_com)
        port_layout.addWidget(self.connect_btn)

        layout.addLayout(port_layout)

        self.status_label = QLabel("Chưa kết nối")
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

        refresh_btn = QPushButton("Làm mới COM")
        refresh_btn.clicked.connect(self.refresh_com_ports)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def refresh_com_ports(self):
        self.com_box.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_box.addItem(port.device)

    def connect_com(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.ser = None
            self.connect_btn.setText("Kết nối")
            self.status_label.setText("Đã ngắt kết nối.")
            self.timer.stop()
            return

        port = self.com_box.currentText()
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            self.status_label.setText(f"Đã kết nối {port}")
            self.connect_btn.setText("Ngắt")
            self.timer.start(100)
        except Exception as e:
            self.status_label.setText(f"Lỗi kết nối: {e}")

    def read_data(self):
        if not self.ser or not self.ser.is_open:
            return

        try:
            line = self.ser.readline().decode(errors='ignore').strip()
            if line.startswith("NODE"):  # hoặc \"Node:\" tuỳ định dạng
                # Ví dụ: NODE99:28.3:65.4
                parts = line.replace("NODE", "").split(":")
                if len(parts) == 3:
                    node = parts[0].strip()
                    temp = float(parts[1])
                    humi = float(parts[2])
                    now_dt = datetime.datetime.now()
                    now_str = now_dt.strftime("%d/%m/%Y %H:%M:%S")

                    last_time = self.last_save_time.get(node, None)
                    if last_time is None or (now_dt - last_time).total_seconds() >= 20:
                        self.data.append([node, now_str, temp, humi])
                        self.update_table(node, now_str, temp, humi)
                        self.last_save_time[node] = now_dt
                        self.status_label.setText(f"Đã ghi mẫu từ Node {node}")
                    else:
                        wait = 20 - int((now_dt - last_time).total_seconds())
                        self.status_label.setText(f"Đã nhận từ Node {node}, chờ {wait}s")
        except Exception as e:
            self.status_label.setText(f"Lỗi đọc dữ liệu: {e}")

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
