document.addEventListener('DOMContentLoaded', () => {

    // Handle Like buttons
    document.querySelectorAll('.like-form').forEach(form => {
        const btn = form.querySelector('.like-btn');

        // Set initial active state
        if (btn.classList.contains('btn-primary')) {
            btn.classList.add('active');
        }

        form.addEventListener('submit', e => {
            e.preventDefault();

            fetch(form.action, { method: 'POST' })
            .then(resp => resp.json())
            .then(data => {
                btn.querySelector('.like-count').textContent = data.likes;
                btn.classList.toggle('btn-primary', data.liked);
                btn.classList.toggle('btn-outline-primary', !data.liked);
            });
        });
    });

    // Handle Bookmark buttons
    document.querySelectorAll('.bookmark-form').forEach(form => {
        const btn = form.querySelector('.bookmark-btn');

        // Set initial active state
        if (btn.classList.contains('btn-warning')) {
            btn.classList.add('active');
        }

        form.addEventListener('submit', e => {
            e.preventDefault();

            fetch(form.action, { method: 'POST' })
            .then(resp => resp.json())
            .then(data => {
                btn.classList.toggle('btn-warning', data.bookmarked);
                btn.classList.toggle('btn-outline-warning', !data.bookmarked);
            });
        });
    });

});
