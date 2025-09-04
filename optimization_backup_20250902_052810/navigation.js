// Simple Navigation Module for Tajir POS
// This is a minimal navigation module that doesn't interfere with existing functionality

console.log('🚀 Navigation module loaded (minimal version)');

// Don't override existing navigation - just provide basic functionality
window.mainNavigation = {
  init: function() {
    console.log('✅ Minimal navigation initialized');
  },
  
  // Simple section visibility helper
  showSection: function(sectionId) {
    console.log(`👁️ Showing section: ${sectionId}`);
    const section = document.getElementById(sectionId);
    if (section) {
      section.style.display = 'block';
      section.classList.remove('hidden');
    }
  },
  
  hideSection: function(sectionId) {
    console.log(`👁️ Hiding section: ${sectionId}`);
    const section = document.getElementById(sectionId);
    if (section) {
      section.style.display = 'none';
      section.classList.add('hidden');
    }
  }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.mainNavigation.init();
  });
} else {
  window.mainNavigation.init();
}
