from flask import Flask, render_template, jsonify
import streamlit as st
import serial
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

def read_audiogram_data():
    ser = serial.Serial('COM6', 9600)  # Adjust the port to match your Arduino port
    ser.flushInput()

    left_ear_results = []
    right_ear_results = []

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(line)

                if "Left Ear Results" in line:
                    left_ear_results = list(map(int, ser.readline().decode('utf-8').strip().split(', ')))
                elif "Right Ear Results" in line:
                    right_ear_results = list(map(int, ser.readline().decode('utf-8').strip().split(', ')))
                    break
        except Exception as e:
            print(f"Error reading from Arduino: {e}")
            break

    return left_ear_results, right_ear_results

def plot_audiogram(left_ear, right_ear):
    frequencies = [125, 250, 500, 1000, 2000, 4000, 8000]
    left_ear_db = [x * 10 for x in left_ear]
    right_ear_db = [x * 10 for x in right_ear]

    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, left_ear_db, label="Left Ear", marker='o', color='r')
    plt.plot(frequencies, right_ear_db, label="Right Ear", marker='o', color='b')
    plt.gca().invert_yaxis()
    plt.title("Audiogram")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Hearing Level (dB)")
    plt.xticks(frequencies)
    plt.yticks(range(0, 130, 10))
    plt.grid(True)
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('ascii')
    plt.close()
    return img_base64

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_audiogram', methods=['GET'])
def get_audiogram():
    left_ear_results, right_ear_results = read_audiogram_data()
    audiogram_img = plot_audiogram(left_ear_results, right_ear_results)
    return jsonify({'img': audiogram_img})

if __name__ == "__main__":
    app.run(debug=True)
