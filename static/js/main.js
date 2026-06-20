document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const toggleBtn = document.getElementById('sidebarToggle');
    const mobileToggle = document.getElementById('sidebarToggleMobile');

    function showSidebar() {
        sidebar.classList.add('show');
        overlay.classList.add('show');
        document.body.classList.add('sidebar-open');
    }
    function hideSidebar() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
        document.body.classList.remove('sidebar-open');
    }

    if (toggleBtn) toggleBtn.addEventListener('click', showSidebar);
    if (mobileToggle) mobileToggle.addEventListener('click', showSidebar);
    if (overlay) overlay.addEventListener('click', hideSidebar);

    // Close sidebar on link click (mobile)
    document.querySelectorAll('.sidebar .menu-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992) hideSidebar();
        });
    });

    // Auto-hide alerts
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 5000);
});