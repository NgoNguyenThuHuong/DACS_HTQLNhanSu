from datetime import datetime, date, time, timedelta
from app.core.exceptions import BusinessException
from app.core.config import Config

class CooldownPolicy:
    @staticmethod
    def validate(latest_log, now_dt):
        """
        Check if the anti-spam cooldown requirement is satisfied.
        """
        if not latest_log:
            print(f"\n[ATTENDANCE DEBUG]\nuser=None\nlast_checkin=None\nnow={now_dt}\ndiff=N/A\nblocked_by_cooldown=False\n")
            return True
        
        # ATTENDANCE_COOLDOWN_SECONDS is read from Config, defaulting to 180 seconds if not defined
        cooldown_seconds = getattr(Config, 'ATTENDANCE_COOLDOWN_SECONDS', 180)
        
        elapsed = (now_dt - latest_log.timestamp).total_seconds()
        
        # Safe fallback for future timestamps or timezone offsets
        if elapsed < 0:
            elapsed = cooldown_seconds + 1
            
        blocked = elapsed < cooldown_seconds
        
        # Print detailed debug logs to console
        print(f"\n[ATTENDANCE DEBUG]\n"
              f"user={latest_log.employee_id}\n"
              f"last_checkin={latest_log.timestamp}\n"
              f"now={now_dt}\n"
              f"diff={int(elapsed)}s\n"
              f"cooldown_remaining={max(0, int(cooldown_seconds - elapsed))}s\n"
              f"blocked_by_cooldown={blocked}\n")
        
        if blocked:
            raise BusinessException(
                f"Thao tác quá nhanh. Vui lòng đợi ít nhất {cooldown_seconds} giây giữa các lần chấm công. "
                f"(Đã trôi qua: {int(elapsed)}s)"
            )
        return True

class StateMachinePolicy:
    STATES = {
        'OUTSIDE': 'OUTSIDE',
        'INSIDE': 'INSIDE',
        'BREAK': 'BREAK'
    }

    ACTIONS = {
        'CHECK_IN': 'CHECK_IN',
        'CHECK_OUT': 'CHECK_OUT',
        'BREAK_OUT': 'BREAK_OUT',
        'BREAK_IN': 'BREAK_IN'
    }

    @classmethod
    def get_current_state(cls, latest_log):
        """
        Determine the current state based on the absolute latest log of the employee.
        """
        if not latest_log:
            return cls.STATES['OUTSIDE']
        
        action = latest_log.action_type
        if action in [cls.ACTIONS['CHECK_IN'], cls.ACTIONS['BREAK_IN']]:
            return cls.STATES['INSIDE']
        elif action == cls.ACTIONS['BREAK_OUT']:
            return cls.STATES['BREAK']
        else:
            return cls.STATES['OUTSIDE']

    @classmethod
    def validate_transition(cls, current_state, action):
        """
        Validate transition. Returns (is_valid, anomaly_type, description).
        """
        # Transition rules:
        # OUTSIDE -> CHECK_IN: INSIDE (Valid)
        # INSIDE -> CHECK_OUT: OUTSIDE (Valid)
        # INSIDE -> BREAK_OUT: BREAK (Valid)
        # BREAK -> BREAK_IN: INSIDE (Valid)
        # BREAK -> CHECK_OUT: OUTSIDE (Valid fallback)
        
        if current_state == cls.STATES['OUTSIDE']:
            if action == cls.ACTIONS['CHECK_IN']:
                return True, None, None
            else:
                return False, 'ORPHAN_CHECK_OUT', f"Yêu cầu {action} khi đang ở trạng thái OUTSIDE."
        
        elif current_state == cls.STATES['INSIDE']:
            if action in [cls.ACTIONS['CHECK_OUT'], cls.ACTIONS['BREAK_OUT']]:
                return True, None, None
            elif action == cls.ACTIONS['CHECK_IN']:
                return False, 'CONSECUTIVE_CHECK_IN', "Yêu cầu CHECK_IN liên tiếp mà chưa CHECK_OUT."
            else:
                return False, 'SUSPICIOUS_RAPID_SWITCHING', f"Hành động {action} không hợp lệ khi đang INSIDE."
                
        elif current_state == cls.STATES['BREAK']:
            if action in [cls.ACTIONS['BREAK_IN'], cls.ACTIONS['CHECK_OUT']]:
                return True, None, None
            else:
                return False, 'SUSPICIOUS_RAPID_SWITCHING', f"Hành động {action} không hợp lệ khi đang ở trạng thái BREAK."
        
        return False, 'UNKNOWN_ANOMALY', "Trạng thái không xác định."

