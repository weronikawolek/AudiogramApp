import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import filedialog
import serial
import time
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

try:
    ser = serial.Serial('COM6', 9600, timeout=1)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    ser = None

class AudiogramApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.left_ear = []
        self.right_ear = []
        self.frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]
        self.calibration_sent = False

        self.title("AudiogramApp")
        self.geometry("600x400")
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.title_label = ctk.CTkLabel(self.top_frame, text="AudiogramApp", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.restart_button = ctk.CTkButton(self.top_frame, text="Restart", command=self.restartTest)
        self.restart_button.grid(row=0, column=1, padx=950, pady=5, sticky="ew")

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nswe")
        self.left_frame.columnconfigure(0, weight=1)

        self.technician_frame = ctk.CTkFrame(self.left_frame)
        self.technician_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self.option_menu = ctk.CTkOptionMenu(self.technician_frame, values=["Technician 1", "Technician 2"])
        self.option_menu.set("Technician")
        self.option_menu.grid(row=0, column=0, padx=10, pady=5)

        self.calibration_frame = ctk.CTkFrame(self.left_frame)
        self.calibration_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.calibration_label = ctk.CTkLabel(self.calibration_frame, text="Calibration", font=("Arial", 14, "bold"))
        self.calibration_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        self.calibration_var = ctk.StringVar(value="Default")

        self.calibration_options = [
            ctk.CTkRadioButton(self.calibration_frame, text="Default", variable=self.calibration_var, value=1, command=self.selectCalibration),
            ctk.CTkRadioButton(self.calibration_frame, text="Ear 3A", variable=self.calibration_var, value=2, command=self.selectCalibration),
            ctk.CTkRadioButton(self.calibration_frame, text="TDH 39", variable=self.calibration_var, value=3, command=self.selectCalibration),
            ctk.CTkRadioButton(self.calibration_frame, text="Biological", variable=self.calibration_var, value=4, command=self.selectCalibration),
        ]

        for i, option in enumerate(self.calibration_options):
            option.grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")

        self.patient_data_frame = ctk.CTkFrame(self.left_frame)
        self.patient_data_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.patient_data_label = ctk.CTkLabel(self.patient_data_frame, text="Patient", font=("Arial", 14, "bold"))
        self.patient_data_label.grid(row=0, column=0, padx=10, pady=(10, 5))

        self.name_entry = ctk.CTkEntry(self.patient_data_frame, placeholder_text="Firstname")
        self.name_entry.grid(row=1, column=0, padx=10, pady=5)

        self.surname_entry = ctk.CTkEntry(self.patient_data_frame, placeholder_text="Lastname")
        self.surname_entry.grid(row=2, column=0, padx=10, pady=5)

        self.age_entry = ctk.CTkEntry(self.patient_data_frame, placeholder_text="Age")
        self.age_entry.grid(row=3, column=0, padx=10, pady=5)

        self.date_entry = ctk.CTkEntry(self.patient_data_frame, placeholder_text="Date")
        self.date_entry.grid(row=4, column=0, padx=10, pady=5)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.date_entry.configure(state="readonly")

        self.tabview = ctk.CTkTabview(self, width=500, height=800)
        self.tabview.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.tabview.rowconfigure(0, weight=1)
        self.tabview.columnconfigure(0, weight=1)

        self.audiogram_tab = self.tabview.add("Audiogram")
        self.result_tab = self.tabview.add("Result")

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.invert_yaxis()
        self.ax.set_title("Audiogram")
        self.ax.grid(True)
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_xticks(range(len(self.frequencies)))
        self.ax.set_xticklabels([str(freq) for freq in self.frequencies])
        self.ax.set_ylabel("Hearing Threshold [dB]")
        self.ax.set_yticks(np.arange(-10, 130, 10))

        self.left_ear_line, = self.ax.plot([], [], marker='o', color='red', label='Left Ear')
        self.right_ear_line, = self.ax.plot([], [], marker='x', color='blue', label='Right Ear')
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.audiogram_tab)
        self.canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.result_textbox = ctk.CTkTextbox(self.result_tab, width=500, height=400)
        self.result_textbox.pack(padx=10, pady=10, fill=ctk.BOTH, expand=True)

        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.bottom_frame.columnconfigure((0, 1, 2), weight=1)

        self.start_button = ctk.CTkButton(self.bottom_frame, text="Start", command=self.startAudiogram)
        self.start_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.save_button = ctk.CTkButton(self.bottom_frame, text="Save", command=self.saveAudiogram)
        self.save_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.open_button = ctk.CTkButton(self.bottom_frame, text="Open", command=self.openAudiogram)
        self.open_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

    def selectCalibration(self):
        calibration_value = self.calibration_var.get()
        print(f"Selected calibration: {calibration_value}")
        self.calibration_value = calibration_value

    def sendCalibrationToArduino(self):
        if ser and ser.is_open:
            try:
                calibration_value = self.calibration_value
                ser.write(str(calibration_value).encode())
                print(f"Sent calibration value {calibration_value} to Arduino.")
            except Exception as e:
                print(f"Error sending calibration to Arduino: {e}")

    def parseResults(self, line):
        try:
            if "Left ear:" in line:
                left_ear = [float(x.split("Hz,")[1].replace(" db", "").strip()) for x in line.split(" | ") if
                            "Hz," in x]
                print(f"Parsed left ear: {left_ear}")
                return left_ear, []
            elif "Right ear:" in line:
                right_ear = [float(x.split("Hz,")[1].replace(" db", "").strip()) for x in line.split(" | ") if
                             "Hz," in x]
                print(f"Parsed right ear: {right_ear}")
                return [], right_ear
            else:
                return [], []
        except Exception as e:
            print(f"Error parsing data: {e}")
            return [], []

    def updateResultText(self):
        if self.left_ear and self.right_ear:
            result_text = "Hearing Thresholds:\n\n"
            result_text += "Left Ear:\n"
            for freq, value in zip(self.frequencies, self.left_ear):
                result_text += f"  {freq} Hz: {value} dB\n"

            result_text += "\nRight Ear:\n"
            for freq, value in zip(self.frequencies, self.right_ear):
                result_text += f"  {freq} Hz: {value} dB\n"

            self.result_textbox.delete("1.0", ctk.END)
            self.result_textbox.insert(ctk.END, result_text)
        else:
            self.result_textbox.delete("1.0", ctk.END)
            self.result_textbox.insert(ctk.END, "No results available yet.\n")

    def startAudiogram(self):
        if not self.calibration_sent:
            self.sendCalibrationToArduino()
            self.calibration_sent = True

        if ser and ser.in_waiting > 0:
            try:
                line = ser.readline().decode().strip()
                print(f"Received: {line}")

                if "Audiogram Results:" in line:
                    self.left_ear, self.right_ear = [], []

                left, right = self.parseResults(line)
                self.left_ear.extend(left)
                self.right_ear.extend(right)

                if len(self.left_ear) == len(self.frequencies) and len(self.right_ear) == len(self.frequencies):
                    self.plotAudiogram(self.left_ear, self.right_ear)

            except Exception as e:
                print(f"Error reading serial data: {e}")

        self.after(1000, self.startAudiogram)

    def plotAudiogram(self, left_ear, right_ear):
        print(f"Plotting left ear: {left_ear}, right ear: {right_ear}")
        self.left_ear_line.set_data(range(len(self.frequencies)), left_ear)
        self.right_ear_line.set_data(range(len(self.frequencies)), right_ear)
        self.canvas.draw()
        self.updateResultText()

    def saveAudiogram(self):
        file_path = ctk.filedialog.asksaveasfilename(
            initialdir="W:/IBM/PI/Wyniki",
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                file_format = 'png' if file_path.endswith('.png') else 'jpg'
                self.fig.savefig(file_path, format=file_format)
                print(f"Audiogram saved as: {file_path}")

                csv_path = file_path.rsplit('.', 1)[0] + '.csv'

                patient_name = self.name_entry.get().strip()
                patient_surname = self.surname_entry.get().strip()
                patient_age = self.age_entry.get().strip()
                test_date = self.date_entry.get().strip()

                with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(['Patient Data'])
                    csv_writer.writerow(['Firstname', 'Lastname', 'Age', 'Date'])
                    csv_writer.writerow([patient_name, patient_surname, patient_age, test_date])
                    csv_writer.writerow([])

                    csv_writer.writerow(['Audiogram Results'])
                    csv_writer.writerow(['Frequency (Hz)', 'Left Ear (dB)', 'Right Ear (dB)'])
                    for freq, left, right in zip(self.frequencies, self.left_ear, self.right_ear):
                        csv_writer.writerow([freq, left, right])

                print(f"Audiogram data saved as: {csv_path}")

            except Exception as e:
                print(f"Failed to save audiogram: {e}")

    def openAudiogram(self):
        file_path = filedialog.askopenfilename(
            initialdir="W:/IBM/PI/Wyniki",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, mode='r', encoding='utf-8') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    data_section = None
                    patient_data = {}
                    audiogram_data = {'Left Ear': [], 'Right Ear': []}

                    for row in csv_reader:
                        if not row or len(row) == 0:
                            continue

                        if "Patient Data" in row[0]:
                            data_section = "patient"
                            continue
                        elif "Audiogram Results" in row[0]:
                            data_section = "audiogram"
                            continue

                        if data_section == "patient":
                            if len(row) >= 5 and row[0] == "Firstname":
                                patient_data['Firstname'] = row[1]
                                patient_data['Lastname'] = row[2]
                                patient_data['Age'] = row[3]
                                patient_data['Date'] = row[4]

                        elif data_section == "audiogram":
                            if len(row) >= 3:
                                try:
                                    freq = int(row[0])
                                    left = float(row[1])
                                    right = float(row[2])
                                    audiogram_data['Left Ear'].append(left)
                                    audiogram_data['Right Ear'].append(right)
                                except ValueError as e:
                                    print(f"Error parsing row in audiogram data: {row}, error: {e}")

                    if 'Firstname' in patient_data:
                        self.name_entry.delete(0, ctk.END)
                        self.name_entry.insert(0, patient_data.get('Firstname', ''))

                    if 'Lastname' in patient_data:
                        self.surname_entry.delete(0, ctk.END)
                        self.surname_entry.insert(0, patient_data.get('Lastname', ''))

                    if 'Age' in patient_data:
                        self.age_entry.delete(0, ctk.END)
                        self.age_entry.insert(0, patient_data.get('Age', ''))

                    if 'Date' in patient_data:
                        self.date_entry.delete(0, ctk.END)
                        self.date_entry.insert(0, patient_data.get('Date', ''))

                    if len(audiogram_data['Left Ear']) == len(self.frequencies) and len(audiogram_data['Right Ear']) == len(self.frequencies):
                        self.left_ear = audiogram_data['Left Ear']
                        self.right_ear = audiogram_data['Right Ear']
                        self.plotAudiogram(self.left_ear, self.right_ear)
                    else:
                        print("Audiogram data is incomplete or mismatched.")

            except Exception as e:
                print(f"Error loading audiogram file: {e}")

    def restartTest(self):
        if ser and ser.is_open:
            try:
                ser.setDTR(False)
                time.sleep(0.1)
                ser.setDTR(True)
                print("Arduino reset via DTR toggle.")
            except Exception as e:
                print(f"Error resetting Arduino: {e}")

        self.left_ear = []
        self.right_ear = []
        self.ax.clear()
        self.ax.invert_yaxis()
        self.ax.set_title("Audiogram")
        self.ax.grid(True)
        self.ax.set_xlabel("Frequency [Hz]")
        self.ax.set_xticks(range(len(self.frequencies)))
        self.ax.set_xticklabels([str(freq) for freq in self.frequencies])
        self.ax.set_ylabel("Hearing Threshold [dB]")
        self.ax.set_yticks(np.arange(-10, 130, 10))
        self.left_ear_line, = self.ax.plot([], [], marker='o', color='red', label='Left Ear')
        self.right_ear_line, = self.ax.plot([], [], marker='x', color='blue', label='Right Ear')
        self.ax.legend()
        self.canvas.draw()

        self.updateResultText()

        self.name_entry.delete(0, ctk.END)
        self.surname_entry.delete(0, ctk.END)
        self.age_entry.delete(0, ctk.END)

        print("Test restarted.")

if __name__ == "__main__":
    app = AudiogramApp()
    app.mainloop()
