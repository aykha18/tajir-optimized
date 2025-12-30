// Lightweight City/Area Autocomplete module
// Extracted from billing-system.js for modularity
window.CityAreaAutocomplete = (function () {
  function setup() {
    const cityInput = document.getElementById('billCity');
    const areaInput = document.getElementById('billArea');
    if (!cityInput || !areaInput) return;

    let cityDropdown = null;
    let areaDropdown = null;
    let cityDebounce = null;
    let areaDebounce = null;

    function ensureCityDropdown() {
      if (cityDropdown) return;
      cityDropdown = document.createElement('div');
      cityDropdown.className = 'city-suggestion';
      cityDropdown.style.cssText =
        'position: fixed; z-index: 99999 !important; background: #1f2937; border: 1px solid #374151; border-radius: 8px; max-height: 240px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.3); display:none;';
      document.body.appendChild(cityDropdown);
      cityDropdown.addEventListener('click', e => e.stopPropagation());
    }

    function ensureAreaDropdown() {
      if (areaDropdown) return;
      areaDropdown = document.createElement('div');
      areaDropdown.className = 'area-suggestion';
      areaDropdown.style.cssText =
        'position: fixed; z-index: 99999 !important; background: #1f2937; border: 1px solid #374151; border-radius: 8px; max-height: 240px; overflow-y: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.3); display:none;';
      document.body.appendChild(areaDropdown);
      areaDropdown.addEventListener('click', e => e.stopPropagation());
    }

    function positionDropdown(dropdown, input) {
      const rect = input.getBoundingClientRect();
      dropdown.style.left = rect.left + 'px';
      dropdown.style.top = rect.bottom + 4 + 'px';
      dropdown.style.width = rect.width + 'px';
      dropdown.style.minWidth = '200px';
    }

    function animateShow(dropdown) {
      dropdown.style.display = 'block';
      dropdown.style.opacity = '0';
      dropdown.style.transform = 'translateY(-10px)';
      setTimeout(() => {
        dropdown.style.transition = 'all 0.2s ease';
        dropdown.style.opacity = '1';
        dropdown.style.transform = 'translateY(0)';
      }, 10);
    }

    function animateHide(dropdownRef, type) {
      const dd = dropdownRef;
      if (!dd) return;
      dd.style.transition = 'all 0.2s ease';
      dd.style.opacity = '0';
      dd.style.transform = 'translateY(-10px)';
      setTimeout(() => {
        dd.style.display = 'none';
        if (dd.parentNode) dd.parentNode.removeChild(dd);
        if (type === 'city') cityDropdown = null;
        if (type === 'area') areaDropdown = null;
      }, 200);
    }

    cityInput.addEventListener('input', function () {
      clearTimeout(cityDebounce);
      const query = this.value.trim();
      if (query.length < 2) {
        animateHide(cityDropdown, 'city');
        return;
      }
      cityDebounce = setTimeout(async () => {
        try {
          const res = await fetch('/api/cities');
          const cities = await res.json();
          const list = (cities || []).filter(c => c.toLowerCase().includes(query.toLowerCase()));
          ensureCityDropdown();
          positionDropdown(cityDropdown, cityInput);
          cityDropdown.innerHTML = list
            .map(c => `<div class="city-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" data-city="${c}">${c}</div>`)
            .join('');
          cityDropdown.querySelectorAll('.city-option').forEach(opt => {
            opt.addEventListener('click', e => {
              e.preventDefault();
              e.stopPropagation();
              const selected = opt.getAttribute('data-city');
              cityInput.value = selected;
              animateHide(cityDropdown, 'city');
              areaInput.value = '';
              updateAreasForCity(selected);
            });
          });
          animateShow(cityDropdown);
        } catch (e) {
          console.error('CityAreaAutocomplete: Error loading cities', e);
        }
      }, 300);
    });

    areaInput.addEventListener('input', function () {
      clearTimeout(areaDebounce);
      const query = this.value.trim();
      if (query.length < 2) {
        animateHide(areaDropdown, 'area');
        return;
      }
      areaDebounce = setTimeout(async () => {
        try {
          const city = cityInput.value.trim();
          const url = city ? `/api/areas?city=${encodeURIComponent(city)}` : '/api/areas';
          const res = await fetch(url);
          const areas = await res.json();
          const list = (areas || []).filter(a => a.toLowerCase().includes(query.toLowerCase()));
          ensureAreaDropdown();
          positionDropdown(areaDropdown, areaInput);
          areaDropdown.innerHTML = list
            .map(a => `<div class="area-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" data-area="${a}">${a}</div>`)
            .join('');
          areaDropdown.querySelectorAll('.area-option').forEach(opt => {
            opt.addEventListener('click', async e => {
              e.preventDefault();
              e.stopPropagation();
              const selected = opt.getAttribute('data-area');
              areaInput.value = selected;
              animateHide(areaDropdown, 'area');
              if (!cityInput.value.trim()) {
                await findCityForArea(selected);
              }
            });
          });
          animateShow(areaDropdown);
        } catch (e) {
          console.error('CityAreaAutocomplete: Error loading areas', e);
        }
      }, 300);
    });

    document.addEventListener('click', function (e) {
      if (e.target.closest('.city-option') || e.target.closest('.area-option')) return;
      if (cityInput.contains(e.target) || areaInput.contains(e.target)) return;
      if (!cityInput.contains(e.target) && (!cityDropdown || !cityDropdown.contains(e.target))) {
        animateHide(cityDropdown, 'city');
      }
      if (!areaInput.contains(e.target) && (!areaDropdown || !areaDropdown.contains(e.target))) {
        animateHide(areaDropdown, 'area');
      }
    });

    async function updateAreasForCity(city) {
      try {
        const res = await fetch(`/api/areas?city=${encodeURIComponent(city)}`);
        const areas = await res.json();
        ensureAreaDropdown();
        positionDropdown(areaDropdown, areaInput);
        if ((areas || []).length > 0) {
          areaDropdown.innerHTML = areas
            .map(a => `<div class="area-option px-4 py-2 hover:bg-neutral-700 cursor-pointer border-b border-neutral-600 last:border-b-0" data-area="${a}">${a}</div>`)
            .join('');
        } else {
          areaDropdown.innerHTML = '<div class="px-4 py-2 text-neutral-400 text-sm">No areas found for this city</div>';
        }
        animateShow(areaDropdown);
        setTimeout(() => animateHide(areaDropdown, 'area'), 2000);
      } catch (e) {
        console.error('CityAreaAutocomplete: Error updating areas for city', e);
      }
    }

    async function findCityForArea(area) {
      try {
        const res = await fetch(`/api/cities?area=${encodeURIComponent(area)}`);
        const cities = await res.json();
        if ((cities || []).length > 0) {
          cityInput.value = cities[0];
        }
      } catch (e) {
        console.error('CityAreaAutocomplete: Error finding city for area', e);
      }
    }
  }

  return { setup };
})();

