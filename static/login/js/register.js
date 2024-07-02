$(document).ready(function() {
    $('#register-form').submit(function(event) {
        event.preventDefault(); // 阻止表單默認提交行為

        var formData = $(this).serialize(); // 獲取表單數據
        $.ajax({
            type: 'POST',
            url: '/register',
            data: formData,
            success: function(response) {
                // 註冊成功，彈出提示框
                alert('註冊成功');
                // 重定向到首頁
                window.location.href = '/';
            },
            error: function(xhr, status, error) {
                var errorMessage = xhr.responseText; // 獲取服務器返回的錯誤消息
                // 如果是重複帳號的錯誤，顯示相應的提示框
                if (errorMessage.includes('帳號重複')) {
                    alert('帳號重複，請嘗試其他帳號');
                } else {
                    // 其他錯誤，顯示默認錯誤提示框
                    alert('註冊失敗，帳號已使用');
                }
            }
        });
    });
});