class ShiftPolicy:
    @staticmethod
    def match_shift(shifts, dt_now):
        """
        Matches a datetime to the most appropriate Shift from a list.
        Supports standard and overnight shifts.
        """
        if not shifts:
            return None
        
        current_time = dt_now.time()
        current_minutes = current_time.hour * 60 + current_time.minute
        
        matched_shift = None
        min_diff = float('inf')
        
        for shift in shifts:
            start_time = shift.start_time
            end_time = shift.end_time
            
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = end_time.hour * 60 + end_time.minute
            
            # Case 1: Overnight Shift (e.g. 22:00 to 06:00)
            if shift.is_overnight or start_minutes > end_minutes:
                # Overnight boundary check: current time is after start_time OR before end_time
                is_within = False
                if start_minutes > end_minutes:
                    if current_time >= start_time or current_time <= end_time:
                        is_within = True
                else:
                    if start_time <= current_time <= end_time:
                        is_within = True
                
                if is_within:
                    return shift
                
                # Coarse distance calculation for overnight
                diff = min(abs(current_minutes - start_minutes), abs(current_minutes - (start_minutes - 1440)))
                if diff < min_diff:
                    min_diff = diff
                    matched_shift = shift
            
            # Case 2: Standard Shift
            else:
                # Standard boundary check with 60 minutes pre-arrival buffer
                if start_minutes - 60 <= current_minutes <= end_minutes:
                    return shift
                
                diff = abs(current_minutes - start_minutes)
                if diff < min_diff:
                    min_diff = diff
                    matched_shift = shift
                    
        return matched_shift

class LatePolicy:
    @staticmethod
    def calculate_late_minutes(check_in_dt, shift):
        """
        Calculate late minutes relative to shift start.
        """
        if not shift:
            return 0.0
        
        # Combine date of check_in with shift start_time
        # For overnight shifts, if check_in occurs within the pre-arrival window after midnight (e.g. at 00:05 for a 22:00 shift),
        # the shift actually started on the PREVIOUS day.
        shift_start_dt = datetime.combine(check_in_dt.date(), shift.start_time)
        
        if shift.is_overnight and check_in_dt.time() < shift.end_time:
            # Check-in occurred after midnight, shift started previous day
            shift_start_dt -= timedelta(days=1)
            
        if check_in_dt > shift_start_dt:
            return max(0.0, (check_in_dt - shift_start_dt).total_seconds() / 60.0)
        return 0.0

class OvertimePolicy:
    @staticmethod
    def calculate_overtime_hours(check_in_dt, check_out_dt, shift):
        """
        Calculate overtime hours.
        - If shift name contains 'Overtime' or 'OT': 100% of duration is overtime.
        - If check-out is after standard shift end_time: excess duration is overtime.
        """
        if not shift:
            return 0.0
            
        total_duration = (check_out_dt - check_in_dt).total_seconds() / 3600.0
        if total_duration <= 0:
            return 0.0
            
        if 'overtime' in shift.name.lower() or 'ot' in shift.name.lower():
            return total_duration
            
        shift_end_dt = datetime.combine(check_in_dt.date(), shift.end_time)
        if shift.is_overnight and shift.start_time > shift.end_time:
            # Shift ends on the next day relative to start day
            # Determine if check_in is on start day or end day
            if check_in_dt.time() >= shift.start_time:
                shift_end_dt += timedelta(days=1)
            # If check_in is already next day, shift_end_dt matches check_in date
            
        if check_out_dt > shift_end_dt:
            return max(0.0, (check_out_dt - shift_end_dt).total_seconds() / 3600.0)
            
        return 0.0
