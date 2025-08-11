/**
 * Mobile Navigation Module for Tajir POS PWA
 * Provides touch-friendly navigation with bottom navigation bar and swipe gestures
 */

class MobileNavigation {
  constructor() {
    this.currentSection = 'dashboard';
    // Replace Customers with Employees; move Customers/Reports/Settings under More
    this.sections = ['dashboard', 'billing', 'products', 'employees', 'more'];
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.touchEndX = 0;
    this.touchEndY = 0;
    this.minSwipeDistance = 50;
    this.isInitialized = false;
  }

  async init() {
    try {
      // Check if we're on a mobile device
      if (!this.isMobile()) {
        console.log('Mobile Navigation: Not on mobile device, skipping initialization');
        return;
      }

      this.createBottomNavigation();
      this.setupSwipeGestures();
      this.setupKeyboardHandling();
      this.setupTouchOptimizations();
      this.updateActiveSection();
      
      // Add resize listener to handle orientation changes
      window.addEventListener('resize', () => {
        this.handleResize();
      });
      
      console.log('Mobile Navigation: Initialized successfully');
      this.isInitialized = true;
    } catch (error) {
      console.error('Mobile Navigation: Initialization failed', error);
    }
  }

  createBottomNavigation() {
    // Remove existing mobile nav if present
    const existingNav = document.querySelector('.mobile-nav');
    if (existingNav) {
      existingNav.remove();
    }

    const nav = document.createElement('nav');
    nav.className = 'mobile-nav';
    nav.innerHTML = `
      <div class="flex justify-around items-center w-full">
        <a href="#dashboard" class="mobile-nav-item" data-section="dashboard">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v6H8V5z"></path>
          </svg>
          <span>Dashboard</span>
        </a>
        <a href="#billing" class="mobile-nav-item" data-section="billing">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <span>Billing</span>
        </a>
        <a href="#products" class="mobile-nav-item" data-section="products">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
          </svg>
          <span>Products</span>
        </a>
        <a href="#employees" class="mobile-nav-item" data-section="employees">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
          </svg>
          <span>Employees</span>
        </a>
        <a href="#more" class="mobile-nav-item" data-section="more">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6a2 2 0 110-4 2 2 0 010 4zm0 8a2 2 0 110-4 2 2 0 010 4zm0 8a2 2 0 110-4 2 2 0 010 4z"></path>
          </svg>
          <span>More</span>
        </a>
      </div>
    `;

    // Add click handlers
    nav.addEventListener('click', (e) => {
      const navItem = e.target.closest('.mobile-nav-item');
      if (navItem) {
        e.preventDefault();
        const section = navItem.dataset.section;
        this.navigateToSection(section);
      }
    });

    document.body.appendChild(nav);
    console.log('Mobile Navigation: Bottom navigation created');
  }

