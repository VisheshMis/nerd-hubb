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

    // Genre theme switcher in the UI (if present)
    const themeSwitchers = document.querySelectorAll('.theme-switcher');
    if (themeSwitchers.length > 0) {
        themeSwitchers.forEach(switcher => {
            switcher.addEventListener('click', function(e) {
                e.preventDefault();
                const theme = this.dataset.theme;
                if (theme) {
                    document.body.className = theme + '-theme';
                    localStorage.setItem('preferred-theme', theme);
                }
            });
        });
    }
    
    // Apply stored theme preference
    const storedTheme = localStorage.getItem('preferred-theme');
    if (storedTheme && !document.body.className.includes('theme')) {
        document.body.className = storedTheme + '-theme';
    }
    
    // Add book cover effects
    const bookCovers = document.querySelectorAll('.book-cover');
    bookCovers.forEach(cover => {
        cover.addEventListener('mouseover', function() {
            this.classList.add('book-hover');
        });
        cover.addEventListener('mouseout', function() {
            this.classList.remove('book-hover');
        });
    });
    
    // Add fancy scroll effect for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').length > 1) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Handle book search form animations
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[type="search"]');
        searchInput.addEventListener('focus', function() {
            searchForm.classList.add('search-focus');
        });
        searchInput.addEventListener('blur', function() {
            if (this.value === '') {
                searchForm.classList.remove('search-focus');
            }
        });
    }
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