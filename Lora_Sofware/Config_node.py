import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox
)

class ConfigSender(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cấu hình Node LoRa STM32")
        self.resize(350, 300)

        # Ngưỡng nhập
        self.tmax_input = QLineEdit("30")
        self.tmin_input = QLineEdit("25")
        self.hmax_input = QLineEdit("70")
        self.hmin_input = QLineEdit("40")
        self.interval_input = QLineEdit("10")

        # COM Port
        self.com_port = QComboBox()
        self.load_ports()

        # Giao diện
        layout = QVBoxLayout()
        layout.addLayout(self.row("COM Port", self.com_port))
        layout.addLayout(self.row("TMAX (°C)", self.tmax_input))
        layout.addLayout(self.row("TMIN (°C)", self.tmin_input))
        layout.addLayout(self.row("HMAX (%)", self.hmax_input))
        layout.addLayout(self.row("HMIN (%)", self.hmin_input))
        layout.addLayout(self.row("Chu kỳ đo (s)", self.interval_input))

        send_btn = QPushButton("Gửi cấu hình")
        send_btn.clicked.connect(self.send_config)
        layout.addWidget(send_btn)

        self.setLayout(layout)

    def row(self, label_text, widget):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        layout.addWidget(widget)
        return layout

    def load_ports(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_port.addItem(port.device)

    def send_config(self):
        try:
            port = self.com_port.currentText()
            ser = serial.Serial(port, 115200, timeout=1)

            # Đọc các giá trị nhập
            tmax = self.tmax_input.text()
            tmin = self.tmin_input.text()
            hmax = self.hmax_input.text()
            hmin = self.hmin_input.text()
            interval = self.interval_input.text()

            # Ghép chuỗi lệnh, THÊM \r\n
            cmd = f"SET:TMAX={tmax}:TMIN={tmin}:HMAX={hmax}:HMIN={hmin}:INTERVAL={interval}\r\n"
            ser.write(cmd.encode())
            ser.close()

            QMessageBox.information(self, "Thành công", "Đã gửi cấu hình:\n" + cmd)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Gửi thất bại: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigSender()
    window.show()
    sys.exit(app.exec_())
