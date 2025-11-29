document.addEventListener('DOMContentLoaded', () => {

    // Handle Like buttons
    document.querySelectorAll('.like-form').forEach(form => {
        const btn = form.querySelector('.like-btn');

        // Initial active state
        if (btn.classList.contains('btn-primary')) {
            btn.classList.add('active');
            btn.classList.remove('btn-primary');
        }

        form.addEventListener('submit', e => {
            e.preventDefault();
            fetch(form.action, { method: 'POST' })
            .then(resp => resp.json())
            .then(data => {
                btn.querySelector('.like-count').textContent = data.likes;
                btn.classList.toggle('active', data.liked);
            });
        });
    });

    // Handle Bookmark buttons
    document.querySelectorAll('.bookmark-form').forEach(form => {
        const btn = form.querySelector('.bookmark-btn');

        // Initial active state
        if (btn.classList.contains('btn-warning')) {
            btn.classList.add('active');
            btn.classList.remove('btn-warning');
        }

        form.addEventListener('submit', e => {
            e.preventDefault();
            fetch(form.action, { method: 'POST' })
            .then(resp => resp.json())
            .then(data => {
                btn.classList.toggle('active', data.bookmarked);
            });
        });
    });

});
