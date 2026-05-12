-- SQL Script cho Hệ thống Quản lý Nhân sự Thông minh
-- Cơ sở dữ liệu: ql_nhansu

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 1. Tạo bảng phòng ban (departments)
CREATE TABLE IF NOT EXISTS `departments` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tạo bảng nhân viên (employees)
CREATE TABLE IF NOT EXISTS `employees` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `employee_code` VARCHAR(20) NOT NULL UNIQUE,
  `fullname` VARCHAR(100) NOT NULL,
  `birthday` DATE DEFAULT NULL,
  `gender` ENUM('Nam', 'Nữ', 'Khác') DEFAULT 'Nam',
  `social_id` VARCHAR(20) DEFAULT NULL,
  `email` VARCHAR(100) DEFAULT NULL,
  `phone` VARCHAR(20) DEFAULT NULL,
  `address` TEXT DEFAULT NULL,
  `hometown` VARCHAR(255) DEFAULT NULL,
  `bank_name` VARCHAR(100) DEFAULT NULL,
  `bank_account` VARCHAR(50) DEFAULT NULL,
  `emergency_contact` VARCHAR(255) DEFAULT NULL,
  `education` VARCHAR(100) DEFAULT NULL,
  `marital_status` VARCHAR(50) DEFAULT NULL,
  `department_id` INT(11) DEFAULT NULL,
  `position` VARCHAR(100) DEFAULT NULL,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `role` ENUM('Admin', 'HR', 'Employee') DEFAULT 'Employee',
  `leave_days_quota` INT DEFAULT 12,
  `leave_days_used` INT DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_employee_dept` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Tạo bảng chấm công (attendance)
CREATE TABLE IF NOT EXISTS `attendance` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `employee_id` INT(11) NOT NULL,
  `work_date` DATE NOT NULL,
  `check_in` DATETIME DEFAULT NULL,
  `check_out` DATETIME DEFAULT NULL,
  `status` VARCHAR(50) DEFAULT 'Normal',
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_attendance_emp` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Tạo bảng yêu cầu nghỉ phép (leave_requests)
CREATE TABLE IF NOT EXISTS `leave_requests` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `employee_id` INT(11) NOT NULL,
  `leave_type` VARCHAR(100) DEFAULT 'Nghỉ phép năm',
  `reason` TEXT DEFAULT NULL,
  `start_date` DATE NOT NULL,
  `end_date` DATE NOT NULL,
  `status` ENUM('Pending', 'Approved', 'Rejected') DEFAULT 'Pending',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_leave_emp` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chèn dữ liệu mẫu
INSERT INTO `departments` (`name`, `description`) VALUES 
('Phòng Kỹ thuật', 'Phát triển phần mềm và bảo trì hệ thống'),
('Phòng Marketing', 'Truyền thông và quảng bá sản phẩm'),
('Phòng Nhân sự', 'Quản lý nhân viên và tuyển dụng');

-- Mật khẩu mặc định là '123456' (Trong thực tế nên dùng hash)
INSERT INTO `employees` (`employee_code`, `fullname`, `username`, `password`, `role`, `department_id`) VALUES 
('NV001', 'Quản trị viên', 'admin', '123456', 'Admin', 3);

-- 5. Tạo bảng nhiệm vụ (tasks)
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `employee_id` INT(11) NOT NULL,
  `title` VARCHAR(255) NOT NULL,
  `due_date` DATETIME DEFAULT NULL,
  `priority` ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
  `status` ENUM('Pending', 'Completed') DEFAULT 'Pending',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_task_emp` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chèn nhiệm vụ mẫu cho NV002
INSERT INTO `tasks` (`employee_id`, `title`, `due_date`, `priority`) VALUES 
(2, 'Hoàn thành báo cáo tháng 10', '2023-10-24 17:00:00', 'High'),
(2, 'Họp dự án mới (Team Branding)', '2023-10-24 14:00:00', 'Medium'),
(2, 'Review mã nguồn cho cộng sự', '2023-10-25 09:00:00', 'Low');

