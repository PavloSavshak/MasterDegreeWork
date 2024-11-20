# Підключення необхідних бібліотек 
import serial
import csv
from datetime import datetime, timedelta

# Встановлення відповідного порта та швидкості передачі даних
arduino_port = 'COM5'
baud_rate = 9600

# Відкриття порту
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

# Створення файлів для запису даних
file_paths = ['temperature_data_1day.csv', 'temperature_data_3days.csv', 'temperature_data_5days.csv']
files = [open(file_path, 'w', newline='') for file_path in file_paths]
csv_writers = [csv.writer(file) for file in files]

# Ініціалізація заголовків CSV-файлів
for writer in csv_writers:
    writer.writerow(['Timestamp', 'Temperature'])

# Встановлення часу завершення для кожного файлу
end_times = [
    datetime.now() + timedelta(seconds=10),  # для 1 хвилини
    datetime.now() + timedelta(seconds=20),  # для 2 хвилин
    datetime.now() + timedelta(seconds=30)   # для 3 хвилин
]

# Список для перевірки закритих файлів
files_closed = [False, False, False]

while True:
    # Перевірка, чи завершено час для всіх файлів
    all_files_closed = True
    for i, end_time in enumerate(end_times):
        if datetime.now() < end_time and not files_closed[i]:
            all_files_closed = False

    if all_files_closed:
        print("="*50)
        print("Час завершення виконання для всіх файлів досягнуто.")
        print("="*50)
        break

    # Очистити буфер порту
    ser.flushInput()

    # Отримати рядок даних від Arduino
    line = ser.readline().decode('utf-8').rstrip()

    # Перевірити, чи отримано коректний рядок даних
    if line.startswith('Outhouse: '):
        temperature = line.split(':')[1].strip()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, Temperature: {temperature}")

        # Записати дані в усі активні CSV-файли
        for i, end_time in enumerate(end_times):
            if datetime.now() < end_time:  # Якщо час для файлу ще не закінчився
                csv_writers[i].writerow([current_time, temperature])
                files[i].flush()  # Забезпечення того, що дані будуть записані відразу
            elif not files_closed[i]:  # Якщо час закінчився і файл ще не закрито
                print("="*50)
                print(f"Файл {file_paths[i]} сформовано.")
                print("="*50)
                files_closed[i] = True  # Помітити файл як закритий

# Закрити файли та послідовний порт при завершенні роботи
for file in files:
    file.close()
ser.close()
