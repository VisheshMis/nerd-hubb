// BookShelf JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Search suggestions
    const searchInput = document.querySelector('.navbar .form-control[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            const query = e.target.value.trim();
            if (query.length < 2) return;
            
            fetch(`/books/search?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    // Handle search suggestions
                    console.log('Search results:', data);
                    // Implement dropdown results here
                })
                .catch(error => console.error('Error fetching search results:', error));
        }, 300));
    }
    
    // Shelf status updates via AJAX
    const shelfButtons = document.querySelectorAll('.shelf-button');
    shelfButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const form = this.closest('form');
            const url = form.action;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update UI to reflect shelf change
                    const bookCard = this.closest('.card');
                    const statusLabel = bookCard.querySelector('.shelf-status');
                    
                    if (statusLabel) {
                        statusLabel.textContent = data.shelf;
                        statusLabel.className = 'shelf-status ' + data.shelf.replace('_', '-');
                    }
                    
                    // Show success message
                    const toast = new bootstrap.Toast(document.getElementById('shelf-toast'));
                    document.getElementById('shelf-toast-body').textContent = 
                        `Book ${data.shelf === 'remove' ? 'removed from' : 'added to'} your shelf!`;
                    toast.show();
                }
            })
            .catch(error => console.error('Error updating shelf:', error));
        });
    });
    
    // Star rating input functionality
    const ratingInputs = document.querySelectorAll('.rating-input');
    ratingInputs.forEach(input => {
        const stars = input.querySelectorAll('.star-rating');
        
        stars.forEach((star, index) => {
            // Hover effect
            star.addEventListener('mouseenter', () => {
                for (let i = 0; i <= index; i++) {
                    stars[i].classList.add('active');
                }
            });
            
            star.addEventListener('mouseleave', () => {
                stars.forEach(s => {
                    if (!s.classList.contains('selected')) {
                        s.classList.remove('active');
                    }
                });
            });
            
            // Click to select
            star.addEventListener('click', () => {
                const ratingValue = index + 1;
                const hiddenInput = input.querySelector('input[type="hidden"]');
                
                stars.forEach((s, i) => {
                    s.classList.remove('selected');
                    s.classList.remove('active');
                    
                    if (i <= index) {
                        s.classList.add('selected');
                        s.classList.add('active');
                    }
                });
                
                hiddenInput.value = ratingValue;
            });
        });
    });
});

// Helper function for debouncing
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
} 