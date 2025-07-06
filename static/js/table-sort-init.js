// Initialize table sorting on all tables
document.addEventListener('DOMContentLoaded', function() {
    // Find all tables with sortable class or all tables if none specified
    const tables = document.querySelectorAll('table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('thead th');
        
        headers.forEach((header, index) => {
            // Skip action columns
            if (header.textContent.toLowerCase().includes('action')) {
                return;
            }
            
            // Add cursor pointer to indicate clickable
            header.style.cursor = 'pointer';
            header.title = 'Click to sort';
            
            // Add click handler
            header.addEventListener('click', function() {
                sortTable(index, table.id);
            });
            
            // Add sort indicator
            if (!header.querySelector('.sort-indicator')) {
                header.innerHTML += ' <span class="sort-indicator">↕️</span>';
            }
        });
    });
});

// Enhanced table sorting with better number/currency handling
function enhancedSortTable(columnIndex, tableId = null) {
    const table = tableId ? document.getElementById(tableId) : document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr')).filter(row => !row.querySelector('td[colspan]'));
    
    // Determine sort direction
    const th = table.querySelectorAll('thead th')[columnIndex];
    const isAscending = !th.classList.contains('sort-asc');
    
    // Update sort indicators
    table.querySelectorAll('thead th').forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
        const indicator = header.querySelector('.sort-indicator');
        if (indicator) {
            indicator.textContent = '↕️';
        }
    });
    
    // Add sort indicator to current column
    th.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    const currentIndicator = th.querySelector('.sort-indicator');
    if (currentIndicator) {
        currentIndicator.textContent = isAscending ? '↑' : '↓';
    }
    
    // Sort rows
    rows.sort((a, b) => {
        const aCell = a.cells[columnIndex];
        const bCell = b.cells[columnIndex];
        
        let aValue = aCell.textContent.trim();
        let bValue = bCell.textContent.trim();
        
        // Handle currency/price columns
        if (aValue.includes('$') || bValue.includes('$')) {
            aValue = parseFloat(aValue.replace(/[$,]/g, '')) || 0;
            bValue = parseFloat(bValue.replace(/[$,]/g, '')) || 0;
        }
        // Handle percentage columns
        else if (aValue.includes('%') || bValue.includes('%')) {
            aValue = parseFloat(aValue.replace(/%/g, '')) || 0;
            bValue = parseFloat(bValue.replace(/%/g, '')) || 0;
        }
        // Handle numeric columns
        else if (!isNaN(aValue) && !isNaN(bValue)) {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
        }
        // Handle text columns (case insensitive)
        else {
            aValue = aValue.toLowerCase();
            bValue = bValue.toLowerCase();
        }
        
        // Compare values
        if (aValue < bValue) {
            return isAscending ? -1 : 1;
        }
        if (aValue > bValue) {
            return isAscending ? 1 : -1;
        }
        return 0;
    });
    
    // Clear and re-append sorted rows
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Override the existing sortTable function if it exists
if (typeof sortTable !== 'undefined') {
    sortTable = enhancedSortTable;
}