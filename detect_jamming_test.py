import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import subprocess
import sys
from collections import defaultdict
import shutil
import argparse

system_map = {
    'GPS': 'G',
    'Glonass': 'R',
    'BeiDou': 'C'
}


class RinexParser:
    def __init__(self, filename):
        self.filename = filename
        self.data = defaultdict(dict)
        self.systems = {'G': 'GPS', 'R': 'GLONASS', 'C': 'BeiDou'}

    def parse(self, start_delay=None, stop_delay=None, time=None):
        with open(self.filename, 'r') as f:
            lines = f.readlines()

        # Skip header
        for i, line in enumerate(lines):
            if "END OF HEADER" in line:
                lines = lines[i + 1:]
                break

        current_time = None
        start_time = None
        end_time = None
        first_epoch_time = None
        last_epoch_time = None

        # Сначала проходим по файлу, чтобы определить первый и последний временные метки
        for line in lines:
            if line.startswith('>'):
                parts = line[1:].split()
                hh, mm, ss = map(float, parts[3:6])
                time_str = f"{int(hh):02d}:{int(mm):02d}:{ss:05.2f}"
                if first_epoch_time is None:
                    first_epoch_time = datetime.strptime(time_str, "%H:%M:%S.%f")
                last_epoch_time = datetime.strptime(time_str, "%H:%M:%S.%f")

        # Устанавливаем границы обработки
        if start_delay is not None:
            start_time = first_epoch_time + timedelta(seconds=start_delay)
            if time is not None:
                potential_end = start_time + timedelta(seconds=time)
                end_time = min(potential_end, last_epoch_time) if stop_delay is None else \
                    min(potential_end, last_epoch_time - timedelta(seconds=stop_delay))
            elif stop_delay is not None:
                end_time = last_epoch_time - timedelta(seconds=stop_delay)
        elif stop_delay is not None:
            end_time = last_epoch_time - timedelta(seconds=stop_delay)

        # Основной парсинг данных
        for line in lines:
            if line.startswith('>'):
                parts = line[1:].split()
                hh, mm, ss = map(float, parts[3:6])
                current_time_str = f"{int(hh):02d}:{int(mm):02d}:{ss:05.2f}"
                current_time = datetime.strptime(current_time_str, "%H:%M:%S.%f")

                # Проверяем, нужно ли обрабатывать эту эпоху
                process_epoch = True
                if start_time and current_time < start_time:
                    process_epoch = False
                if end_time and current_time > end_time:
                    process_epoch = False

                if not process_epoch:
                    current_time = None
                    continue

                current_time = current_time_str

            elif current_time and line.strip():
                sat = line[:3].strip()
                obs = line[3:]

                try:
                    s1 = float(obs[32:48].strip())  # L1 SNR
                    self.data[current_time][f"{sat}_L1"] = s1
                except ValueError:
                    pass

                try:
                    s2 = float(obs[80:96].strip())  # L2 SNR
                    self.data[current_time][f"{sat}_L2"] = s2
                except ValueError:
                    pass

    def check_conditions(self, min_snr, min_sats, target_system=None, target_band=None, output_dir=None):
        if target_system and target_band:
            sys_code = system_map.get(target_system, 'G')
            band = f"_{target_band}"
            systems_to_check = {
                f"{target_system}_{target_band}": (sys_code, band)
            }
            print(f"\nChecking conditions: SNR ≥ {min_snr}, min {min_sats} satellites for {target_system} {target_band} only")
        else:
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
                    txt_file_path = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(self.filename))[0]}.txt')
                    with open(txt_file_path, 'a', encoding='utf-8') as file:
                        file.write(f"WARNING at {time} for {system_name}: {count} satellites (need {min_sats})\n")
                    problems += 1

        if problems == 0:
            print("\nLOG OK\n")
        else:
            print(f"\nTotal problems: {problems}\n")

    def calculate_average_snr(self, output_dir=None):
        stats = defaultdict(lambda: {'snr_sum': 0, 'snr_count': 0, 'sat_counts': []})
        
        for time, sats in self.data.items():
            temp_counts = defaultdict(int)
            
            for sat_key in sats:
                sys_code = sat_key[0]
                band = '_L1' if '_L1' in sat_key else '_L2'
                key = f"{sys_code}{band}"
                temp_counts[key] += 1
                
            for key, count in temp_counts.items():
                stats[key]['sat_counts'].append(count)
            
            for sat_key, snr in sats.items():
                sys_code = sat_key[0]
                band = '_L1' if '_L1' in sat_key else '_L2'
                key = f"{sys_code}{band}"
                
                if snr > 0:
                    stats[key]['snr_sum'] += snr
                    stats[key]['snr_count'] += 1

        result = {}
        for key, data in stats.items():
            avg_snr = data['snr_sum'] / data['snr_count'] if data['snr_count'] > 0 else 0
            avg_sats = sum(data['sat_counts']) / len(data['sat_counts']) if data['sat_counts'] else 0
            
            result[key] = {
                'avg_snr': avg_snr,
                'avg_sats': avg_sats
            }

        if output_dir:
            txt_file_path = os.path.join(output_dir, f'{os.path.splitext(os.path.basename(self.filename))[0]}_average_snr.txt')
            with open(txt_file_path, 'w', encoding='utf-8') as file:
                file.write("System Avg_SNR_dBHz Avg_Sat\n")    
                for key, values in sorted(result.items()):
                    sys_code = key[0]
                    band = key[1:]
                    system_name = self.systems.get(sys_code, 'Unknown')
                    file.write(f"{system_name}_{band} {round(values['avg_snr'],1)} {round(values['avg_sats'])}\n")    

        print("\nAverage statistics for each system:")
        print("System  Avg SNR (dBHz)  Avg Satellites")
        print("-------------------------------------")
        for key, values in sorted(result.items()):
            print(f"{key:<7} {values['avg_snr']:>12.1f} {values['avg_sats']:>15.0f}")

        return result

    def plot_snr(self, output_dir=None, target_system=None, target_band=None):
        if not output_dir:
            output_dir = os.path.splitext(os.path.basename(self.filename))[0]
            
        os.makedirs(output_dir, exist_ok=True)
        
        if target_system and target_band:
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
                        try:
                            temp_time = datetime.strptime(time_str, '%H:%M:%S.%f')
                        except ValueError:
                            h, m, s = time_str.split(':')
                            whole_sec, fraction_sec = s.split('.')
                            if int(whole_sec) == 60:
                                new_minute = int(m) + 1
                                new_time_str = f"{h}:{new_minute:02d}:00.{fraction_sec}"
                                temp_time = datetime.strptime(new_time_str, '%H:%M:%S.%f')

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

                base_name = os.path.splitext(os.path.basename(self.filename))[0]
                plot_file = os.path.join(output_dir, f"{sys_name}_{band}_SNR.png")
                plt.savefig(plot_file, dpi=150)
                if args.plot:
                    plt.show()
                plt.close()
                print(f"Saved {plot_file}")

    @staticmethod
    def archive_and_remove_directory(directory_name):
        archive_name = shutil.make_archive(directory_name, 'zip', directory_name)
        print(f"Directory archived as: {archive_name}")
        shutil.rmtree(directory_name)
        print(f"Directory removed: {directory_name}")

