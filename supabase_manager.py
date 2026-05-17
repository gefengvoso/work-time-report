import os
from datetime import date, datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ['SUPABASE_URL']
        key = os.environ['SUPABASE_KEY']
        _client = create_client(url, key)
    return _client


def init_excel():
    pass


def sign_in(email, password):
    try:
        res = _get_client().auth.sign_in_with_password({'email': email, 'password': password})
        return {'access_token': res.session.access_token, 'email': res.user.email}
    except Exception as e:
        return {'error': str(e)}


def _calc_duration(start_date, start_time, end_date, end_time):
    if not start_time or not end_time:
        return 0.0
    end_d = end_date or start_date
    try:
        start_dt = datetime.fromisoformat(f"{start_date}T{start_time}")
        end_dt = datetime.fromisoformat(f"{end_d}T{end_time}")
        return max(0.0, (end_dt - start_dt).total_seconds() / 3600)
    except Exception:
        return 0.0


def _row_to_report(row):
    return {
        'id': row['id'],
        'date': row['date'],
        'project': row['project'] or '',
        'start_time': row['start_time'] or '',
        'end_time': row['end_time'] or '',
        'duration_hours': float(row['duration_hours'] or 0),
        'end_date': row['end_date'] or '',
        'mission_code': row.get('mission_code') or '',
        'mission_description': row.get('mission_description') or '',
    }


# ── Reports ───────────────────────────────────────────────────────────────────

def get_reports(date_str):
    res = _get_client().table('time_reports').select('*').eq('date', date_str).execute()
    return [_row_to_report(r) for r in res.data]


def get_reports_range(start_str, end_str):
    res = (_get_client().table('time_reports').select('*')
           .gte('date', start_str).lte('date', end_str).execute())
    return [_row_to_report(r) for r in res.data]


def add_report(date_str, project, start_time, end_time, end_date=None, mission_code='', mission_description=''):
    duration = _calc_duration(date_str, start_time, end_date, end_time)
    res = _get_client().table('time_reports').insert({
        'date': date_str,
        'project': project or '',
        'start_time': start_time or '',
        'end_time': end_time or '',
        'duration_hours': duration,
        'end_date': end_date or None,
        'mission_code': mission_code or '',
        'mission_description': mission_description or '',
    }).execute()
    return _row_to_report(res.data[0])


def update_report(report_id, date_str, project, start_time, end_time, end_date=None, mission_code='', mission_description=''):
    duration = _calc_duration(date_str, start_time, end_date, end_time)
    res = _get_client().table('time_reports').update({
        'date': date_str,
        'project': project or '',
        'start_time': start_time or '',
        'end_time': end_time or '',
        'duration_hours': duration,
        'end_date': end_date or None,
        'mission_code': mission_code or '',
        'mission_description': mission_description or '',
    }).eq('id', report_id).execute()
    if not res.data:
        return None
    return _row_to_report(res.data[0])


def delete_report(report_id):
    res = _get_client().table('time_reports').delete().eq('id', report_id).execute()
    return bool(res.data)


# ── Projects ──────────────────────────────────────────────────────────────────

def get_projects():
    res = _get_client().table('projects').select('*').execute()
    return [{'id': r['id'], 'name': r['name'], 'favorite': r['favorite'], 'active': r['active']}
            for r in res.data]


def add_project(name):
    res = _get_client().table('projects').insert(
        {'name': name, 'favorite': False, 'active': True}
    ).execute()
    r = res.data[0]
    return {'id': r['id'], 'name': r['name'], 'favorite': r['favorite'], 'active': r['active']}


def update_project(project_id, name, favorite, active):
    res = _get_client().table('projects').update({
        'name': name,
        'favorite': bool(favorite),
        'active': bool(active),
    }).eq('id', project_id).execute()
    if not res.data:
        return None
    r = res.data[0]
    return {'id': r['id'], 'name': r['name'], 'favorite': r['favorite'], 'active': r['active']}


def delete_project(project_id):
    res = _get_client().table('projects').delete().eq('id', project_id).execute()
    return bool(res.data)


# ── Holidays ──────────────────────────────────────────────────────────────────

def get_holidays():
    res = _get_client().table('holidays').select('*').execute()
    return [{'id': r['id'], 'date': r['date'], 'name': r['name'],
             'quota_hours': float(r['quota_hours'] or 0)}
            for r in res.data]


def add_holiday(date_str, name, quota_hours):
    res = _get_client().table('holidays').insert(
        {'date': date_str, 'name': name, 'quota_hours': float(quota_hours)}
    ).execute()
    r = res.data[0]
    return {'id': r['id'], 'date': r['date'], 'name': r['name'], 'quota_hours': float(r['quota_hours'])}


def update_holiday(holiday_id, date_str, name, quota_hours):
    res = _get_client().table('holidays').update(
        {'date': date_str, 'name': name, 'quota_hours': float(quota_hours)}
    ).eq('id', holiday_id).execute()
    if not res.data:
        return None
    r = res.data[0]
    return {'id': r['id'], 'date': r['date'], 'name': r['name'], 'quota_hours': float(r['quota_hours'])}


def delete_holiday(holiday_id):
    res = _get_client().table('holidays').delete().eq('id', holiday_id).execute()
    return bool(res.data)


# ── Day Status ────────────────────────────────────────────────────────────────

def get_day_status(date_str):
    res = _get_client().table('day_status').select('status').eq('date', date_str).execute()
    return res.data[0]['status'] if res.data else 'normal'


def get_day_statuses_range(start_str, end_str):
    res = (_get_client().table('day_status').select('date,status')
           .gte('date', start_str).lte('date', end_str).execute())
    return {r['date']: r['status'] for r in res.data}


def set_day_status(date_str, status):
    _get_client().table('day_status').upsert({'date': date_str, 'status': status}).execute()


# ── Quota & Balance ───────────────────────────────────────────────────────────

def get_quota(d, holidays_cache=None):
    if d.weekday() in (4, 5):  # Friday or Saturday
        return 0.0
    holidays = holidays_cache if holidays_cache is not None else get_holidays()
    for h in holidays:
        if h['date'] == d.isoformat():
            return h['quota_hours']
    return 9.0


def get_balance(ref_date_str):
    ref = date.fromisoformat(ref_date_str)
    holidays = get_holidays()

    def day_actual(d):
        return sum(r['duration_hours'] for r in get_reports(d.isoformat()))

    d_actual = day_actual(ref)
    d_quota = get_quota(ref, holidays)

    days_since_sunday = (ref.weekday() + 1) % 7
    week_start = ref - timedelta(days=days_since_sunday)
    week_end = week_start + timedelta(days=4)
    w_actual, w_quota = 0.0, 0.0
    d = week_start
    while d <= week_end:
        if d <= ref:
            w_actual += day_actual(d)
            w_quota += get_quota(d, holidays)
        d += timedelta(days=1)

    month_start = ref.replace(day=1)
    m_actual, m_quota = 0.0, 0.0
    d = month_start
    while d <= ref:
        m_actual += day_actual(d)
        m_quota += get_quota(d, holidays)
        d += timedelta(days=1)

    return {
        'daily':   {'actual': round(d_actual, 2), 'quota': d_quota,  'balance': round(d_actual - d_quota, 2)},
        'weekly':  {'actual': round(w_actual, 2), 'quota': w_quota,  'balance': round(w_actual - w_quota, 2)},
        'monthly': {'actual': round(m_actual, 2), 'quota': m_quota,  'balance': round(m_actual - m_quota, 2)},
    }
