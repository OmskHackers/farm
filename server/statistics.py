import json
import os
import sqlite3
import re
from time import sleep
from datetime import datetime, timedelta

from server import reloader
from server.config import CONFIG



def change_times(json_time,json_value):
    f = open('statistics.json', 'r+')
    json_string = ""
    parts = []

    for line in f.readlines():
        parts.append(line)

    start_part = parts[0]

    one_time_str = parts[1]
    two_time_str = parts[2]
    three_time_str = parts[3]
    four_time_str = parts[4]
    five_time_str = parts[5]
    six_time_str = parts[6]

    one_flags_str = parts[7]
    two_flags_str = parts[8]
    three_flags_str = parts[9]
    four_flags_str = parts[10]
    five_flags_str = parts[11]
    six_flags_str = parts[12]

    #end_part = parts[13]

    one_answer = one_time_str
    two_answer = two_time_str
    three_answer = three_time_str
    four_answer = four_time_str
    five_answer = five_time_str
    six_answer = six_time_str

    if json_time == 'one_time':
        start_of_part = one_time_str[0:15]
        changed_part = json_value + '",'
        end_of_part = one_time_str.split(',')[1]

        one_answer = start_of_part + changed_part + end_of_part

    if json_time == 'two_time':
        start_of_part = two_time_str[0:15]
        changed_part = json_value + '",'
        end_of_part = two_time_str.split(',')[1]

        two_answer = start_of_part + changed_part + end_of_part

    if json_time == 'three_time':
        start_of_part = three_time_str[0:17]
        changed_part = json_value + '",'
        end_of_part = three_time_str.split(',')[1]

        three_answer = start_of_part + changed_part + end_of_part

    if json_time == 'four_time':
        start_of_part = four_time_str[0:16]
        changed_part = json_value + '",'
        end_of_part = four_time_str.split(',')[1]

        four_answer = start_of_part + changed_part + end_of_part

    if json_time == 'five_time':
        start_of_part = five_time_str[0:16]
        changed_part = json_value + '",'
        end_of_part = five_time_str.split(',')[1]

        five_answer = start_of_part + changed_part + end_of_part

    if json_time == 'six_time':
        start_of_part = six_time_str[0:15]
        changed_part = json_value + '",'
        end_of_part = six_time_str.split(',')[1]

        six_answer = start_of_part + changed_part + end_of_part


    file_answer = start_part + one_answer + two_answer + three_answer + four_answer + five_answer + six_answer + one_flags_str + two_flags_str + three_flags_str + four_flags_str +five_flags_str +six_flags_str + '\n}'

    f.seek(0)
    f.write(file_answer)
    f.truncate()
    f.close()

def change_flags(json_flags,json_value):
    f = open('statistics.json', 'r+')
    json_string = ""
    parts = []

    for line in f.readlines():
        parts.append(line)

    start_part = parts[0]

    one_time_str = parts[1]
    two_time_str = parts[2]
    three_time_str = parts[3]
    four_time_str = parts[4]
    five_time_str = parts[5]
    six_time_str = parts[6]

    one_flags_str = parts[7]
    two_flags_str = parts[8]
    three_flags_str = parts[9]
    four_flags_str = parts[10]
    five_flags_str = parts[11]
    six_flags_str = parts[12]


    one_answer = one_flags_str
    two_answer = two_flags_str
    three_answer = three_flags_str
    four_answer = four_flags_str
    five_answer = five_flags_str
    six_answer = six_flags_str

    if json_flags == 'one_flags':
        start_of_part = one_flags_str[0:15]
        changed_part = json_value + ','
        end_of_part = one_flags_str.split(',')[1]

        one_answer = start_of_part + changed_part + end_of_part

    if json_flags == 'two_flags':
        start_of_part = two_flags_str[0:15]
        changed_part = json_value + ','
        end_of_part = two_flags_str.split(',')[1]

        two_answer = start_of_part + changed_part + end_of_part

    if json_flags == 'three_flags':
        start_of_part = three_flags_str[0:17]
        changed_part = json_value + ','
        end_of_part = three_flags_str.split(',')[1]

        three_answer = start_of_part + changed_part + end_of_part

    if json_flags == 'four_flags':
        start_of_part = four_flags_str[0:16]
        changed_part = json_value + ','
        end_of_part = four_flags_str.split(',')[1]

        four_answer = start_of_part + changed_part + end_of_part

    if json_flags == 'five_flags':
        start_of_part = five_flags_str[0:16]
        changed_part = json_value + ','
        end_of_part = five_flags_str.split(',')[1]

        five_answer = start_of_part + changed_part + end_of_part

    if json_flags == 'six_flags':
        start_of_part = six_flags_str[0:15]
        changed_part = json_value

        six_answer = start_of_part + changed_part

    file_answer =start_part + one_time_str + two_time_str + three_time_str + four_time_str + five_time_str + six_time_str + one_answer + two_answer + three_answer + four_answer + five_answer + six_answer + '\n}'

    f.seek(0)
    f.write(file_answer)
    f.truncate()
    f.close()