def main():
    parser = argparse.ArgumentParser(description="Обработка файла и параметров для скрипта detect_jamming_test.py")
    
    parser.add_argument('name_file', type=str, help="Имя файла для обработки")
    parser.add_argument('min_snr', type=float, help="Минимальный SNR")
    parser.add_argument('min_sats', type=int, help="Минимальное количество спутников")
    parser.add_argument('--system', type=str, help="Целевая система (например, GPS)", default=None)
    parser.add_argument('--band', type=str, help="Целевой диапазон (например, L1)", default=None)
    parser.add_argument('--archive', action='store_true', help="Нужно ли архивировать папку")
    parser.add_argument('--plot', action='store_true', help="Флаг для указания, нужно ли строить график")
    parser.add_argument('--start_delay', type=int, help="Время задержки начала обработки, сек", default=None)
    parser.add_argument('--stop_delay', type=int, help="Время задержки конца обработки, сек", default=None)
    parser.add_argument('--time', type=int, help="Время продолжительности обработки, сек", default=None)


    
    return parser.parse_args()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python detect_jamming_test.py input_file min_snr min_sats [--system SYSTEM] [--band BAND] [--archive] [--plot] [--start_delay]")
        print("Example: python3 detect_jamming_test.py test_tau1312.cyno 30 5")
        sys.exit(1)
    
    # Parse arguments
    args = main()
    
    int_name_file = os.path.splitext(args.name_file)[0]
    obs_file = f"{int_name_file}.obs"
    
    is_windows = os.name == 'nt'
    convbin_command = "convbin.exe" if is_windows else "convbin"
    
    subprocess.call(f"{convbin_command} {args.name_file} -o {obs_file} -os -r ubx", shell=True)
    if not os.path.exists(obs_file):
        subprocess.call(f"{convbin_command} {args.name_file} -o {obs_file} -os -r rtcm3", shell=True)

    os.makedirs(int_name_file, exist_ok=True)

    # Clear existing txt file
    txt_file_path = os.path.join(int_name_file, f'{int_name_file}.txt')
    txt2_file_path = os.path.join(int_name_file, f'{int_name_file}_average_snr.txt')
    if os.path.exists(txt_file_path):
        os.remove(txt_file_path)
    if os.path.exists(txt2_file_path):
        os.remove(txt2_file_path)

    parser = RinexParser(obs_file)
    parser.parse(args.start_delay, args.stop_delay, args.time)
    parser.check_conditions(args.min_snr, args.min_sats, args.system, args.band, int_name_file)
    parser.calculate_average_snr(int_name_file)
    parser.plot_snr(int_name_file, target_system=args.system, target_band=args.band)
    
    # Clear obs file
    if os.path.exists(obs_file):
        os.remove(obs_file)
        
    if args.archive:
        RinexParser.archive_and_remove_directory(int_name_file)