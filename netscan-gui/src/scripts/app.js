/**
 * NetScan GUI - Main Application Controller
 */

class App {
  constructor() {
    this.currentView = 'dashboard';
    this.devices = [];
    this.scanResults = null;
    this.isScanning = false;
    
    this.init();
  }
  
  async init() {
    // Set up theme
    await this.initTheme();
    
    // Set platform class for macOS-specific styling
    if (window.netscan.isDarwin) {
      document.body.classList.add('darwin');
    }
    
    // Set up navigation
    this.setupNavigation();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Load initial view
    this.navigateTo('dashboard');
    
    // Listen for IPC events
    this.setupIPCListeners();
    
    // Start periodic updates
    this.startPeriodicUpdates();
  }
  
  async initTheme() {
    const theme = await window.netscan.getTheme();
    document.documentElement.setAttribute('data-theme', theme);
  }
  
  setupNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const view = item.dataset.view;
        if (view) {
          this.navigateTo(view);
        }
      });
    });
  }
  
  setupEventListeners() {
    // Theme toggle
    document.getElementById('theme-btn').addEventListener('click', () => this.toggleTheme());
    
    // Scan button
    document.getElementById('scan-btn').addEventListener('click', () => this.startScan());
    
    // Search input
    document.getElementById('search-input').addEventListener('input', (e) => {
      this.handleSearch(e.target.value);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Cmd/Ctrl + K for search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('search-input').focus();
      }
    });
  }
  
  setupIPCListeners() {
    // Navigation from menu
    window.netscan.onNavigate((view) => {
      this.navigateTo(view);
    });
    
    // Actions from menu
    window.netscan.onAction((action) => {
      this.handleAction(action);
    });
    
    // Theme changes
    window.netscan.onThemeChanged((theme) => {
      document.documentElement.setAttribute('data-theme', theme);
    });
  }
  
  async toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    await window.netscan.setTheme(newTheme);
  }
  
  navigateTo(view) {
    this.currentView = view;
    
    // Update navigation active state
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.dataset.view === view);
    });
    
    // Update page title
    const titles = {
      dashboard: 'Dashboard',
      scan: 'Scan Network',
      devices: 'Devices',
      topology: 'Network Topology',
      security: 'Security Audit',
      monitor: 'Network Monitor',
      lookup: 'MAC Lookup',
      wol: 'Wake-on-LAN',
      settings: 'Settings'
    };
    document.getElementById('page-title').textContent = titles[view] || 'NetScan';
    
    // Render the view
    this.renderView(view);
  }
  
  renderView(view) {
    const content = document.getElementById('content');
    
    switch (view) {
      case 'dashboard':
        content.innerHTML = Views.dashboard(this);
        this.initDashboard();
        break;
      case 'scan':
        content.innerHTML = Views.scan(this);
        this.initScanView();
        break;
      case 'devices':
        content.innerHTML = Views.devices(this);
        this.initDevicesView();
        break;
      case 'topology':
        content.innerHTML = Views.topology(this);
        this.initTopologyView();
        break;
      case 'security':
        content.innerHTML = Views.security(this);
        this.initSecurityView();
        break;
      case 'monitor':
        content.innerHTML = Views.monitor(this);
        this.initMonitorView();
        break;
      case 'lookup':
        content.innerHTML = Views.lookup(this);
        this.initLookupView();
        break;
      case 'wol':
        content.innerHTML = Views.wol(this);
        this.initWolView();
        break;
      case 'settings':
        content.innerHTML = Views.settings(this);
        this.initSettingsView();
        break;
      default:
        content.innerHTML = '<p>View not found</p>';
    }
  }
  
  handleAction(action) {
    switch (action) {
      case 'new-scan':
      case 'quick-scan':
        this.startScan('quick');
        break;
      case 'full-scan':
        this.startScan('full');
        break;
      case 'security-audit':
        this.navigateTo('security');
        break;
      case 'fingerprint':
        this.runFingerprinting();
        break;
      case 'export':
        this.exportResults();
        break;
    }
  }
  
  handleSearch(query) {
    if (!query) return;
    
    // Filter displayed devices
    const devices = document.querySelectorAll('.device-card');
    devices.forEach(card => {
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
    });
  }
  
  async startScan(type = 'quick') {
    if (this.isScanning) return;
    
    this.isScanning = true;
    this.showLoading(`Running ${type} scan...`);
    
    try {
      // Get network interfaces
      const interfaces = await window.netscan.getInterfaces();
      
      if (interfaces.length === 0) {
        this.hideLoading();
        this.showToast('error', 'No network interfaces found');
        return;
      }
      
      // Use first interface
      const iface = interfaces[0];
      const subnet = this.getSubnet(iface.address, iface.netmask);
      
      // Run Python scanner
      const result = await window.netscan.runPython('async_scanner.py', [
        '--target', subnet,
        '--json'
      ]);
      
      if (result.success) {
        try {
          this.scanResults = JSON.parse(result.data);
          this.devices = this.scanResults.devices || [];
          this.updateDeviceCount();
          this.showToast('success', `Found ${this.devices.length} devices`);
        } catch (e) {
          // Parse line by line for devices
          this.parseARPOutput(result.data);
        }
      } else {
        // Fallback to ARP scan
        await this.runARPScan();
      }
    } catch (error) {
      this.showToast('error', 'Scan failed: ' + error.message);
    } finally {
      this.isScanning = false;
      this.hideLoading();
      
      // Refresh current view
      if (this.currentView === 'dashboard' || this.currentView === 'devices') {
        this.renderView(this.currentView);
      }
    }
  }
  
  async runARPScan() {
    let cmd;
    if (window.netscan.isDarwin || window.netscan.isLinux) {
      cmd = 'arp -a';
    } else {
      cmd = 'arp -a';
    }
    
    const result = await window.netscan.runCommand(cmd);
    if (result.success) {
      this.parseARPOutput(result.data);
    }
  }
  
  parseARPOutput(output) {
    this.devices = [];
    const lines = output.split('\n');
    
    for (const line of lines) {
      // Parse macOS/Linux format: hostname (ip) at mac on interface
      const match = line.match(/\((\d+\.\d+\.\d+\.\d+)\) at ([0-9a-f:]+)/i);
      if (match) {
        this.devices.push({
          ip: match[1],
          mac: match[2].toUpperCase(),
          hostname: line.split('(')[0].trim() || 'Unknown',
          status: 'online',
          vendor: 'Unknown'
        });
      }
    }
    
    this.updateDeviceCount();
  }
  
  getSubnet(ip, netmask) {
    const ipParts = ip.split('.').map(Number);
    const maskParts = netmask.split('.').map(Number);
    
    const networkParts = ipParts.map((part, i) => part & maskParts[i]);
    
    // Calculate CIDR
    let cidr = 0;
    for (const part of maskParts) {
      cidr += (part >>> 0).toString(2).split('1').length - 1;
    }
    
    return `${networkParts.join('.')}/${cidr}`;
  }
  
  updateDeviceCount() {
    document.getElementById('device-count').textContent = this.devices.length;
  }
  
  async runFingerprinting() {
    this.showLoading('Fingerprinting devices...');
    
    try {
      const result = await window.netscan.runPython('fingerprint.py', [
        '--scan-network', '--json'
      ]);
      
      if (result.success) {
        this.showToast('success', 'Fingerprinting complete');
        // Merge fingerprint data with devices
      }
    } catch (error) {
      this.showToast('error', 'Fingerprinting failed');
    } finally {
      this.hideLoading();
    }
  }
  
  async exportResults() {
    const options = {
      title: 'Export Scan Results',
      defaultPath: `netscan-export-${Date.now()}.json`,
      filters: [
        { name: 'JSON', extensions: ['json'] },
        { name: 'CSV', extensions: ['csv'] },
        { name: 'HTML', extensions: ['html'] }
      ]
    };
    
    const result = await window.netscan.showSaveDialog(options);
    
    if (!result.canceled && result.filePath) {
      const ext = result.filePath.split('.').pop();
      let content;
      
      if (ext === 'json') {
        content = JSON.stringify({ devices: this.devices, timestamp: new Date().toISOString() }, null, 2);
      } else if (ext === 'csv') {
        content = this.devicesToCSV();
      } else {
        content = this.devicesToHTML();
      }
      
      const writeResult = await window.netscan.writeFile(result.filePath, content);
      
      if (writeResult.success) {
        this.showToast('success', 'Export saved successfully');
      } else {
        this.showToast('error', 'Failed to save export');
      }
    }
  }
  
  devicesToCSV() {
    const headers = ['IP', 'MAC', 'Hostname', 'Vendor', 'Status'];
    const rows = this.devices.map(d => [d.ip, d.mac, d.hostname, d.vendor, d.status]);
    return [headers, ...rows].map(r => r.join(',')).join('\n');
  }
  
  devicesToHTML() {
    return `<!DOCTYPE html>
<html>
<head>
  <title>NetScan Export</title>
  <style>
    body { font-family: -apple-system, sans-serif; padding: 40px; }
    h1 { color: #228be6; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #dee2e6; padding: 12px; text-align: left; }
    th { background: #f8f9fa; }
  </style>
</head>
<body>
  <h1>NetScan Export</h1>
  <p>Generated: ${new Date().toLocaleString()}</p>
  <table>
    <tr><th>IP</th><th>MAC</th><th>Hostname</th><th>Vendor</th><th>Status</th></tr>
    ${this.devices.map(d => `<tr><td>${d.ip}</td><td>${d.mac}</td><td>${d.hostname}</td><td>${d.vendor}</td><td>${d.status}</td></tr>`).join('')}
  </table>
</body>
</html>`;
  }
  
  startPeriodicUpdates() {
    // Update stats every 30 seconds
    setInterval(() => {
      if (this.currentView === 'dashboard') {
        this.updateDashboardStats();
      }
    }, 30000);
  }
  
  // View initializers
  initDashboard() {
    this.updateDashboardStats();
    Charts.initDashboardCharts(this);
  }
  
  initScanView() {
    // Set up scan type buttons
    document.querySelectorAll('[data-scan-type]').forEach(btn => {
      btn.addEventListener('click', () => {
        this.startScan(btn.dataset.scanType);
      });
    });
  }
  
  initDevicesView() {
    // Set up filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.filterDevices(btn.dataset.filter);
      });
    });
    
    // Set up view toggle
    document.querySelectorAll('.view-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.view-toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.setDeviceViewMode(btn.dataset.view);
      });
    });
  }
  
  initTopologyView() {
    // Initialize network visualization
    setTimeout(() => {
      Charts.initTopology(this);
    }, 100);
  }
  
  initSecurityView() {
    document.getElementById('run-audit-btn')?.addEventListener('click', () => {
      this.runSecurityAudit();
    });
  }
  
  initMonitorView() {
    // Start real-time monitoring
  }
  
  initLookupView() {
    const form = document.getElementById('lookup-form');
    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const mac = document.getElementById('mac-input').value;
      await this.lookupMAC(mac);
    });
  }
  
  initWolView() {
    const form = document.getElementById('wol-form');
    form?.addEventListener('submit', async (e) => {
      e.preventDefault();
      const mac = document.getElementById('wol-mac-input').value;
      await this.sendWOL(mac);
    });
  }
  
  initSettingsView() {
    // Load current settings
    this.loadSettings();
    
    // Theme select
    document.getElementById('theme-select')?.addEventListener('change', async (e) => {
      await window.netscan.setTheme(e.target.value);
      if (e.target.value !== 'system') {
        document.documentElement.setAttribute('data-theme', e.target.value);
      }
    });
    
    // Toggle settings
    document.querySelectorAll('.settings-toggle').forEach(toggle => {
      toggle.addEventListener('change', async (e) => {
        await window.netscan.setSetting(e.target.dataset.setting, e.target.checked);
      });
    });
  }
  
  async loadSettings() {
    const settings = await window.netscan.getAllSettings();
    
    // Apply settings to form
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
      themeSelect.value = settings.theme || 'system';
    }
    
    document.querySelectorAll('.settings-toggle').forEach(toggle => {
      toggle.checked = settings[toggle.dataset.setting] ?? true;
    });
  }
  
  updateDashboardStats() {
    // Update stat values
    const onlineCount = this.devices.filter(d => d.status === 'online').length;
    document.getElementById('stat-devices')?.setAttribute('data-value', this.devices.length);
    document.getElementById('stat-online')?.setAttribute('data-value', onlineCount);
  }
  
  filterDevices(filter) {
    const cards = document.querySelectorAll('.device-card');
    cards.forEach(card => {
      if (filter === 'all') {
        card.style.display = '';
      } else {
        const status = card.dataset.status;
        card.style.display = status === filter ? '' : 'none';
      }
    });
  }
  
  setDeviceViewMode(mode) {
    const container = document.getElementById('devices-container');
    if (container) {
      container.className = mode === 'grid' ? 'device-grid' : 'device-list';
    }
  }
  
  async runSecurityAudit() {
    this.showLoading('Running security audit...');
    
    try {
      const result = await window.netscan.runPython('security.py', ['--scan', '--json']);
      
      if (result.success) {
        // Display results
        this.showToast('success', 'Security audit complete');
        // Refresh view with results
      }
    } catch (error) {
      this.showToast('error', 'Security audit failed');
    } finally {
      this.hideLoading();
    }
  }
  
  async lookupMAC(mac) {
    const resultDiv = document.getElementById('lookup-result');
    resultDiv.innerHTML = '<div class="skeleton skeleton-text"></div>';
    
    try {
      const result = await window.netscan.runPython('mac_normalizer.py', ['--lookup', mac]);
      
      if (result.success) {
        resultDiv.innerHTML = `
          <div class="card">
            <h3>Results</h3>
            <p><strong>MAC:</strong> ${mac}</p>
            <p><strong>Vendor:</strong> ${result.data.trim() || 'Unknown'}</p>
          </div>
        `;
      } else {
        resultDiv.innerHTML = `<div class="alert error">Lookup failed</div>`;
      }
    } catch (error) {
      resultDiv.innerHTML = `<div class="alert error">${error.message}</div>`;
    }
  }
  
  async sendWOL(mac) {
    this.showLoading('Sending magic packet...');
    
    try {
      const result = await window.netscan.runPython('wol.py', ['--mac', mac]);
      
      if (result.success) {
        this.showToast('success', `Magic packet sent to ${mac}`);
      } else {
        this.showToast('error', 'Failed to send magic packet');
      }
    } catch (error) {
      this.showToast('error', error.message);
    } finally {
      this.hideLoading();
    }
  }
  
  // UI Helpers
  showLoading(text = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    overlay.querySelector('.loading-text').textContent = text;
    overlay.classList.add('active');
  }
  
  hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
  }
  
  showToast(type, message, title = '') {
    const container = document.getElementById('toast-container');
    
    const icons = {
      success: '<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
      error: '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>',
      warning: '<svg viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
      info: '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div class="toast-icon">${icons[type]}</div>
      <div class="toast-content">
        ${title ? `<div class="toast-title">${title}</div>` : ''}
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close">×</button>
    `;
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
      toast.remove();
    });
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
      toast.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new App();
});
