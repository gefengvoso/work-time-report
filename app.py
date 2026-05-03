from flask import Flask, request, jsonify, render_template
import supabase_manager as em
from datetime import date

app = Flask(__name__)
em.init_excel()


@app.route('/')
def index():
    return render_template('index.html')


# ── Reports ───────────────────────────────────────────────────────────────────

@app.route('/api/reports')
def get_reports():
    date_str = request.args.get('date', date.today().isoformat())
    return jsonify(em.get_reports(date_str))


@app.route('/api/reports/range')
def get_reports_range():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end required'}), 400
    return jsonify(em.get_reports_range(start, end))


@app.route('/api/reports', methods=['POST'])
def add_report():
    data = request.json
    try:
        report = em.add_report(
            data['date'],
            data.get('project', ''),
            data.get('start_time', ''),
            data.get('end_time', ''),
            data.get('end_date') or None,
        )
        return jsonify(report), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    data = request.json
    result = em.update_report(
        report_id,
        data['date'],
        data.get('project', ''),
        data.get('start_time', ''),
        data.get('end_time', ''),
        data.get('end_date') or None,
    )
    if result is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(result)


@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    if em.delete_report(report_id):
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── Projects ──────────────────────────────────────────────────────────────────

@app.route('/api/projects')
def get_projects():
    return jsonify(em.get_projects())


@app.route('/api/projects', methods=['POST'])
def add_project():
    data = request.json
    return jsonify(em.add_project(data['name'])), 201


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.json
    result = em.update_project(
        project_id,
        data.get('name', ''),
        data.get('favorite', False),
        data.get('active', True),
    )
    if result is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(result)


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    if em.delete_project(project_id):
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── Holidays ──────────────────────────────────────────────────────────────────

@app.route('/api/holidays')
def get_holidays():
    return jsonify(em.get_holidays())


@app.route('/api/holidays', methods=['POST'])
def add_holiday():
    data = request.json
    return jsonify(em.add_holiday(data['date'], data['name'], data['quota_hours'])), 201


@app.route('/api/holidays/<int:holiday_id>', methods=['PUT'])
def update_holiday(holiday_id):
    data = request.json
    result = em.update_holiday(holiday_id, data['date'], data['name'], data['quota_hours'])
    if result is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(result)


@app.route('/api/holidays/<int:holiday_id>', methods=['DELETE'])
def delete_holiday(holiday_id):
    if em.delete_holiday(holiday_id):
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── Day Status ────────────────────────────────────────────────────────────────

@app.route('/api/day-statuses')
def get_day_statuses():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end required'}), 400
    return jsonify(em.get_day_statuses_range(start, end))


@app.route('/api/day-status')
def get_day_status():
    date_str = request.args.get('date', date.today().isoformat())
    return jsonify({'date': date_str, 'status': em.get_day_status(date_str)})


@app.route('/api/day-status', methods=['POST'])
def set_day_status():
    data = request.json
    em.set_day_status(data['date'], data['status'])
    return jsonify({'ok': True})


# ── Balance ───────────────────────────────────────────────────────────────────

@app.route('/api/balance')
def get_balance():
    date_str = request.args.get('date', date.today().isoformat())
    return jsonify(em.get_balance(date_str))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
