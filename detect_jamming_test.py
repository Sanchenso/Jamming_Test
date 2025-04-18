import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import subprocess
import sys
from collections import defaultdict
import shutil

system_map = {
    'GPS': 'G',
    'Glonass': 'R',
    'BeiDou': 'C'
}

name_file = sys.argv[1]
min_snr = float(sys.argv[2])
min_sats = int(sys.argv[3])
target_system = sys.argv[4] if len(sys.argv) > 4 else None
target_band = sys.argv[5] if len(sys.argv) > 5 else None
int_name_file, ext_name_file = os.path.splitext(name_file)
obsFile = int_name_file + '.obs'


class RinexParser:
    def __init__(self, filename):
        self.filename = filename
        self.data = defaultdict(dict)
        self.systems = {'G': 'GPS', 'R': 'GLONASS', 'C': 'BeiDou'}

    def parse(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        # Skip header
        for i, line in enumerate(lines):
            if "END OF HEADER" in line:
                lines = lines[i + 1:]
                break

        current_time = None
        for line in lines:
            if line.startswith('>'):
                parts = line[1:].split()
                hh, mm, ss = map(float, parts[3:6])
                current_time = f"{int(hh):02d}:{int(mm):02d}:{ss:05.2f}"
            elif current_time and line.strip():
                sat = line[:3].strip()  # G01, R02, etc.
                obs = line[3:]

                try:
                    s1 = float(obs[32:48].strip())  # L1 SNR
                    self.data[current_time][f"{sat}_L1"] = s1
                except:
                    pass

                try:
                    s2 = float(obs[80:96].strip())  # L2 SNR
                    self.data[current_time][f"{sat}_L2"] = s2
                except:
                    pass

    def check_conditions(self, min_snr, min_sats, target_system=None, target_band=None, output_dir=int_name_file):
        if target_system and target_band:
            # Проверяем только указанную систему и диапазон
            sys_code = system_map.get(target_system, 'G')  # По умолчанию GPS
            band = f"_{target_band}"
            systems_to_check = {
                f"{target_system}_{target_band}": (sys_code, band)
            }
            print(
                f"\nChecking conditions: SNR ≥ {min_snr}, min {min_sats} satellites for {target_system} {target_band} only")
        else:
            # Проверяем все системы
            systems_to_check = {
                'GPS_L1': ('G', '_L1'),
                'GPS_L2': ('G', '_L2'),
                'Glonass_L1': ('R', '_L1'),
                'Glonass_L2': ('R', '_L2'),
                'BeiDou_L1': ('C', '_L1'),
                'BeiDou_L2': ('C', '_L2')
            }
            print(f"\nChecking conditions: SNR ≥ {min_snr}, min {min_sats} satellites for all systems/bands")

        problems = 0

        present_systems = set()
        for sats in self.data.values():
            for sat_key in sats:
                sys_code = sat_key[0]
                band = '_L1' if '_L1' in sat_key else '_L2'
                present_systems.add(f"{sys_code}{band}")

        for time, sats in self.data.items():
            for system_name, (sys_code, band) in systems_to_check.items():
                if f"{sys_code}{band}" not in present_systems:
                    continue

                count = sum(1 for sat_key in sats
                            if sat_key.startswith(sys_code)
                            and sat_key.endswith(band)
                            and sats[sat_key] >= min_snr)

                if count < min_sats:
                    print(f"WARNING at {time} for {system_name}: {count} satellites (need {min_sats})")
                    txt_file_path = os.path.join(int_name_file, f'{int_name_file}.txt')
                    with open(txt_file_path, 'a', encoding='utf-8') as file:
                        file.write(f"WARNING at {time} for {system_name}: {count} satellites (need {min_sats})\n")
                    problems += 1

        if problems == 0:
            print("\nLOG OK\n")
        else:
            print(f"\nTotal problems: {problems}\n")

    def save_csv(self, output_dir=int_name_file):
        os.makedirs(output_dir, exist_ok=True)
        for system in self.systems:
            for band in ['L1', 'L2']:
                # Prepare data for system, band
                sys_data = {}
                for time, sats in self.data.items():
                    row = {}
                    for sat, snr in sats.items():
                        if sat.startswith(system) and sat.endswith(band):
                            row[sat.split('_')[0]] = int(round(snr))
                    if row:
                        sys_data[time] = row

                if not sys_data:
                    continue

                df = pd.DataFrame.from_dict(sys_data, orient='index')
                df.index.name = 'Time'
                df.sort_index(inplace=True)

                csv_file = os.path.join(output_dir, f"{int_name_file}_{self.systems[system]}_{band}.csv")
                df.to_csv(csv_file, sep=' ')
                print(f"Saved {csv_file}")

    def plot_snr(self, int_name_file, target_system=None, target_band=None):
        os.makedirs(int_name_file, exist_ok=True)
        if target_system and target_band:
            system_map = {'GPS': 'G', 'Glonass': 'R', 'BeiDou': 'C'}
            sys_code = system_map.get(target_system, 'G')
            bands = [f"_{target_band}"]
            systems = [(sys_code, target_system)]
            print(f"\nPlotting SNR for {target_system} {target_band} only")
        else:
            systems = [('G', 'GPS'), ('R', 'GLONASS'), ('C', 'BeiDou')]
            bands = ['_L1', '_L2']
            print("\nPlotting SNR for all systems/bands")

        for sys_code, sys_name in systems:
            for band_suffix in bands:
                band = band_suffix[1:]
                plot_data = {}

                for time_str, sats in self.data.items():
                    try:
                        # Обработка времени (исправление 60 секунд)
                        try:
                            temp_time = datetime.strptime(time_str, '%H:%M:%S.%f')
                        except ValueError:
                            h, m, s = time_str.split(':')
                            whole_sec, fraction_sec = s.split('.')
                            if int(whole_sec) == 60:
                                new_minute = int(m) + 1
                                new_time_str = f"{h}:{new_minute:02d}:00.{fraction_sec}"
                                temp_time = datetime.strptime(new_time_str, '%H:%M:%S.%f')

                        # Собираем данные для построения
                        for sat, snr in sats.items():
                            if sat.startswith(sys_code) and sat.endswith(band_suffix):
                                prn = sat.split('_')[0]
                                if prn not in plot_data:
                                    plot_data[prn] = {'time': [], 'snr': []}
                                plot_data[prn]['time'].append(temp_time)
                                plot_data[prn]['snr'].append(snr)

                    except Exception as e:
                        print(f"Error processing time {time_str}: {e}")
                        continue

                if not plot_data:
                    print(f"No data found for {sys_name} {band}")
                    continue

                # Создаем график
                plt.figure(figsize=(12, 6))
                ax = plt.gca()
                time_format = mdates.DateFormatter('%H:%M:%S')
                ax.xaxis.set_major_formatter(time_format)

                for prn, data in sorted(plot_data.items()):
                    plt.plot(data['time'], data['snr'], '-', label=prn)

                plt.title(f"{sys_name} {band} SNR", fontsize=14)
                plt.xlabel('Time', fontsize=14)
                plt.ylabel('SNR, dBHz', fontsize=14)
                plt.grid(color='black', linestyle='--', linewidth=0.2)
                plt.ylim(10, 60)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()

                # Сохраняем график
                plot_file = os.path.join(int_name_file, f"{sys_name}_{band}_SNR.png")
                plt.savefig(plot_file, dpi=200)
                plt.show()
                plt.close()
                print(f"Saved {plot_file}")

    def archive_and_remove_directory(int_name_file, directory_name):
        archive_name = shutil.make_archive(directory_name, 'zip', directory_name)
        print(f"Directory archived as: {archive_name}")
        shutil.rmtree(directory_name)
        print(f"Directory removed: {directory_name}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python parser.py input.obs min_snr min_sats")
        sys.exit(1)

    is_windows = os.name == 'nt'
    convbin_command = "convbin.exe" if is_windows else "convbin"
    commandUBX = f"{convbin_command} {name_file} -o {obsFile} -os -r ubx"
    commandRTCM = f"{convbin_command} {name_file} -o {obsFile} -os -r rtcm3"
    subprocess.call(commandUBX, shell=True)
    if not os.path.exists(obsFile):
        subprocess.call(commandRTCM, shell=True)
    txt_file_path = os.path.join(int_name_file, f'{int_name_file}.txt')
    if os.path.exists(txt_file_path):
        os.remove(txt_file_path)

    if len(sys.argv) < 5 or (target_system in system_map and (target_band == 'L1' or target_band == 'L2')):
        parser = RinexParser(obsFile)
        parser.parse()
        # parser.save_csv()
        os.makedirs(int_name_file, exist_ok=True)
        parser.check_conditions(min_snr, min_sats, target_system, target_band)
        parser.plot_snr(int_name_file, target_system=target_system, target_band=target_band)
        os.remove(obsFile)
        parser.archive_and_remove_directory(int_name_file)
    else:
        print('Error name system. Pls choose:')
        print(' GPS L1')
        print(' GPS L2')
        print(' Glonass L1')
        print(' Glonass L2')
        print(' BeiDou L1')
        print(' BeiDou L2')
