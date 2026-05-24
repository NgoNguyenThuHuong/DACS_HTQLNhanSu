from datetime import datetime, date, timedelta, time
from app.repositories.attendance_log_repo import AttendanceLogRepository
from app.repositories.shift_repo import ShiftRepository
from app.services.attendance_policies import LatePolicy, OvertimePolicy, ShiftPolicy, StateMachinePolicy
from app.extensions import db

class AttendanceSessionService:
    def __init__(self):
        self.log_repo = AttendanceLogRepository()
        self.shift_repo = ShiftRepository()

    def reconstruct_day_sessions(self, employee_id, work_date):
        """
        Reconstruct sessions dynamically for an employee on a specific work date.
        To handle overnight shifts, we retrieve logs for both work_date and work_date + 1.
        """
        next_day = work_date + timedelta(days=1)
        logs = self.log_repo.get_logs_by_employee_and_date_range(employee_id, work_date, next_day)
        
        # Filter logs:
        # For work_date: keep all logs.
        # For next_day: keep only logs that belong to overnight shifts started on work_date.
        # (Usually, checking logs up to 12:00 PM of next_day is safe for overnight shifts).
        filtered_logs = []
        for log in logs:
            if log.timestamp.date() == work_date:
                filtered_logs.append(log)
            else:
                # Log is on the next day. We only count it if it is a CHECK_OUT, BREAK_IN or BREAK_OUT
                # that helps close a session started on work_date.
                # To be simple and robust: if the latest log before this next-day log was a CHECK_IN on work_date,
                # we include it.
                if filtered_logs and filtered_logs[-1].timestamp.date() == work_date:
                    # If last log was CHECK_IN, we include this next-day log to close the session
                    filtered_logs.append(log)
        
        # Sort logs ascendingly
        filtered_logs.sort(key=lambda l: l.timestamp)
        
        sessions = []
        active_session = None
        
        for log in filtered_logs:
            action = log.action_type
            
            if action == 'CHECK_IN':
                if active_session:
                    # Anomaly: Consecutive CHECK_IN. Close active session as orphan and start new.
                    sessions.append(active_session)
                    # Log anomaly
                    self.log_repo.create_anomaly(
                        employee_id=employee_id,
                        log_id=log.id,
                        anomaly_type='CONSECUTIVE_CHECK_IN',
                        description=f"CHECK_IN liên tiếp xuất hiện tại {log.timestamp}."
                    )
                active_session = {
                    'check_in': log,
                    'check_out': None,
                    'breaks': [],
                    'anomalies': []
                }
                
            elif action == 'CHECK_OUT':
                if active_session:
                    active_session['check_out'] = log
                    sessions.append(active_session)
                    active_session = None
                else:
                    # Anomaly: Orphan CHECK_OUT.
                    sessions.append({
                        'check_in': None,
                        'check_out': log,
                        'breaks': [],
                        'anomalies': ['ORPHAN_CHECK_OUT']
                    })
                    self.log_repo.create_anomaly(
                        employee_id=employee_id,
                        log_id=log.id,
                        anomaly_type='ORPHAN_CHECK_OUT',
                        description=f"CHECK_OUT mồ côi (không có CHECK_IN) xuất hiện tại {log.timestamp}."
                    )
                    
            elif action in ['BREAK_OUT', 'BREAK_IN']:
                if active_session:
                    active_session['breaks'].append(log)
                else:
                    # Break outside of session is an anomaly
                    self.log_repo.create_anomaly(
                        employee_id=employee_id,
                        log_id=log.id,
                        anomaly_type='SUSPICIOUS_RAPID_SWITCHING',
                        description=f"Ghi nhận {action} ngoài ca làm việc tại {log.timestamp}."
                    )
        
        # If there's an open active session left at the end
        if active_session:
            sessions.append(active_session)
            self.log_repo.create_anomaly(
                employee_id=employee_id,
                log_id=active_session['check_in'].id,
                anomaly_type='MISSING_CHECK_OUT',
                description=f"Thiếu CHECK_OUT cho phiên bắt đầu lúc {active_session['check_in'].timestamp}."
            )
            
        return sessions

    def calculate_session_metrics(self, session):
        """
        Calculate metrics for a single reconstructed session.
        """
        metrics = {
            'work_hours': 0.0,
            'break_minutes': 0.0,
            'overtime_hours': 0.0,
            'late_minutes': 0.0,
            'early_leave_minutes': 0.0
        }
        
        check_in = session.get('check_in')
        check_out = session.get('check_out')
        
        if not check_in or not check_out:
            return metrics # Missing pairing, cannot calculate standard metrics
            
        # 1. Total break duration within the session
        breaks = sorted(session['breaks'], key=lambda l: l.timestamp)
        break_minutes = 0.0
        i = 0
        while i < len(breaks) - 1:
            if breaks[i].action_type == 'BREAK_OUT' and breaks[i+1].action_type == 'BREAK_IN':
                break_minutes += (breaks[i+1].timestamp - breaks[i].timestamp).total_seconds() / 60.0
                i += 2
            else:
                i += 1
                
        metrics['break_minutes'] = break_minutes
        
        # 2. Total work hours (Gross)
        gross_hours = (check_out.timestamp - check_in.timestamp).total_seconds() / 3600.0
        # Net work hours excludes break time inside the session
        net_hours = max(0.0, gross_hours - (break_minutes / 60.0))
        metrics['work_hours'] = net_hours
        
        # 3. Resolve shift
        shift = check_in.shift
        if not shift:
            # If shift is not associated, try to resolve dynamically
            shifts = self.shift_repo.get_all_shifts()
            shift = ShiftPolicy.match_shift(shifts, check_in.timestamp)
            
        if shift:
            # 4. Late minutes
            metrics['late_minutes'] = LatePolicy.calculate_late_minutes(check_in.timestamp, shift)
            
            # 5. Early leave minutes
            shift_end_dt = datetime.combine(check_in.timestamp.date(), shift.end_time)
            if shift.is_overnight and shift.start_time > shift.end_time:
                # Overnight shift, ends on the next calendar day
                if check_in.timestamp.time() >= shift.start_time:
                    shift_end_dt += timedelta(days=1)
            
            if check_out.timestamp < shift_end_dt:
                metrics['early_leave_minutes'] = max(0.0, (shift_end_dt - check_out.timestamp).total_seconds() / 60.0)
                
            # 6. Overtime hours
            metrics['overtime_hours'] = OvertimePolicy.calculate_overtime_hours(check_in.timestamp, check_out.timestamp, shift)
            
        return metrics

    def calculate_daily_summary(self, employee_id, work_date):
        """
        Calculates day summary of work, breaks, and overtime for backward compatibility snapshot.
        """
        sessions = self.reconstruct_day_sessions(employee_id, work_date)
        
        total_work_hours = 0.0
        inner_break_minutes = 0.0
        overtime_hours = 0.0
        
        # Sort sessions to calculate inter-session gaps
        valid_sessions = [s for s in sessions if s['check_in'] and s['check_out']]
        valid_sessions.sort(key=lambda s: s['check_in'].timestamp)
        
        # Sum metrics from inside sessions
        for s in valid_sessions:
            m = self.calculate_session_metrics(s)
            total_work_hours += m['work_hours']
            inner_break_minutes += m['break_minutes']
            overtime_hours += m['overtime_hours']
            
        # Calculate gaps between sessions as break time
        gaps_minutes = 0.0
        for i in range(len(valid_sessions) - 1):
            end_prev = valid_sessions[i]['check_out'].timestamp
            start_next = valid_sessions[i+1]['check_in'].timestamp
            if start_next > end_prev:
                gaps_minutes += (start_next - end_prev).total_seconds() / 60.0
                
        total_break_minutes = inner_break_minutes + gaps_minutes
        
        # Get first check-in and last check-out
        first_check_in = None
        last_check_out = None
        
        all_logs = []
        for s in sessions:
            if s['check_in']: all_logs.append(s['check_in'])
            if s['check_out']: all_logs.append(s['check_out'])
            all_logs.extend(s['breaks'])
            
        if all_logs:
            all_logs.sort(key=lambda l: l.timestamp)
            # Find first check-in log
            checkins = [l for l in all_logs if l.action_type == 'CHECK_IN']
            if checkins:
                first_check_in = checkins[0].timestamp
                
            # Find last check-out log
            checkouts = [l for l in all_logs if l.action_type == 'CHECK_OUT']
            if checkouts:
                last_check_out = checkouts[-1].timestamp
                
        return {
            'first_check_in': first_check_in,
            'last_check_out': last_check_out,
            'total_work_hours': round(total_work_hours, 2),
            'total_break_minutes': round(total_break_minutes, 1),
            'overtime_hours': round(overtime_hours, 2)
        }
