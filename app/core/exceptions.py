class BusinessException(Exception):
    """Base exception for all business logic errors."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class EntityNotFoundException(BusinessException):
    def __init__(self, message="Không tìm thấy thực thể yêu cầu."):
        super().__init__(message, status_code=404)

class ValidationException(BusinessException):
    def __init__(self, message="Dữ liệu đầu vào không hợp lệ."):
        super().__init__(message, status_code=400)

class AuthorizationException(BusinessException):
    def __init__(self, message="Bạn không có quyền truy cập chức năng này."):
        super().__init__(message, status_code=403)

class AIVerificationError(BusinessException):
    def __init__(self, message="Lỗi xác thực AI / Nhận diện khuôn mặt."):
        super().__init__(message, status_code=400)

# Aliases for convenience
ValidationError = ValidationException
AuthorizationError = AuthorizationException
