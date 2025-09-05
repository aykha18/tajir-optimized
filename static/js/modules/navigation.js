// Navigation module for handling page navigation
console.log('Navigation module loaded');

// Handle navigation buttons with data-go attributes
document.addEventListener('DOMContentLoaded', function() {
    // Handle navigation buttons with data-go attributes
    document.addEventListener('click', function(e) {
        const navButton = e.target.closest('[data-go]');
        if (navButton) {
            e.preventDefault();
            const targetSection = navButton.getAttribute('data-go');
            
            // Hide all sections
            document.querySelectorAll('.page').forEach(section => {
                section.classList.add('hidden');
            });
            
            // Show target section
            const targetElement = document.getElementById(targetSection);
            if (targetElement) {
                targetElement.classList.remove('hidden');
                console.log(`Navigated to: ${targetSection}`);
            } else {
                console.warn(`Section not found: ${targetSection}`);
            }
        }
    });
});
