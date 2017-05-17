from flask import request, render_template, jsonify, send_from_directory
import taglibro.config
from taglibro import app
from taglibro.taglibro import get_entry_list
import time
import markdown2
import datetime
import uuid
import os
import os.path

entry_cache = (None, datetime.datetime.now() - datetime.timedelta(days=30))
config = taglibro.config.get_config()


@app.route('/')
def home():
    return send_from_directory('static', 'taglibro.html')


@app.route('/entry', methods=['GET'])
def get_entries():
    entries = get_entry_list()  # get all entries, parsed and sorted

    # setup entries for front-end
    dispatch_entries = []
    for e in entries:
        header = {
                #    'date': e.date.strftime('%d-%m-%Y %H:%M'),
                  'date': e.date,
                  'tags': e.tags}
        start = time.time()
        body = {
            'txt': e.body,
            'markdown': markdown2.markdown(e.body)
        }

        de = {'header': header, 'body': body, 'uuid': str(uuid.uuid4())}
        dispatch_entries.append(de)

    return jsonify(dispatch_entries)


@app.route('/entry', methods=['POST'])
def post_entry():
    if request.json is None:
        return 'no data sent', 400

    now = datetime.datetime.now()

    # create year and folder directories
    base_dir = config['journal_paths'][0]
    year_folder = os.path.join(base_dir, str(now.year))

    month_str = str(now.day) if now.month >= 10 else '0' + str(now.month)
    month_folder = os.path.join(base_dir, str(now.year), month_str)
    if not os.path.exists(year_folder):
        os.mkdir(year_folder)
    if not os.path.exists(month_folder):
        os.mkdir(month_folder)

    # generate filename for entry
    ext = '.md'
    day_str = str(now.day) if now.day >= 10 else '0' + str(now.day)
    fn_date = '{}-{}-{}'.format(day_str, month_str, str(now.year))
    fn_base = os.path.join(month_folder, fn_date)
    num_ext = ''
    num = 1
    while os.path.exists(fn_base + num_ext + ext):
        num += 1
        num_ext = '_{}'.format(num)

    fn = fn_base + num_ext + ext
    entry_txt = request.json['body']

    # fn = os.path.join(month_folder, 'test.md')
    with open(fn, 'w') as f:
        f.write(entry_txt)

    print('wrote text:', entry_txt)
    print('wrote on ', fn)

    return 'OK', 200
