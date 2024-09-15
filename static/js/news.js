// News-related JavaScript functionality
function addComment(event, newsId) {
    event.preventDefault();
    const form = event.target;
    const input = form.querySelector('input');
    const comment = input.value.trim();

    if (comment) {
        fetch('/api/comment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ news_id: newsId, comment: comment }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const commentsContainer = document.getElementById(`comments-${newsId}`);
                const newComment = document.createElement('div');
                newComment.className = 'bg-gray-100 p-2 rounded';
                newComment.innerHTML = `<strong>${data.username}:</strong> ${comment}`;
                commentsContainer.appendChild(newComment);
                input.value = '';
            }
        });
    }
}
