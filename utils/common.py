from datetime import datetime

# 날짜/시간 포맷팅 함수
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    """주어진 datetime 객체를 지정된 포맷으로 변환합니다."""
    if not isinstance(value, datetime):
        raise ValueError("value는 datetime 객체여야 합니다.")
    return value.strftime(format)

# 입력값 검증 함수
def validate_input(value, allowed_values):
    """입력값이 허용된 값 목록에 있는지 확인합니다."""
    if value not in allowed_values:
        raise ValueError(f"{value}는 허용되지 않는 값입니다.")
    return True
