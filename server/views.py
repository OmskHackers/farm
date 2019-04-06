import re
import time
import json
import requests

from datetime import datetime, timedelta
from flask import jsonify, render_template, request

from server import app, auth, database, reloader
from server.models import FlagStatus
from server import statistics



start_config = reloader.get_config()



@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)

@app.route('/<sploit_name>')
@auth.auth_required
def sploit(sploit_name):
    teams = start_config['TEAMS'].keys() #команды
    flags_per_time = [] #стыренные флаги по 6-ти временным промежуткам и по каждой тиме
    for i in range(0,len(teams)):
        flags_per_time.append(['0','0','0','0','0','0']) #инициализация стыренных флагов

    teams_info = []
    for i in range(0,len(teams)):
        teams_info.append([])

    for item in teams:

        rows = database.query('SELECT time FROM flags WHERE sploit=\'' + str(sploit_name) +'\' AND team=\''+item+'\' ')
        for row in rows:
            for r in row:
                teams_info[list(teams).index(item)].append(timestamp_to_datetime(r))

    time_points = []

    point = datetime.strptime(start_config['START_TIME'], "%Y-%m-%d %H:%M:%S")

    for loop in range(0, 400):
        time_points.append(point)
        point = point + timedelta(seconds=start_config['ROUND_PERIOD'])

    now_point = datetime.now()

    for this_point in time_points:
        if now_point < this_point:
            next_point = this_point
            break

    six_point = next_point

    time_six = ""

    for this_point in reversed(time_points):
        if this_point < next_point:
            six_point = this_point
            time_six = str(this_point.strftime("%Y-%m-%d %H:%M:%S"))
            break
    five_point = six_point
    time_five = ""

    for this_point in reversed(time_points):
        if this_point < six_point:
            five_point = this_point
            time_five = str(this_point.strftime("%Y-%m-%d %H:%M:%S"))
            break
    four_point = five_point
    time_four = ""

    for this_point in reversed(time_points):
        if this_point < five_point:
            four_point = this_point
            time_four = str(this_point.strftime("%Y-%m-%d %H:%M:%S"))
            break
    three_point = four_point
    time_three = ""

    for this_point in reversed(time_points):
        if this_point < four_point:
            three_point = this_point
            time_three = str(this_point.strftime("%Y-%m-%d %H:%M:%S"))
            break
    two_point = three_point
    time_two = ""

    for this_point in reversed(time_points):
        if this_point < three_point:
            two_point = this_point
            time_two = str(this_point.strftime("%Y-%m-%d %H:%M:%S"))
            break
    one_point = two_point
    time_one = ""

    for this_point in reversed(time_points):
        if this_point < two_point:
            one_point = this_point
            time_one = str(this_point.strftime("%Y-%m-%d %H:%M:%S"))
            break

    try:
        for i in range(0,len(teams)):

            six_flags = 0
            five_flags = 0
            four_flags = 0
            three_flags = 0
            two_flags = 0
            one_flags = 0

            for flag_time in teams_info[i]:
                #print(flag_time)
                if flag_time >= six_point:
                    six_flags += 1
                #print('флагов за 6й поинт :' + str(six_flags))
                elif flag_time >= five_point and flag_time < six_point:
                    five_flags += 1
                #print('флагов за 5й поинт :' + str(five_flags))
                elif flag_time >= four_point and flag_time < five_point:
                    four_flags += 1
                #print('флагов за 4й поинт :' + str(four_flags))
                elif flag_time >= three_point and flag_time < four_point:
                    three_flags += 1
                #print('флагов за 3й поинт :' + str(three_flags))
                elif flag_time >= two_point and flag_time < three_point:
                    two_flags += 1
                #print('флагов за 2й поинт :' + str(two_flags))
                elif flag_time >= one_point and flag_time < two_point:
                    one_flags += 1
                #print('флагов за 1й поинт :' + str(one_flags))

            flags_per_time[i][5] = str(six_flags)
            flags_per_time[i][4] = str(five_flags)
            flags_per_time[i][3] = str(four_flags)
            flags_per_time[i][2] = str(three_flags)
            flags_per_time[i][1] = str(two_flags)
            flags_per_time[i][0] = str(one_flags)
    except:
        pass


    for item in flags_per_time:
        item[0] = "time_1." + item[0]
        item[1] = "time_2." + item[1]
        item[2] = "time_3." + item[2]
        item[3] = "time_4." + item[3]
        item[4] = "time_5." + item[4]
        item[5] = "time_6." + item[5]


    d = dict(zip(teams,flags_per_time))

    html = "<html><head><title>" + str(sploit_name) + "</title><meta charset=\"utf-8\"><script src=\"static/js/jquery.min.js\"></script></head><body><table border=\"1\"> \
    <tr><th>" + str(sploit_name) + "</th><th>" + time_one[-9:] + "</th><th>" + time_two[-9:] + "</th><th>" + time_three[-9:] + "</th> \
<th>" + time_four[-9:] + "</th>,<th>" + time_five[-9:] + "</th>,<th>" + time_six[-9:] + "</th> </tr> """
    for time in d:
        html += "<tr><td>{}</td>".format(time)
        for state in "time_1", "time_2", "time_3", "time_4","time_5","time_6" :
            element = '<br>'.join(f for f in d[time] if "{}.".format(state) in f)
            try:
                if int(element[7:])>0:
                    html += "<td align=\"center\" bgcolor=\"#37b700\">{}</td>".format(element[7:])
                elif int(element[7:])==0:
                    html += "<td align=\"center\" bgcolor=\"#f40000\">{}</td>".format(element[7:])
                else:
                    html += "<td align=\"center\" >-</td>"
            except:
                html += "<td align=\"center\" >-</td>"


        html += "</tr>"
    html += "</table><script> setTimeout(function(){window.location.reload();}, 10000);</script></html>"
    return html


