;(function () {
  var COUNTRY_CODES_VERSION = 'v1';
  window.countryCodes = [];
  async function loadCountryCodes() {
    try {
      var cached = localStorage.getItem('countryCodes_' + COUNTRY_CODES_VERSION);
      if (cached) {
        var parsed = JSON.parse(cached);
        if (Array.isArray(parsed) && parsed.length > 0) {
          window.countryCodes = parsed;
          return;
        }
      }
      var response = await fetch('/static/data/countryCodes.json');
      if (!response.ok) {
        throw new Error('HTTP error');
      }
      var data = await response.json();
      if (Array.isArray(data) && data.length > 0) {
        window.countryCodes = data;
        localStorage.setItem('countryCodes_' + COUNTRY_CODES_VERSION, JSON.stringify(window.countryCodes));
        return;
      }
      throw new Error('Invalid data');
    } catch (error) {
      window.countryCodes = [
        { code: "+971", country: "UAE", flag: "🇦🇪" },
        { code: "+91", country: "India", flag: "🇮🇳" },
        { code: "+966", country: "Saudi Arabia", flag: "🇸🇦" },
        { code: "+973", country: "Bahrain", flag: "🇧🇭" },
        { code: "+968", country: "Oman", flag: "🇴🇲" },
        { code: "+965", country: "Kuwait", flag: "🇰🇼" },
        { code: "+974", country: "Qatar", flag: "🇶🇦" },
        { code: "+1", country: "USA", flag: "🇺🇸" },
        { code: "+44", country: "UK", flag: "🇬🇧" },
        { code: "+20", country: "Egypt", flag: "🇪🇬" },
        { code: "+92", country: "Pakistan", flag: "🇵🇰" },
        { code: "+63", country: "Philippines", flag: "🇵🇭" },
        { code: "+880", country: "Bangladesh", flag: "🇧🇩" }
      ];
      localStorage.setItem('countryCodes_' + COUNTRY_CODES_VERSION, JSON.stringify(window.countryCodes));
    }
  }
  function getCombinedPhoneNumber() {
    var codeBtn = document.getElementById('countryCodeText');
    var mobileInput = document.getElementById('billMobile');
    if (!mobileInput) return '';
    var code = codeBtn ? codeBtn.textContent.trim() : '+971';
    var number = mobileInput.value.trim();
    if (!number) return '';
    if (number.startsWith('+')) return number;
    var cleanNumber = number.replace(/^0+/, '');
    return code + cleanNumber;
  }
  function parsePhoneNumber(fullNumber) {
    if (!fullNumber) return { code: '+971', number: '' };
    var normalized = fullNumber;
    if (normalized.startsWith('++')) {
      normalized = normalized.replace(/^\++/, '+');
    } else if (!normalized.startsWith('+')) {
      normalized = '+' + normalized;
    }
    var sortedCodes = window.countryCodes.slice().sort(function (a, b) { return b.code.length - a.code.length; });
    for (var i = 0; i < sortedCodes.length; i++) {
      var country = sortedCodes[i];
      if (normalized.startsWith(country.code)) {
        return { code: country.code, number: normalized.slice(country.code.length) };
      }
    }
    return { code: '+971', number: normalized.replace(/^\+971/, '') };
  }
  function setupCountryCodeSelector() {
    var btn = document.getElementById('countryCodeBtn');
    var flagSpan = document.getElementById('countryFlag');
    var codeSpan = document.getElementById('countryCodeText');
    var input = document.getElementById('billMobile');
    if (!btn) return;
    var modal = null;
    var searchInput = null;
    var optionsContainer = null;
    function createModal() {
      if (modal) return modal;
      modal = document.createElement('div');
      modal.className = 'absolute bg-neutral-900 border border-neutral-700 rounded-lg shadow-lg z-50 w-full max-w-md overflow-hidden';
      modal.style.display = 'none';
      modal.innerHTML = '<div class="p-2 border-b border-neutral-700"><input type="text" placeholder="Search countries..." class="search-input w-full bg-neutral-800 border border-neutral-600 rounded px-2 py-1 text-white placeholder-neutral-400 focus:ring-2 focus:ring-indigo-400/60 focus:border-transparent text-sm"></div><div class="options-container max-h-48 overflow-y-auto p-1">' + renderOptions(window.countryCodes) + '</div>';
      document.body.appendChild(modal);
      searchInput = modal.querySelector('.search-input');
      optionsContainer = modal.querySelector('.options-container');
      searchInput.addEventListener('input', function (e) {
        var query = e.target.value.toLowerCase().trim();
        var filtered = window.countryCodes.filter(function (c) { return c.country.toLowerCase().includes(query) || c.code.toLowerCase().includes(query); });
        optionsContainer.innerHTML = renderOptions(filtered);
      });
      return modal;
    }
    function renderOptions(countries) {
      return countries.map(function (c) {
        return '<div class="country-option px-3 py-2 hover:bg-neutral-700 cursor-pointer flex items-center gap-3 transition-colors rounded-lg" data-code="' + c.code + '" data-flag="' + c.flag + '"><span class="text-lg">' + c.flag + '</span><span class="text-white font-medium w-12">' + c.code + '</span><span class="text-neutral-400 text-sm truncate">' + c.country + '</span></div>';
      }).join('');
    }
    function showModal() {
      if (!modal) createModal();
      var rect = btn.getBoundingClientRect();
      modal.style.left = rect.left + 'px';
      modal.style.top = (rect.bottom + 4) + 'px';
      modal.style.width = Math.max(rect.width, 200) + 'px';
      modal.style.display = 'block';
      if (searchInput) {
        searchInput.focus();
        searchInput.value = '';
        optionsContainer.innerHTML = renderOptions(window.countryCodes);
      }
    }
    function hideModal() {
      if (modal) {
        modal.style.display = 'none';
      }
    }
    function handleSelection(code, flag) {
      if (codeSpan) codeSpan.textContent = code;
      if (flagSpan) flagSpan.textContent = flag;
      hideModal();
      if (input) input.focus();
      if (input && input.value) {
        input.dispatchEvent(new Event('input'));
      }
    }
    btn.addEventListener('click', function () { showModal(); });
    document.addEventListener('click', function (e) {
      if (!modal || modal.style.display === 'none') return;
      if (!modal.contains(e.target) && e.target !== btn) hideModal();
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hideModal(); });
    document.addEventListener('click', function (e) {
      if (modal && e.target.classList.contains('country-option')) {
        var code = e.target.getAttribute('data-code');
        var flag = e.target.getAttribute('data-flag');
        handleSelection(code, flag);
      }
    });
  }
  window.CountryCode = {
    loadCountryCodes: loadCountryCodes,
    setupPicker: setupCountryCodeSelector,
    getCombinedPhoneNumber: getCombinedPhoneNumber,
    parsePhoneNumber: parsePhoneNumber
  };

  // Export global helpers for backward compatibility
  window.getCombinedPhoneNumber = getCombinedPhoneNumber;
  window.parsePhoneNumber = parsePhoneNumber;
})();
