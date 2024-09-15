// Divisions-related JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    const divisionsDropdown = document.getElementById('divisionsDropdown');
    const divisionsMenu = document.getElementById('divisionsMenu');

    if (divisionsDropdown && divisionsMenu) {
        divisionsDropdown.addEventListener('click', function() {
            divisionsMenu.classList.toggle('hidden');
        });

        // Fetch divisions and populate the dropdown
        fetch('/divisions')
            .then(response => response.json())
            .then(divisions => {
                divisions.forEach(division => {
                    const link = document.createElement('a');
                    link.href = `/divisions#${division.name.toLowerCase().replace(' ', '-')}`;
                    link.textContent = division.name;
                    link.className = 'block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100';
                    divisionsMenu.appendChild(link);
                });
            });
    }
});
