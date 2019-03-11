import re
import time
import json

from flask import jsonify, render_template, request

from server import app, auth, database, reloader
from server.models import FlagStatus


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


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
