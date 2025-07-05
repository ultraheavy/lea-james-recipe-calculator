// Elegant SVG Icon Library for Food Categories
const foodIcons = {
  protein: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3"/>
    <path d="M11 3C11 3 13 5 13 8C13 11 11 13 11 13"/>
    <path d="M11 3C11 3 9 5 9 8C9 11 11 13 11 13"/>
    <circle cx="18" cy="5" r="3"/>
  </svg>`,
  
  dairy: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M8 2v4m8-4v4"/>
    <path d="M5 6h14l-1 7H6L5 6z"/>
    <path d="M6 13v7a2 2 0 002 2h8a2 2 0 002-2v-7"/>
    <circle cx="12" cy="17" r="1"/>
  </svg>`,
  
  produce: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
    <path d="M12 2v7"/>
    <path d="M9 5l3 3 3-3"/>
  </svg>`,
  
  grains: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 2v20M8 4l4-2 4 2M6 8l6-4 6 4M4 12l8-6 8 6M4 16l8-4 8 4"/>
  </svg>`,
  
  beverage: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 12V7a1 1 0 011-1h12a1 1 0 011 1v5M5 12l2 7h10l2-7M5 12h14"/>
    <path d="M9 6V3m6 3V3"/>
  </svg>`,
  
  spices: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="3"/>
    <path d="M12 3v6m0 6v6M3 12h6m6 0h6"/>
    <path d="M5.64 5.64l4.24 4.24m4.24 4.24l4.24 4.24M18.36 5.64l-4.24 4.24m-4.24 4.24l-4.24 4.24"/>
  </svg>`,
  
  oil: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M9 2h6v5l-1.5 1.5a2.12 2.12 0 00-.5 1.5v12H11V10a2.12 2.12 0 00-.5-1.5L9 7V2z"/>
    <path d="M9 2h6M11 22h2"/>
  </svg>`,
  
  frozen: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 2v20m8-10H4"/>
    <path d="M16.24 7.76L7.76 16.24m0-8.48l8.48 8.48"/>
    <circle cx="12" cy="12" r="2"/>
  </svg>`,
  
  dessert: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 21v-8a4 4 0 00-4-4H8a4 4 0 00-4 4v8"/>
    <path d="M4 21h16M12 9V3"/>
    <circle cx="12" cy="3" r="1"/>
    <path d="M8 13h8"/>
  </svg>`,
  
  seafood: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M18 12c0-4-3-6-6-6s-6 2-6 6c0 4 3 6 6 6"/>
    <path d="M18 12l3 3-3 3"/>
    <circle cx="9" cy="11" r="1"/>
    <path d="M6 7s2-1 6-1 6 1 6 1"/>
  </svg>`,
  
  sauce: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10 2h4v6h-4z"/>
    <path d="M8 8h8a1 1 0 011 1v11a2 2 0 01-2 2H9a2 2 0 01-2-2V9a1 1 0 011-1z"/>
    <path d="M10 13h4"/>
  </svg>`,
  
  misc: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2"/>
    <path d="M9 9h6v6H9z"/>
  </svg>`
};

// Function to get icon based on category
function getCategoryIcon(category) {
  if (!category) return foodIcons.misc;
  
  const categoryLower = category.toLowerCase();
  
  if (categoryLower.includes('protein') || categoryLower.includes('meat') || 
      categoryLower.includes('chicken') || categoryLower.includes('beef') || 
      categoryLower.includes('pork')) {
    return foodIcons.protein;
  }
  
  if (categoryLower.includes('dairy') || categoryLower.includes('milk') || 
      categoryLower.includes('cheese') || categoryLower.includes('egg')) {
    return foodIcons.dairy;
  }
  
  if (categoryLower.includes('produce') || categoryLower.includes('vegetable') || 
      categoryLower.includes('fruit') || categoryLower.includes('lettuce')) {
    return foodIcons.produce;
  }
  
  if (categoryLower.includes('grain') || categoryLower.includes('bread') || 
      categoryLower.includes('flour') || categoryLower.includes('rice')) {
    return foodIcons.grains;
  }
  
  if (categoryLower.includes('beverage') || categoryLower.includes('drink') || 
      categoryLower.includes('soda') || categoryLower.includes('juice')) {
    return foodIcons.beverage;
  }
  
  if (categoryLower.includes('spice') || categoryLower.includes('seasoning') || 
      categoryLower.includes('herb')) {
    return foodIcons.spices;
  }
  
  if (categoryLower.includes('oil') || categoryLower.includes('butter') || 
      categoryLower.includes('fat')) {
    return foodIcons.oil;
  }
  
  if (categoryLower.includes('frozen') || categoryLower.includes('ice')) {
    return foodIcons.frozen;
  }
  
  if (categoryLower.includes('dessert') || categoryLower.includes('cake') || 
      categoryLower.includes('sweet')) {
    return foodIcons.dessert;
  }
  
  if (categoryLower.includes('fish') || categoryLower.includes('seafood') || 
      categoryLower.includes('shrimp')) {
    return foodIcons.seafood;
  }
  
  if (categoryLower.includes('sauce') || categoryLower.includes('dressing') || 
      categoryLower.includes('condiment')) {
    return foodIcons.sauce;
  }
  
  return foodIcons.misc;
}

// Function to create icon element
function createFoodIcon(category, size = 'default') {
  const icon = document.createElement('div');
  icon.className = `food-icon ${size === 'sm' ? 'food-icon-sm' : size === 'lg' ? 'food-icon-lg' : ''}`;
  
  // Determine icon class
  const categoryLower = (category || '').toLowerCase();
  let iconClass = 'icon-misc';
  
  if (categoryLower.includes('protein') || categoryLower.includes('meat')) iconClass = 'icon-protein';
  else if (categoryLower.includes('dairy') || categoryLower.includes('egg')) iconClass = 'icon-dairy';
  else if (categoryLower.includes('produce') || categoryLower.includes('vegetable')) iconClass = 'icon-produce';
  else if (categoryLower.includes('grain') || categoryLower.includes('bread')) iconClass = 'icon-grains';
  else if (categoryLower.includes('beverage') || categoryLower.includes('drink')) iconClass = 'icon-beverage';
  else if (categoryLower.includes('spice') || categoryLower.includes('herb')) iconClass = 'icon-spices';
  else if (categoryLower.includes('oil') || categoryLower.includes('fat')) iconClass = 'icon-oil';
  else if (categoryLower.includes('frozen')) iconClass = 'icon-frozen';
  else if (categoryLower.includes('dessert') || categoryLower.includes('sweet')) iconClass = 'icon-dessert';
  else if (categoryLower.includes('fish') || categoryLower.includes('seafood')) iconClass = 'icon-seafood';
  else if (categoryLower.includes('sauce') || categoryLower.includes('dressing')) iconClass = 'icon-sauce';
  
  icon.classList.add(iconClass);
  icon.innerHTML = getCategoryIcon(category);
  
  return icon;
}

// Initialize icons on page load
document.addEventListener('DOMContentLoaded', function() {
  // Auto-generate icons for elements with data-category attribute
  document.querySelectorAll('[data-category]').forEach(element => {
    const category = element.getAttribute('data-category');
    const iconContainer = element.querySelector('.icon-container');
    if (iconContainer && !iconContainer.querySelector('.food-icon')) {
      iconContainer.appendChild(createFoodIcon(category));
    }
  });
});