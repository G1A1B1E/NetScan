// =============================================================================
// NetScan Documentation - Main JavaScript (Single-Page Edition)
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Mount content into #app
    const app = document.getElementById('app');
    if (app && window.NETSCAN_CONTENT) {
        app.innerHTML = window.NETSCAN_CONTENT;
    }
    
    // Trigger syntax highlighting
    if (window.Prism) {
        Prism.highlightAll();
    }

    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    
    // Mobile menu toggle
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
    
    // Search functionality with live sidebar filter
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 150));
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                searchInput.value = '';
                resetSearchFilter();
            }
        });
    }
    
    // Copy buttons for code blocks
    document.querySelectorAll('.copy-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const pre = btn.closest('.code-block').querySelector('pre');
            if (pre) {
                copyToClipboard(pre.textContent.trim());
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                btn.style.backgroundColor = '#28a745';
                btn.style.color = '#fff';
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.backgroundColor = '';
                    btn.style.color = '';
                }, 2000);
            }
        });
    });
    
    // Add copy buttons to any code blocks without one
    document.querySelectorAll('.code-block').forEach(function(block) {
        if (!block.querySelector('.copy-btn')) {
            let header = block.querySelector('.code-header');
            const pre = block.querySelector('pre');
            const code = block.querySelector('code');
            
            if (pre && code) {
                if (!header) {
                    header = document.createElement('div');
                    header.className = 'code-header';
                    const lang = code.className.replace('language-', '') || 'code';
                    header.innerHTML = `<span>${lang}</span>`;
                    block.insertBefore(header, pre);
                }
                const btn = document.createElement('button');
                btn.className = 'copy-btn';
                btn.textContent = 'Copy';
                btn.addEventListener('click', function() {
                    copyToClipboard(pre.textContent.trim());
                    btn.textContent = 'Copied!';
                    setTimeout(() => btn.textContent = 'Copy', 2000);
                });
                header.appendChild(btn);
            }
        }
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (!href || href === '#') return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                history.pushState(null, null, href);
                
                // Update active state in sidebar immediately
                updateActiveLink(href);
                
                // Close mobile sidebar on navigation
                if (sidebar && sidebar.classList.contains('open')) {
                    sidebar.classList.remove('open');
                    if (mobileMenuBtn) mobileMenuBtn.classList.remove('active');
                }
            }
        });
    });

    // Scrollspy for sidebar highlighting
    window.addEventListener('scroll', debounce(updateScrollspy, 80));
    
    // Initial highlight / anchor scroll on page load
    if (window.location.hash) {
        setTimeout(function() {
            const target = document.querySelector(window.location.hash);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                updateActiveLink(window.location.hash);
            }
        }, 150);
    } else {
        updateScrollspy();
    }
    
    // External links target=_blank
    document.querySelectorAll('a[href^="http"]').forEach(function(link) {
        if (!link.getAttribute('target')) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });
});

// =============================================================================
// Helper Functions
// =============================================================================

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
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

function updateActiveLink(hash) {
    document.querySelectorAll('.sidebar-nav a, .nav-links a').forEach(function(link) {
        if (link.getAttribute('href') === hash) {
            link.classList.add('active');
        } else if (link.getAttribute('href') && link.getAttribute('href').startsWith('#')) {
            link.classList.remove('active');
        }
    });
}

function updateScrollspy() {
    const sections = document.querySelectorAll('section[id]');
    if (sections.length === 0) return;
    
    let currentId = '';
    const scrollPos = window.scrollY + 140;
    
    sections.forEach(function(sec) {
        if (sec.offsetTop <= scrollPos) {
            currentId = sec.getAttribute('id');
        }
    });
    
    if (currentId) {
        updateActiveLink('#' + currentId);
    }
}

// Live Search Filter for Single-Page Navigation
function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    const navSections = document.querySelectorAll('.nav-section');
    
    if (!query) {
        resetSearchFilter();
        return;
    }
    
    navSections.forEach(function(sec) {
        let sectionHasMatch = false;
        const items = sec.querySelectorAll('li');
        
        items.forEach(function(item) {
            const text = item.textContent.toLowerCase();
            const link = item.querySelector('a');
            const href = link ? link.getAttribute('href') : '';
            
            // Check if text or section content matches
            const match = text.includes(query) || href.includes(query);
            if (match) {
                item.style.display = '';
                sectionHasMatch = true;
            } else {
                item.style.display = 'none';
            }
        });
        
        sec.style.display = sectionHasMatch ? '' : 'none';
    });
}

function resetSearchFilter() {
    document.querySelectorAll('.nav-section').forEach(sec => sec.style.display = '');
    document.querySelectorAll('.nav-section li').forEach(item => item.style.display = '');
}

// Keyboard shortcut: '/' to focus search, Esc to blur/clear
document.addEventListener('keydown', function(e) {
    if (e.key === '/' && !isInputFocused()) {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});

function isInputFocused() {
    const el = document.activeElement;
    return el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
}