@app.route('/')
@auth.auth_required
def index():
    distinct_values = {}
    for column in ['sploit', 'status', 'team']:
        rows = database.query('SELECT DISTINCT {} FROM flags ORDER BY {}'.format(column, column))
        distinct_values[column] = [item[column] for item in rows]

    config = reloader.get_config()

    legend = 'Flag delivery statistics'

    f = open('statistics.json', 'r')
    json_string = ''
    for line in f.readlines():
        json_string = json_string + line
    f.close()
    statistics = json.loads(json_string)
    flags = [statistics['one_flags'], statistics['two_flags'], statistics['three_flags'], statistics['four_flags'],
             statistics['five_flags'], statistics['six_flags']]
    times = [statistics['one_time'], statistics['two_time'], statistics['three_time'], statistics['four_time'],
             statistics['five_time'], statistics['six_time']]
    refresh_interval = config['GRAPHICS_REFRESH_INTERVAL'] * 1000


    server_tz_name = time.strftime('%Z')
    if server_tz_name.startswith('+'):
        server_tz_name = 'UTC' + server_tz_name

    return render_template('index.html',
                           flag_format=config['FLAG_FORMAT'],
                           distinct_values=distinct_values,
                           server_tz_name=server_tz_name,
                           values=flags,
                           labels=times,
                           legend=legend,
                           refresh_interval=refresh_interval)


@app.route('/statistics')
@auth.auth_required
def statistics():
    legend = 'Flag delivery statistics'
    config = reloader.get_config()
    f = open('statistics.json', 'r')
    json_string = ''
    for line in f.readlines():
        json_string = json_string + line
    f.close()
    statistics = json.loads(json_string)
    flags = [statistics['one_flags'],statistics['two_flags'], statistics['three_flags'], statistics['four_flags'], statistics['five_flags'], statistics['six_flags']]
    times = [statistics['one_time'],statistics['two_time'], statistics['three_time'], statistics['four_time'], statistics['five_time'], statistics['six_time']]
    refresh_interval = config['GRAPHICS_REFRESH_INTERVAL'] * 1000
    return render_template('chart.html', values=flags, labels=times, legend=legend, refresh_interval=refresh_interval)

FORM_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
FLAGS_PER_PAGE = 30


@app.route('/ui/show_flags', methods=['POST'])
@auth.auth_required
def show_flags():
    conditions = []
    for column in ['sploit', 'status', 'team']:
        value = request.form[column]
        if value:
            conditions.append(('{} = ?'.format(column), value))
    for column in ['flag', 'checksystem_response']:
        value = request.form[column]
        if value:
            conditions.append(('INSTR(LOWER({}), ?)'.format(column), value))
    for param in ['time-since', 'time-until']:
        value = request.form[param].strip()
        if value:
            timestamp = round(datetime.strptime(value, FORM_DATETIME_FORMAT).timestamp())
            sign = '>=' if param == 'time-since' else '<='
            conditions.append(('time {} ?'.format(sign), timestamp))
    page_number = int(request.form['page-number'])
    if page_number < 1:
        raise ValueError('Invalid page-number')

    if conditions:
        chunks, values = list(zip(*conditions))
        conditions_sql = 'WHERE ' + ' AND '.join(chunks)
        conditions_args = list(values)
    else:
        conditions_sql = ''
        conditions_args = []

    sql = 'SELECT * FROM flags ' + conditions_sql + ' ORDER BY time DESC LIMIT ? OFFSET ?'
    args = conditions_args + [FLAGS_PER_PAGE, FLAGS_PER_PAGE * (page_number - 1)]
    flags = database.query(sql, args)

    sql = 'SELECT COUNT(*) FROM flags ' + conditions_sql
    args = conditions_args
    total_count = database.query(sql, args)[0][0]

    return jsonify({
        'rows': [dict(item) for item in flags],

        'rows_per_page': FLAGS_PER_PAGE,
        'total_count': total_count,
    })


@app.route('/ui/post_flags_manual', methods=['POST'])
@auth.auth_required
def post_flags_manual():
    config = reloader.get_config()
    flags = re.findall(config['FLAG_FORMAT'], request.form['text'])

    cur_time = round(time.time())
    rows = [(item, 'Manual', '*', cur_time, FlagStatus.QUEUED.name)
            for item in flags]

    db = database.get()
    db.executemany("INSERT OR IGNORE INTO flags (flag, sploit, team, time, status) "
                   "VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()

    return ''
