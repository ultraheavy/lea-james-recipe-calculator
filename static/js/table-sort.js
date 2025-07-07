// Reusable table sorting functionality
function sortTable(columnIndex, tableId = null) {
    const table = tableId ? document.getElementById(tableId) : document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr')).filter(row => !row.querySelector('td[colspan]'));
    
    // Determine sort direction
    const th = table.querySelectorAll('thead th')[columnIndex];
    const isAscending = !th.classList.contains('sort-asc');
    
    // Remove all sort indicators
    table.querySelectorAll('thead th').forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
        const indicator = header.querySelector('.sort-indicator');
        if (indicator) {
            indicator.textContent = '↕';
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
        
        // Handle price columns (remove $ and convert to number)
        if (aValue.includes('$')) {
            aValue = parseFloat(aValue.replace(/[$,]/g, '')) || 0;
            bValue = parseFloat(bValue.replace(/[$,]/g, '')) || 0;
        }
        // Handle percentage columns
        else if (aValue.includes('%')) {
            aValue = parseFloat(aValue.replace('%', '')) || 0;
            bValue = parseFloat(bValue.replace('%', '')) || 0;
        }
        // Handle date columns (various formats)
        else if (aValue.match(/^\d{4}-\d{2}-\d{2}$/) || 
                 aValue.match(/^\d{1,2}\/\d{1,2}\/\d{4}$/) ||
                 aValue.match(/^\d{1,2}\/\d{1,2}\/\d{2}$/)) {
            aValue = new Date(aValue).getTime() || 0;
            bValue = new Date(bValue).getTime() || 0;
        }
        // Try to parse as number if it looks numeric
        else if (!isNaN(parseFloat(aValue)) && !isNaN(parseFloat(bValue))) {
            aValue = parseFloat(aValue);
            bValue = parseFloat(bValue);
        }
        // Handle N/A and empty values for strings
        else {
            if (aValue === '-' || aValue === 'N/A' || aValue === '') {
                aValue = '';
            }
            if (bValue === '-' || bValue === 'N/A' || bValue === '') {
                bValue = '';
            }
        }
        
        // Numeric comparison
        if (typeof aValue === 'number' && typeof bValue === 'number') {
            return isAscending ? aValue - bValue : bValue - aValue;
        }
        
        // String comparison (empty values go to bottom)
        if (aValue === '' && bValue !== '') return 1;
        if (aValue !== '' && bValue === '') return -1;
        
        return isAscending ? 
            aValue.toString().localeCompare(bValue.toString()) : 
            bValue.toString().localeCompare(aValue.toString());
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// Initialize sortable tables
function initSortableTables(tableId = null) {
    const tables = tableId ? [document.getElementById(tableId)] : document.querySelectorAll('table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('thead th');
        headers.forEach((header, index) => {
            // Skip the Actions column and already initialized headers
            if (header.textContent.trim() !== 'Actions' && !header.hasAttribute('data-sortable')) {
                header.style.cursor = 'pointer';
                header.style.userSelect = 'none';
                header.style.position = 'relative';
                header.setAttribute('data-sortable', 'true');
                
                // Create a unique handler for this table and column
                header.onclick = () => sortTable(index, table.id);
                
                // Add visual indicator
                const indicator = document.createElement('span');
                indicator.className = 'sort-indicator';
                indicator.style.marginLeft = '5px';
                indicator.style.fontSize = '12px';
                indicator.style.opacity = '0.5';
                indicator.innerHTML = '↕';
                header.appendChild(indicator);
            }
        });
    });
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initSortableTables();
});