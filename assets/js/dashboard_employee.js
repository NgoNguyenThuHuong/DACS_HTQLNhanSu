// Employee Dashboard Logic
function handleAttendance(action) {
    if (!confirm('Bạn muốn thực hiện thao tác này?')) return;
    const formData = new FormData();
    formData.append('action', action);
    
    // Thêm feedback người dùng (loading) nếu cần
    const btn = event.currentTarget;
    const originalContent = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Đang xử lý...';

    fetch('modules/attendance/ajax_check.php', { method: 'POST', body: formData })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) location.reload();
        else {
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Đã có lỗi xảy ra. Vui lòng thử lại sau.');
        btn.disabled = false;
        btn.innerHTML = originalContent;
    });
}
