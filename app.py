import sys
import serial
import numpy as np
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

ser = serial.Serial('COM6', 9600, timeout=1)  

class AudioDevice(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: lightblue;")

        self.left_ear = []
        self.right_ear = []
        self.frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]
        self.freq_labels = ["125", "250", "500", "1000", "2000", "4000", "8000"]

        self.initUI()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_audiogram)
        self.timer.start(1000)

    def initUI(self):
        self.setWindowTitle("Audiogram Interface")
        self.showMaximized()

        self.fig, self.ax = plt.subplots(figsize=(1,1))
        self.ax.invert_yaxis()

        self.ax.set_title("Audiogram")
        self.ax.grid(True)
        self.ax.set_xlabel("Frequency [Hz]", fontsize=10)
        self.ax.set_xticks(range(len(self.frequencies)))
        self.ax.set_xticklabels(self.freq_labels, fontsize=8)
        self.ax.set_ylabel("Hearing threshold [dB]", fontsize=10)
        self.ax.set_yticks(np.arange(-10, 130, 10))
        self.ax.set_yticklabels([i for i in range(-10, 130, 10)], fontsize=8)

        self.canvas = FigureCanvas(self.fig)

        self.left_ear_line, = self.ax.plot([], [], marker='o', color='red', label='Left Ear')
        self.right_ear_line, = self.ax.plot([], [], marker='x', color='blue', label='Right Ear')
        self.ax.legend()

        save_button = QtWidgets.QPushButton("Save audiogram")
        save_button.clicked.connect(self.save_audiogram)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(save_button)

        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def parse_results(self, line):
        try:
            left_ear = []
            right_ear = []

            if "Left Ear:" in line:
                left_ear = [float(x.split("Hz,")[1].replace(" db", "")) for x in line.split(" | ")]
            elif "Right Ear:" in line:
                right_ear = [float(x.split("Hz,")[1].replace(" db", "")) for x in line.split(" | ")]

            return left_ear, right_ear
        except Exception as e:
            print(f"Error parsing data: {e}")
            return [], []

    def update_audiogram(self):
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if "Audiogram Results:" in line:
                self.left_ear, self.right_ear = [], []
            else:
                left, right = self.parse_results(line)
                self.left_ear.extend(left)
                self.right_ear.extend(right)
                if len(self.left_ear) == 7 and len(self.right_ear) == 7:
                    self.plot_audiogram(self.left_ear, self.right_ear)

    def plot_audiogram(self, left_ear, right_ear):
        # Update the data of the existing line objects
        self.left_ear_line.set_data(range(len(self.frequencies)), left_ear)
        self.right_ear_line.set_data(range(len(self.frequencies)), right_ear)
        self.canvas.draw()

    def save_audiogram(self):
        self.canvas.draw()

        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Audiogram As",
            "",
            "Images (*.png *.jpg)",
            options=options
        )

        if file_path:
            try:
                self.fig.savefig(file_path, format='png' if file_path.endswith('.png') else 'jpg')
                QtWidgets.QMessageBox.information(self, "Saved", f"Audiogram saved as: {file_path}")
            except Exception as e:
                # Display an error message if saving fails
                QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save audiogram: {e}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    audiodevice = AudioDevice()
    audiodevice.show()
    sys.exit(app.exec_())