-- 6. Tạo bảng nhật ký hệ thống (system_logs)
CREATE TABLE IF NOT EXISTS `system_logs` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) DEFAULT NULL,
  `action` VARCHAR(255) NOT NULL,
  `target_user_id` INT(11) DEFAULT NULL,
  `details` TEXT DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_log_user` FOREIGN KEY (`user_id`) REFERENCES `employees` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 7. Tạo bảng phân tích nhân sự (employee_analytics)
CREATE TABLE IF NOT EXISTS `employee_analytics` (
        `id` INT(11) NOT NULL AUTO_INCREMENT,
        `employee_id` INT(11) NOT NULL,
        `job_satisfaction` TINYINT(1) DEFAULT NULL,
        `monthly_income` INT(11) DEFAULT NULL,
        `overtime` ENUM('Yes', 'No') DEFAULT 'No',
        `distance_from_home` INT(11) DEFAULT NULL,
        `performance_rating` TINYINT(1) DEFAULT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        CONSTRAINT `fk_emp_analytics` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 8. Tạo bảng phân quyền (role_permissions)
CREATE TABLE IF NOT EXISTS `role_permissions` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `permission_key` VARCHAR(100) NOT NULL,
  `role_name` ENUM('Admin', 'HR', 'Employee') NOT NULL,
  `is_allowed` TINYINT(1) DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_role_perm` (`permission_key`, `role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Chèn dữ liệu mẫu cho ma trận phân quyền
INSERT IGNORE INTO `role_permissions` (`permission_key`, `role_name`, `is_allowed`) VALUES
('Dashboard', 'Admin', 1), ('Dashboard', 'HR', 1), ('Dashboard', 'Employee', 1),
('Quản lý nhân viên', 'Admin', 1), ('Quản lý nhân viên', 'HR', 1), ('Quản lý nhân viên', 'Employee', 0),
('Cơ sở dữ liệu', 'Admin', 1), ('Cơ sở dữ liệu', 'HR', 0), ('Cơ sở dữ liệu', 'Employee', 0),
('Quản lý tài khoản', 'Admin', 1), ('Quản lý tài khoản', 'HR', 0), ('Quản lý tài khoản', 'Employee', 0),
('Phân quyền', 'Admin', 1), ('Phân quyền', 'HR', 0), ('Phân quyền', 'Employee', 0),
('Backup Data', 'Admin', 1), ('Backup Data', 'HR', 0), ('Backup Data', 'Employee', 0),
('System logs', 'Admin', 1), ('System logs', 'HR', 0), ('System logs', 'Employee', 0),
('Báo cáo tổng', 'Admin', 1), ('Báo cáo tổng', 'HR', 1), ('Báo cáo tổng', 'Employee', 0),
('Chấm công', 'Admin', 1), ('Chấm công', 'HR', 1), ('Chấm công', 'Employee', 1),
('Duyệt nghỉ phép', 'Admin', 1), ('Duyệt nghỉ phép', 'HR', 1), ('Duyệt nghỉ phép', 'Employee', 0),
('Yêu cầu nghỉ phép', 'Admin', 0), ('Yêu cầu nghỉ phép', 'HR', 0), ('Yêu cầu nghỉ phép', 'Employee', 1),
('Hồ sơ của tôi', 'Admin', 1), ('Hồ sơ của tôi', 'HR', 1), ('Hồ sơ của tôi', 'Employee', 1);

-- 9. Tạo bảng ghi đè quyền cá nhân (user_permissions)
CREATE TABLE IF NOT EXISTS `user_permissions` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `permission_key` VARCHAR(100) NOT NULL,
  `is_allowed` TINYINT(1) DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_perm` (`user_id`, `permission_key`),
  CONSTRAINT `fk_user_perm` FOREIGN KEY (`user_id`) REFERENCES `employees` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
