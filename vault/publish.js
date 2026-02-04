// Favicon Support for Obsidian Publish
(function() {
  function addFavicon() {
    // Remove any existing favicons
    document.querySelectorAll('link[rel*="icon"]').forEach(el => el.remove());
    
    // Add favicon links
    const sizes = [
      { rel: 'icon', type: 'image/x-icon', href: '/Images/favicon/favicon.ico' },
      { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/Images/favicon/favicon-16x16.png' },
      { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/Images/favicon/favicon-32x32.png' },
      { rel: 'icon', type: 'image/png', sizes: '192x192', href: '/Images/favicon/favicon-192x192.png' },
      { rel: 'apple-touch-icon', sizes: '256x256', href: '/Images/favicon/favicon-256x256.png' }
    ];
    
    sizes.forEach(icon => {
      const link = document.createElement('link');
      link.rel = icon.rel;
      if (icon.type) link.type = icon.type;
      if (icon.sizes) link.sizes = icon.sizes;
      link.href = icon.href;
      document.head.appendChild(link);
    });
  }
  
  // Run immediately
  addFavicon();
})();

// Sortable Tables for Obsidian Publish
// Click column headers to sort

(function() {
  // Pages where we skip sorting entirely (tables are intentionally ordered)
  function isWelcomePage() {
    // Check URL path
    const path = window.location.pathname.toLowerCase();
    const hash = window.location.hash.toLowerCase();
    
    // Check document title
    const title = document.title.toLowerCase();
    
    // Check for Welcome page heading
    const h1 = document.querySelector('h1');
    const hasWelcomeHeading = h1 && h1.textContent.toLowerCase().includes('welcome');
    
    // Check for the specific Welcome page intro text
    const hasWelcomeContent = document.body.textContent.includes('Pull up a pixelated barstool');
    
    return path === '/' || 
           path === '/welcome' || 
           path.endsWith('/welcome') ||
           hash.includes('welcome') ||
           title.includes('welcome') ||
           hasWelcomeHeading ||
           hasWelcomeContent;
  }

  function makeSortable(table) {
    // Skip if already processed
    if (table.dataset.sortable === 'true') return;
    table.dataset.sortable = 'true';

    // Skip ALL sorting on Welcome page
    if (isWelcomePage()) return;

    const headerRow = table.querySelector('thead tr') || table.querySelector('tr');
    if (!headerRow) return;

    const headers = headerRow.querySelectorAll('th');
    if (headers.length === 0) return;

    headers.forEach((header, index) => {
      header.style.cursor = 'pointer';
      header.style.userSelect = 'none';
      header.title = 'Click to sort';

      // Add sort indicator span if not exists
      if (!header.querySelector('.sort-indicator')) {
        const indicator = document.createElement('span');
        indicator.className = 'sort-indicator';
        indicator.style.marginLeft = '6px';
        indicator.style.opacity = '0.4';
        indicator.textContent = '▲'; // Always show arrow
        header.appendChild(indicator);
      }

      header.onclick = function(e) {
        e.preventDefault();
        sortTable(table, index, header);
      };
    });

    // Default sort by Year column (or first column if no Year)
    let defaultIndex = 0;
    headers.forEach((h, i) => {
      if (h.textContent.trim().toLowerCase() === 'year') defaultIndex = i;
    });
    const defaultHeader = headers[defaultIndex];
    if (defaultHeader) {
      defaultHeader.dataset.sortDir = 'none'; // Will become 'asc' on first sort
      sortTable(table, defaultIndex, defaultHeader);
    }
  }

  function sortTable(table, columnIndex, header) {
    const tbody = table.querySelector('tbody');
    const rowContainer = tbody || table;
    const allRows = Array.from(rowContainer.querySelectorAll('tr'));
    const rows = allRows.filter(row => row.querySelector('td'));

    if (rows.length === 0) return;

    // Determine sort direction
    const currentDir = header.dataset.sortDir || 'none';
    const newDir = currentDir === 'asc' ? 'desc' : 'asc';

    // Update all headers - dim inactive, highlight active
    table.querySelectorAll('th').forEach(th => {
      th.dataset.sortDir = 'none';
      const ind = th.querySelector('.sort-indicator');
      if (ind) {
        ind.style.opacity = '0.3';
        ind.textContent = '▲';
      }
    });

    // Set current header as active
    header.dataset.sortDir = newDir;
    const indicator = header.querySelector('.sort-indicator');
    if (indicator) {
      indicator.style.opacity = '1';
      indicator.textContent = newDir === 'asc' ? '▲' : '▼';
    }

    // Sort rows
    rows.sort((a, b) => {
      const cellA = a.querySelectorAll('td')[columnIndex];
      const cellB = b.querySelectorAll('td')[columnIndex];

      if (!cellA || !cellB) return 0;

      let valA = cellA.textContent.trim();
      let valB = cellB.textContent.trim();

      // Try numeric sort first (for Year column)
      const numA = parseFloat(valA);
      const numB = parseFloat(valB);

      if (!isNaN(numA) && !isNaN(numB)) {
        return newDir === 'asc' ? numA - numB : numB - numA;
      }

      // String sort
      valA = valA.toLowerCase();
      valB = valB.toLowerCase();

      if (valA < valB) return newDir === 'asc' ? -1 : 1;
      if (valA > valB) return newDir === 'asc' ? 1 : -1;
      return 0;
    });

    // Reorder rows in DOM
    rows.forEach(row => rowContainer.appendChild(row));
  }

  function initSortableTables() {
    document.querySelectorAll('table').forEach(makeSortable);
  }

  // Run on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSortableTables);
  } else {
    setTimeout(initSortableTables, 100);
  }

  // Re-run when Obsidian Publish navigates
  const observer = new MutationObserver((mutations) => {
    let shouldInit = false;
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length) {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1 && (node.querySelector?.('table') || node.tagName === 'TABLE')) {
            shouldInit = true;
          }
        });
      }
    });
    if (shouldInit) setTimeout(initSortableTables, 100);
  });

  observer.observe(document.body, { childList: true, subtree: true });
})();