def get():

    need_init = not os.path.exists(db_filename)
    database = sqlite3.connect(db_filename)
    database.row_factory = sqlite3.Row

    return database

def query(sql, args=()):
    return get().execute(sql, args).fetchall()

db_filename = os.path.join(os.path.dirname(__file__), 'flags.sqlite')

def start_loop():
    if 'START_TIME' not in CONFIG:
        CONFIG['START_TIME'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
        with open('config.py', 'r') as f:
            content = f.read()

        content = re.sub(r'CONFIG\s*=\s*{', f"CONFIG = {{\n    'START_TIME': '{CONFIG['START_TIME']}',", content)

        with open('config.py', 'w') as f:
            f.write(content)

    print('Statistics')
    config = reloader.get_config()

    while(True):
        times_dict = {}

        for column in ['time']:
            rows = query('SELECT * FROM flags')
            times_dict[column] = [item[column] for item in rows]

        total_flags = 0
        normal_times = []

        for time in times_dict['time']:
            total_flags = total_flags + 1
            normal_times.append(datetime.fromtimestamp(time))

        flags = []
        times = []


        for item in set(normal_times):
            times.append(item)
            flags.append(normal_times.count(item))

        time_points = []

        #Сюда загружаться должен параметр конфига START_TIME
        point = datetime.strptime(config['START_TIME'], "%Y-%m-%d %H:%M:%S")
        flags_sum = 0
        flags_sums = []

        for loop in range(0,400):
            time_points.append(point)
            try:
                for index in range(0,flags.__len__()):
                    if times[index] < point + timedelta(seconds=config['ROUND_PERIOD']) and times[index] > point:
                        flags_sum = flags_sum +flags[index]
            except:
                pass
            flags_sums.append(flags_sum)
            flags_sum = 0
            point = point + timedelta(seconds=config['ROUND_PERIOD'])


        now_point = datetime.now()

        if flags.__len__() == 0:
            pass

        next_point = now_point

        for this_point in time_points:
            if now_point < this_point:
                next_point = this_point
                break

        six_point = next_point

        for this_point in reversed(time_points):
            if this_point < next_point:
                six_point = this_point
                change_flags('six_flags',str(flags_sums[time_points.index(this_point)]))
                change_times('six_time',str(this_point.strftime("%H:%M:%S")))
                break


        five_point = six_point

        for this_point in reversed(time_points):
            if this_point < six_point:
                five_point = this_point
                change_flags('five_flags',str(flags_sums[time_points.index(this_point)]))
                change_times('five_time', str(this_point.strftime("%H:%M:%S")))
                break

        four_point = five_point

        for this_point in reversed(time_points):
            if this_point < five_point:
                four_point = this_point
                change_flags('four_flags', str(flags_sums[time_points.index(this_point)]))
                change_times('four_time', str(this_point.strftime("%H:%M:%S")))
                break

        three_point = four_point

        for this_point in reversed(time_points):
            if this_point < four_point:
                three_point = this_point
                change_flags('three_flags',str(flags_sums[time_points.index(this_point)]))
                change_times('three_time', str(this_point.strftime("%H:%M:%S")))
                break

        two_point = three_point

        for this_point in reversed(time_points):
            if this_point < three_point:
                two_point = this_point
                change_flags('two_flags',str(flags_sums[time_points.index(this_point)]))
                change_times('two_time', str(this_point.strftime("%H:%M:%S")))
                break

        one_point = two_point

        for this_point in reversed(time_points):
            if this_point < two_point:
                one_point = this_point
                change_flags('one_flags',str(flags_sums[time_points.index(this_point)]))
                change_times('one_time', str(this_point.strftime("%H:%M:%S")))
                break

        sleep(config['GRAPHICS_REFRESH_INTERVAL'])


