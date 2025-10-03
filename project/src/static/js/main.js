
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('loginModal');
    const openBtn = document.getElementById('loginModalOpen');
    const closeBtn = document.getElementById('loginModalClose');

    openBtn.addEventListener('click', function(e) {
        e.preventDefault();
        modal.style.display = 'block';
    });

    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

