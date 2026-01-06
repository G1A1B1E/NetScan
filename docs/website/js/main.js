// =============================================================================
// NetScan Documentation - Main JavaScript
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileMenuBtn && sidebar) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            mobileMenuBtn.classList.toggle('active');
        });
        
        // Close sidebar when clicking outside
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                sidebar.classList.remove('open');
                mobileMenuBtn.classList.remove('active');
            }
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                searchInput.value = '';
                closeSearchResults();
            }
        });
    }
    
    // Copy buttons for code blocks
    document.querySelectorAll('.copy-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const target = btn.getAttribute('data-clipboard-target');
            const code = document.querySelector(target);
            
            if (code) {
                copyToClipboard(code.textContent);
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = 'Copy', 2000);
            }
        });
    });
    
    // Add copy buttons to all code blocks without them
    document.querySelectorAll('.code-block').forEach(function(block) {
        if (!block.querySelector('.copy-btn')) {
            const header = block.querySelector('.code-header');
            const pre = block.querySelector('pre');
            const code = block.querySelector('code');
            
            if (pre && code && !header) {
                const newHeader = document.createElement('div');
                newHeader.className = 'code-header';
                
                const lang = code.className.replace('language-', '') || 'code';
                newHeader.innerHTML = `<span>${lang}</span><button class="copy-btn">Copy</button>`;
                
                block.insertBefore(newHeader, pre);
                
                newHeader.querySelector('.copy-btn').addEventListener('click', function() {
                    copyToClipboard(code.textContent);
                    this.textContent = 'Copied!';
                    setTimeout(() => this.textContent = 'Copy', 2000);
                });
            }
        }
    });
    
    // Table of contents highlighting
    const tocLinks = document.querySelectorAll('.toc nav a');
    const headings = document.querySelectorAll('h2[id], h3[id]');
    
    if (tocLinks.length > 0 && headings.length > 0) {
        window.addEventListener('scroll', debounce(updateTocHighlight, 100));
        updateTocHighlight();
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Update URL without scrolling
                history.pushState(null, null, this.getAttribute('href'));
            }
        });
    });
    
    // Add IDs to headings if missing
    document.querySelectorAll('h2, h3, h4').forEach(function(heading) {
        if (!heading.id) {
            heading.id = slugify(heading.textContent);
        }
    });
    
    // External link handling
    document.querySelectorAll('a[href^="http"]').forEach(function(link) {
        if (!link.getAttribute('target')) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
});

// =============================================================================
// Utility Functions
// =============================================================================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
    }
}

function slugify(text) {
    return text
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/--+/g, '-')
        .trim();
}

function updateTocHighlight() {
    const headings = document.querySelectorAll('h2[id], h3[id]');
    const tocLinks = document.querySelectorAll('.toc nav a');
    
    let currentSection = null;
    const scrollPos = window.scrollY + 100;
    
    headings.forEach(function(heading) {
        if (heading.offsetTop <= scrollPos) {
            currentSection = heading.id;
        }
    });
    
    tocLinks.forEach(function(link) {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + currentSection) {
            link.classList.add('active');
        }
    });
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    
    if (query.length < 2) {
        closeSearchResults();
        return;
    }
    
    // Search implementation would go here
    // For a static site, this could search a pre-built index
    console.log('Searching for:', query);
}

function closeSearchResults() {
    // Close any search results dropdown
    const results = document.querySelector('.search-results');
    if (results) {
        results.remove();
    }
}

// =============================================================================
// Keyboard shortcuts
// =============================================================================

document.addEventListener('keydown', function(e) {
    // Focus search on '/' key
    if (e.key === '/' && !isInputFocused()) {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Close sidebar on Escape
    if (e.key === 'Escape') {
        const sidebar = document.querySelector('.sidebar');
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        if (sidebar && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            mobileMenuBtn.classList.remove('active');
        }
    }
});

function isInputFocused() {
    const activeElement = document.activeElement;
    return activeElement && (
        activeElement.tagName === 'INPUT' ||
        activeElement.tagName === 'TEXTAREA' ||
        activeElement.isContentEditable
    );
}
