// 获取按钮元素
var button = document.getElementById('customButton');

// 添加点击事件处理程序
button.addEventListener('click', function() {
    // 设置要跳转的页面的URL
    var destinationPage = "/profile";

    // 使用 window.location.href 实现页面跳转
    window.location.href = destinationPage;
});