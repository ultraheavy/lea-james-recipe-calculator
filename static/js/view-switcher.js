// View Switcher Functionality
class ViewSwitcher {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.currentView = localStorage.getItem(`view-${containerId}`) || options.defaultView || 'table';
        this.views = options.views || ['table', 'card', 'list'];
        this.onViewChange = options.onViewChange || null;
        
        this.init();
    }
    
    init() {
        this.render();
        this.attachEventListeners();
        this.applyView(this.currentView);
    }
    
    render() {
        const switcher = document.createElement('div');
        switcher.className = 'view-switcher';
        
        // Table View Button
        if (this.views.includes('table')) {
            switcher.innerHTML += `
                <button data-view="table" class="${this.currentView === 'table' ? 'active' : ''}" title="Table View">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <line x1="3" y1="9" x2="21" y2="9"/>
                        <line x1="3" y1="15" x2="21" y2="15"/>
                        <line x1="9" y1="3" x2="9" y2="21"/>
                        <line x1="15" y1="3" x2="15" y2="21"/>
                    </svg>
                    <span>Table</span>
                </button>
            `;
        }
        
        // Card View Button
        if (this.views.includes('card')) {
            switcher.innerHTML += `
                <button data-view="card" class="${this.currentView === 'card' ? 'active' : ''}" title="Card View">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="7" height="7" rx="1"/>
                        <rect x="14" y="3" width="7" height="7" rx="1"/>
                        <rect x="3" y="14" width="7" height="7" rx="1"/>
                        <rect x="14" y="14" width="7" height="7" rx="1"/>
                    </svg>
                    <span>Cards</span>
                </button>
            `;
        }
        
        // List View Button
        if (this.views.includes('list')) {
            switcher.innerHTML += `
                <button data-view="list" class="${this.currentView === 'list' ? 'active' : ''}" title="List View">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="8" y1="6" x2="21" y2="6"/>
                        <line x1="8" y1="12" x2="21" y2="12"/>
                        <line x1="8" y1="18" x2="21" y2="18"/>
                        <line x1="3" y1="6" x2="3.01" y2="6"/>
                        <line x1="3" y1="12" x2="3.01" y2="12"/>
                        <line x1="3" y1="18" x2="3.01" y2="18"/>
                    </svg>
                    <span>List</span>
                </button>
            `;
        }
        
        this.container.appendChild(switcher);
    }
    
    attachEventListeners() {
        const buttons = this.container.querySelectorAll('.view-switcher button');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const view = button.getAttribute('data-view');
                this.switchView(view);
            });
        });
    }
    
    switchView(view) {
        if (view === this.currentView) return;
        
        // Update active button
        const buttons = this.container.querySelectorAll('.view-switcher button');
        buttons.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-view') === view);
        });
        
        // Save preference
        this.currentView = view;
        localStorage.setItem(`view-${this.container.id}`, view);
        
        // Apply view
        this.applyView(view);
        
        // Call callback if provided
        if (this.onViewChange) {
            this.onViewChange(view);
        }
    }
    
    applyView(view) {
        const contentArea = document.querySelector('.view-content') || document.querySelector('.main-content');
        if (!contentArea) return;
        
        // Add transition class
        contentArea.classList.add('view-transition');
        
        // Remove transition class after animation
        setTimeout(() => {
            contentArea.classList.remove('view-transition');
        }, 300);
        
        // Apply view-specific classes to body or container
        document.body.setAttribute('data-view', view);
    }
}

// Helper function to convert table to cards
function convertTableToCards(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return null;
    
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    const headers = Array.from(thead.querySelectorAll('th')).map(th => th.textContent.trim());
    const rows = tbody.querySelectorAll('tr');
    
    const cardGrid = document.createElement('div');
    cardGrid.className = 'card-grid';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const card = createItemCard(cells, headers);
        if (card) cardGrid.appendChild(card);
    });
    
    return cardGrid;
}

// Helper function to convert table to list
function convertTableToList(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return null;
    
    const tbody = table.querySelector('tbody');
    const rows = tbody.querySelectorAll('tr');
    
    const listView = document.createElement('div');
    listView.className = 'list-view';
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const listItem = createListItem(cells);
        if (listItem) listView.appendChild(listItem);
    });
    
    return listView;
}

// Create item card from table row cells
function createItemCard(cells, headers) {
    // This function should be customized based on the specific table structure
    // Here's a generic implementation
    const card = document.createElement('div');
    card.className = 'item-card';
    
    // Extract data from cells based on headers
    let html = '<div class="item-card-body">';
    
    cells.forEach((cell, index) => {
        if (index < headers.length - 1 && headers[index] !== 'Actions') {
            html += `
                <div class="item-card-row">
                    <span class="item-card-label">${headers[index]}</span>
                    <span class="item-card-value">${cell.innerHTML}</span>
                </div>
            `;
        }
    });
    
    // Add actions if present
    const actionsCell = cells[cells.length - 1];
    if (actionsCell && actionsCell.querySelector('a, button')) {
        html += '<div class="item-card-actions">';
        html += actionsCell.innerHTML;
        html += '</div>';
    }
    
    html += '</div>';
    card.innerHTML = html;
    
    return card;
}

// Create list item from table row cells
function createListItem(cells) {
    const listItem = document.createElement('div');
    listItem.className = 'list-item';
    
    // Generic implementation - customize based on table structure
    const title = cells[0] ? cells[0].textContent.trim() : '';
    const subtitle = cells[1] ? cells[1].textContent.trim() : '';
    const meta = cells[2] ? cells[2].textContent.trim() : '';
    
    listItem.innerHTML = `
        <div class="list-item-content">
            <div class="list-item-title">${title}</div>
            ${subtitle ? `<div class="list-item-subtitle">${subtitle}</div>` : ''}
        </div>
        ${meta ? `<div class="list-item-meta">${meta}</div>` : ''}
    `;
    
    return listItem;
}