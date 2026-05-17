import os
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import supabase_manager as em
from datetime import date
from auth import require_auth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'access_token' in session:
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        result = em.sign_in(email, password)
        if 'error' in result:
            error = 'אימייל או סיסמה שגויים'
        else:
            session['access_token'] = result['access_token']
            session['user_email'] = result['email']
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Main ──────────────────────────────────────────────────────────────────────

@app.route('/')
@require_auth
def index():
    return render_template('index.html')


# ── Reports ───────────────────────────────────────────────────────────────────

@app.route('/api/reports')
@require_auth
def get_reports():
    date_str = request.args.get('date', date.today().isoformat())
    return jsonify(em.get_reports(date_str))


@app.route('/api/reports/range')
@require_auth
def get_reports_range():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end required'}), 400
    return jsonify(em.get_reports_range(start, end))


@app.route('/api/reports', methods=['POST'])
@require_auth
def add_report():
    data = request.json
    try:
        report = em.add_report(
            data['date'],
            data.get('project', ''),
            data.get('start_time', ''),
            data.get('end_time', ''),
            data.get('end_date') or None,
            data.get('mission_code', ''),
            data.get('mission_description', ''),
        )
        return jsonify(report), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/<int:report_id>', methods=['PUT'])
@require_auth
def update_report(report_id):
    data = request.json
    result = em.update_report(
        report_id,
        data['date'],
        data.get('project', ''),
        data.get('start_time', ''),
        data.get('end_time', ''),
        data.get('end_date') or None,
        data.get('mission_code', ''),
        data.get('mission_description', ''),
    )
    if result is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(result)


@app.route('/api/reports/<int:report_id>', methods=['DELETE'])
@require_auth
def delete_report(report_id):
    if em.delete_report(report_id):
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── Projects ──────────────────────────────────────────────────────────────────

@app.route('/api/projects')
@require_auth
def get_projects():
    return jsonify(em.get_projects())


@app.route('/api/projects', methods=['POST'])
@require_auth
def add_project():
    data = request.json
    return jsonify(em.add_project(data['name'])), 201


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@require_auth
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
@require_auth
def delete_project(project_id):
    if em.delete_project(project_id):
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── Holidays ──────────────────────────────────────────────────────────────────

@app.route('/api/holidays')
@require_auth
def get_holidays():
    return jsonify(em.get_holidays())


@app.route('/api/holidays', methods=['POST'])
@require_auth
def add_holiday():
    data = request.json
    return jsonify(em.add_holiday(data['date'], data['name'], data['quota_hours'])), 201


@app.route('/api/holidays/<int:holiday_id>', methods=['PUT'])
@require_auth
def update_holiday(holiday_id):
    data = request.json
    result = em.update_holiday(holiday_id, data['date'], data['name'], data['quota_hours'])
    if result is None:
        return jsonify({'error': 'not found'}), 404
    return jsonify(result)


@app.route('/api/holidays/<int:holiday_id>', methods=['DELETE'])
@require_auth
def delete_holiday(holiday_id):
    if em.delete_holiday(holiday_id):
        return jsonify({'ok': True})
    return jsonify({'error': 'not found'}), 404


# ── Day Status ────────────────────────────────────────────────────────────────

@app.route('/api/day-statuses')
@require_auth
def get_day_statuses():
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end:
        return jsonify({'error': 'start and end required'}), 400
    return jsonify(em.get_day_statuses_range(start, end))


@app.route('/api/day-status')
@require_auth
def get_day_status():
    date_str = request.args.get('date', date.today().isoformat())
    return jsonify({'date': date_str, 'status': em.get_day_status(date_str)})


@app.route('/api/day-status', methods=['POST'])
@require_auth
def set_day_status():
    data = request.json
    em.set_day_status(data['date'], data['status'])
    return jsonify({'ok': True})


# ── Balance ───────────────────────────────────────────────────────────────────

@app.route('/api/balance')
@require_auth
def get_balance():
    date_str = request.args.get('date', date.today().isoformat())
    return jsonify(em.get_balance(date_str))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
