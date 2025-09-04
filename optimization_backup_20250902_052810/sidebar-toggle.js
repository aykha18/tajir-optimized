// Sidebar Toggle Module
class SidebarToggle {
    constructor() {
        this.sidebar = null;
        this.mobileMenuToggle = null;
        this.sidebarCloseBtn = null;
        this.isOpen = false;
        this.init();
    }

    init() {
        this.sidebar = document.getElementById('sidebar');
        this.mobileMenuToggle = document.getElementById('mobileMenuToggle');
        this.sidebarCloseBtn = document.getElementById('sidebarCloseBtn');
        
        if (!this.sidebar) {
            console.error('Sidebar not found');
            return;
        }

        this.setupEventListeners();
        this.setupResponsiveBehavior();
        console.log('Sidebar toggle initialized');
    }

    setupEventListeners() {
        // Mobile menu toggle button
        if (this.mobileMenuToggle) {
            this.mobileMenuToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        // Close button (mobile only)
        if (this.sidebarCloseBtn) {
            this.sidebarCloseBtn.addEventListener('click', () => {
                this.closeSidebar();
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (this.isOpen && window.innerWidth < 1024) {
                if (!this.sidebar.contains(e.target) && 
                    !this.mobileMenuToggle.contains(e.target)) {
                    this.closeSidebar();
                }
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    setupResponsiveBehavior() {
        // On large screens, always show sidebar
        if (window.innerWidth >= 1024) {
            this.showSidebar();
        } else {
            this.hideSidebar();
        }
    }

    toggleSidebar() {
        if (this.isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        if (!this.sidebar) return;
        
        this.sidebar.classList.remove('hidden');
        this.sidebar.classList.add('lg:block');
        
        // Add mobile-specific positioning
        if (window.innerWidth < 1024) {
            this.sidebar.classList.add('fixed', 'inset-y-0', 'left-0', 'z-50');
            this.sidebar.classList.remove('lg:relative', 'lg:inset-auto');
        }
        
        this.isOpen = true;
        console.log('Sidebar opened');
    }

    closeSidebar() {
        if (!this.sidebar) return;
        
        this.sidebar.classList.add('hidden');
        this.sidebar.classList.remove('lg:block');
        
        // Remove mobile-specific positioning
        this.sidebar.classList.remove('fixed', 'inset-y-0', 'left-0', 'z-50');
        
        this.isOpen = false;
        console.log('Sidebar closed');
    }

    handleResize() {
        if (window.innerWidth >= 1024) {
            // Large screen - show sidebar
            this.showSidebar();
        } else {
            // Small screen - hide sidebar
            this.hideSidebar();
        }
    }

    showSidebar() {
        if (!this.sidebar) return;
        
        this.sidebar.classList.remove('hidden');
        this.sidebar.classList.add('lg:block');
        this.sidebar.classList.remove('fixed', 'inset-y-0', 'left-0', 'z-50');
        this.sidebar.classList.add('lg:relative', 'lg:inset-auto');
        this.isOpen = true;
    }

    hideSidebar() {
        if (!this.sidebar) return;
        
        this.sidebar.classList.add('hidden');
        this.sidebar.classList.remove('lg:block');
        this.sidebar.classList.remove('fixed', 'inset-y-0', 'left-0', 'z-50');
        this.isOpen = false;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.sidebarToggle = new SidebarToggle();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SidebarToggle;
}