  setupSwipeGestures() {
    // Only add swipe gestures to the main content area, not to interactive elements
    const mainContent = document.querySelector('.mobile-container') || document.body;
    
    mainContent.addEventListener('touchstart', (e) => {
      // Don't handle swipes on interactive elements like tables, buttons, forms
      if (e.target.closest('table, button, input, select, textarea, .swipe-actions, .mobile-nav')) {
        return;
      }
      
      this.touchStartX = e.changedTouches[0].screenX;
      this.touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    mainContent.addEventListener('touchend', (e) => {
      // Don't handle swipes on interactive elements
      if (e.target.closest('table, button, input, select, textarea, .swipe-actions, .mobile-nav')) {
        return;
      }
      
      this.touchEndX = e.changedTouches[0].screenX;
      this.touchEndY = e.changedTouches[0].screenY;
      this.handleSwipe();
    }, { passive: true });
  }

  handleSwipe() {
    const deltaX = this.touchEndX - this.touchStartX;
    const deltaY = this.touchEndY - this.touchStartY;
    
    // Only handle horizontal swipes
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > this.minSwipeDistance) {
      const currentIndex = this.sections.indexOf(this.currentSection);
      
      console.log(`Mobile Navigation: Swipe detected - deltaX: ${deltaX}, currentSection: ${this.currentSection}`);
      
      if (deltaX > 0 && currentIndex > 0) {
        // Swipe right - go to previous section
        console.log(`Mobile Navigation: Swiping right to ${this.sections[currentIndex - 1]}`);
        this.navigateToSection(this.sections[currentIndex - 1]);
      } else if (deltaX < 0 && currentIndex < this.sections.length - 1) {
        // Swipe left - go to next section
        console.log(`Mobile Navigation: Swiping left to ${this.sections[currentIndex + 1]}`);
        this.navigateToSection(this.sections[currentIndex + 1]);
      }
    }
  }

  setupKeyboardHandling() {
    // Handle virtual keyboard
    const viewport = document.querySelector('meta[name=viewport]');
    if (viewport) {
      const originalContent = viewport.getAttribute('content');
      
      // Detect keyboard open/close
      const handleResize = () => {
        const height = window.innerHeight;
        const width = window.innerWidth;
        
        if (height < width * 0.8) {
          // Keyboard is likely open
          document.body.classList.add('keyboard-open');
        } else {
          document.body.classList.remove('keyboard-open');
        }
      };

      window.addEventListener('resize', handleResize);
      window.addEventListener('orientationchange', handleResize);
    }
  }

  setupTouchOptimizations() {
    // Add touch-action to scrollable elements
    const scrollableElements = document.querySelectorAll('.overflow-y-auto, .overflow-auto');
    scrollableElements.forEach(element => {
      element.style.touchAction = 'pan-y';
    });

    // Prevent zoom on double tap
    let lastTouchEnd = 0;
    document.addEventListener('touchend', (event) => {
      const now = (new Date()).getTime();
      if (now - lastTouchEnd <= 300) {
        event.preventDefault();
      }
      lastTouchEnd = now;
    }, false);
  }

  navigateToSection(section) {
    if (this.sections.includes(section)) {
      this.currentSection = section;
      this.updateActiveSection();
      
      // Map section names to the app's navigation
      const sectionMap = {
        'dashboard': 'dashSec',
        'billing': 'billingSec',
        'products': 'productSec',
        'employees': 'employeeSec'
      };
      
      const targetSection = sectionMap[section];
      if (section === 'more') {
        this.showMoreMenu();
        return;
      }
      if (targetSection) {
        // Use the existing app navigation
        const navButton = document.querySelector(`[data-go="${targetSection}"]`);
        if (navButton) {
          navButton.click();
          console.log(`Mobile Navigation: Navigated to ${section} (${targetSection})`);
        } else {
          console.warn(`Mobile Navigation: Navigation button for ${targetSection} not found`);
        }
      }
      
      // Trigger section change event
      window.dispatchEvent(new CustomEvent('sectionChanged', {
        detail: { section: section }
      }));
    }
  }

  showMoreMenu() {
    // Build lightweight bottom sheet with inline styles (no external CSS dependency)
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.inset = '0';
    overlay.style.background = 'rgba(0,0,0,0.5)';
    overlay.style.zIndex = '99999';

    const sheet = document.createElement('div');
    sheet.style.position = 'absolute';
    sheet.style.left = '0';
    sheet.style.right = '0';
    sheet.style.bottom = '0';
    sheet.style.background = '#111827'; // neutral-900
    sheet.style.borderTop = '1px solid #374151'; // neutral-700
    sheet.style.borderRadius = '12px 12px 0 0';
    sheet.style.padding = '16px';
    sheet.style.color = '#e5e7eb';

    sheet.innerHTML = `
      <div style="text-align:center;font-weight:600;margin-bottom:8px;">More</div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <button data-action="customers" style="padding:12px;border:1px solid #374151;border-radius:8px;background:#1f2937;color:#e5e7eb;text-align:left;">Customers</button>
        <button data-action="reports" style="padding:12px;border:1px solid #374151;border-radius:8px;background:#1f2937;color:#e5e7eb;text-align:left;">Reports</button>
        <button data-action="expenses" style="padding:12px;border:1px solid #374151;border-radius:8px;background:#1f2937;color:#e5e7eb;text-align:left;">Expenses</button>
        <button data-action="settings" style="padding:12px;border:1px solid #374151;border-radius:8px;background:#1f2937;color:#e5e7eb;text-align:left;">Shop Settings</button>
        <button data-action="product-types" style="padding:12px;border:1px solid #374151;border-radius:8px;background:#1f2937;color:#e5e7eb;text-align:left;">Product Types</button>
        <button data-action="close" style="padding:12px;border:1px solid #4b5563;border-radius:8px;background:#111827;color:#9ca3af;text-align:center;">Close</button>
      </div>
    `;

    overlay.appendChild(sheet);
    document.body.appendChild(overlay);

    const handleClose = () => {
      if (overlay && overlay.parentElement) overlay.parentElement.removeChild(overlay);
    };

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) handleClose();
    });

    sheet.addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-action]');
      if (!btn) return;
      const action = btn.getAttribute('data-action');
      if (action === 'close') { handleClose(); return; }
      const map = {
        customers: 'customerSec',
        reports: 'advancedReportsSec',
        expenses: 'expenses',
        settings: 'shopSettingsSec',
        'product-types': 'productTypeSec'
      };
      const target = map[action];
      if (target) {
        if (target === 'expenses') {
          // Navigate to expenses page
          window.location.href = '/expenses';
        } else {
          const navButton = document.querySelector(`[data-go="${target}"]`);
          if (navButton) navButton.click();
        }
      }
      handleClose();
    });
  }

  updateActiveSection() {
    const navItems = document.querySelectorAll('.mobile-nav-item');
    navItems.forEach(item => {
      item.classList.remove('active');
      if (item.dataset.section === this.currentSection) {
        item.classList.add('active');
      }
    });
  }

  showSection(section) {
    // Hide all sections
    const sections = document.querySelectorAll('[data-section]');
    sections.forEach(s => {
      s.style.display = 'none';
    });

    // Show target section
    const targetSection = document.querySelector(`[data-section="${section}"]`);
    if (targetSection) {
      targetSection.style.display = 'block';
      targetSection.classList.add('fade-in-mobile');
    }

    // Update URL hash
    window.location.hash = section;
  }

  // Mobile-specific utility methods
  showMobileModal(content, options = {}) {
    const modal = document.createElement('div');
    modal.className = 'modal-mobile';
    modal.innerHTML = `
      <div class="modal-mobile-content">
        <div class="modal-mobile-header">
          <h3 class="text-lg font-semibold">${options.title || 'Action'}</h3>
        </div>
        <div class="modal-mobile-body">
          ${content}
        </div>
        <div class="modal-mobile-footer">
          ${options.showCancel ? '<button class="btn-secondary-mobile" onclick="this.closest(\'.modal-mobile\').remove()">Cancel</button>' : ''}
          ${options.confirmText ? `<button class="btn-primary-mobile" onclick="this.closest('.modal-mobile').dispatchEvent(new CustomEvent('confirm'))">${options.confirmText}</button>` : ''}
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    // Auto-remove on backdrop click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });

    return modal;
  }

  showMobileNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification-mobile ${type === 'error' ? 'bg-red-500 text-white' : type === 'success' ? 'bg-green-500 text-white' : 'bg-blue-500 text-white'}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Show notification
    setTimeout(() => {
      notification.classList.add('show');
    }, 100);

    // Hide and remove
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        if (notification.parentElement) {
          notification.remove();
        }
      }, 300);
    }, duration);
  }

  // Mobile-optimized form handling
  setupMobileForm(formSelector) {
    const form = document.querySelector(formSelector);
    if (!form) return;

    // Add mobile classes
    form.classList.add('form-mobile');

    // Optimize inputs
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
      input.classList.add('input-mobile');
      
      // Prevent zoom on iOS
      if (input.type === 'text' || input.type === 'email' || input.type === 'password') {
        input.style.fontSize = '16px';
      }
    });

    // Optimize buttons
    const buttons = form.querySelectorAll('button');
    buttons.forEach(button => {
      if (button.type === 'submit') {
        button.classList.add('btn-primary-mobile');
      } else {
        button.classList.add('btn-secondary-mobile');
      }
    });
  }

  // Mobile-optimized list handling
  setupMobileList(listSelector) {
    const list = document.querySelector(listSelector);
    if (!list) return;

    list.classList.add('list-mobile');
    
    const items = list.querySelectorAll('li, .list-item');
    items.forEach(item => {
      item.classList.add('list-item-mobile');
      
      // Add touch feedback
      item.addEventListener('touchstart', () => {
        item.style.transform = 'scale(0.98)';
      });
      
      item.addEventListener('touchend', () => {
        item.style.transform = 'scale(1)';
      });
    });
  }

  // Get current section
  getCurrentSection() {
    return this.currentSection;
  }

  // Check if running on mobile
  isMobile() {
    return window.innerWidth <= 768;
  }

  // Check if running on tablet
  isTablet() {
    return window.innerWidth > 768 && window.innerWidth <= 1024;
  }

  // Check if running on desktop
  isDesktop() {
    return window.innerWidth > 1024;
  }

  // Get device orientation
  getOrientation() {
    return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
  }

  // Manual initialization method
  static async initializeMobileNavigation() {
    const mobileNav = new MobileNavigation();
    await mobileNav.init();
    return mobileNav;
  }
}

// Make mobile navigation available globally
window.MobileNavigation = MobileNavigation;

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MobileNavigation;
} 