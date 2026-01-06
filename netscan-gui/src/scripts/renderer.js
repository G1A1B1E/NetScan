/**
 * NetScan GUI - Renderer Process
 * Main entry point for the frontend
 */

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  // Create app instance
  window.app = new App();
  
  // Initialize the app
  await app.init();
  
  // Setup view rendering
  app.renderView = function(view) {
    const content = document.getElementById('main-content');
    
    if (Views[view]) {
      content.innerHTML = Views[view](this);
      this.initViewHandlers(view);
    } else {
      content.innerHTML = `<div class="card"><h2>View not found: ${view}</h2></div>`;
    }
  };
  
  // Initialize view-specific handlers
  app.initViewHandlers = function(view) {
    switch(view) {
      case 'dashboard':
        this.initDashboard();
        break;
      case 'scan':
        this.initScanView();
        break;
      case 'devices':
        this.initDevicesView();
        break;
      case 'lookup':
        this.initLookupView();
        break;
      case 'wol':
        this.initWolView();
        break;
      case 'security':
        this.initSecurityView();
        break;
      case 'monitor':
        this.initMonitorView();
        break;
      case 'settings':
        this.initSettingsView();
        break;
    }
  };
  
  // Dashboard initialization
  app.initDashboard = function() {
    // Initialize charts if needed
    this.initDashboardCharts();
  };
  
  // Initialize dashboard charts
  app.initDashboardCharts = function() {
    const typesCanvas = document.getElementById('device-types-chart');
    const vendorCanvas = document.getElementById('vendor-chart');
    
    // Simple visualization without Chart.js
    if (typesCanvas) {
      const ctx = typesCanvas.getContext('2d');
      this.drawSimplePieChart(ctx, [
        { label: 'Computers', value: 3, color: '#228be6' },
        { label: 'Phones', value: 2, color: '#40c057' },
        { label: 'IoT', value: 1, color: '#fab005' },
        { label: 'Other', value: 1, color: '#868e96' }
      ]);
    }
    
    if (vendorCanvas) {
      const ctx = vendorCanvas.getContext('2d');
      this.drawSimpleBarChart(ctx, [
        { label: 'Apple', value: 3 },
        { label: 'Samsung', value: 2 },
        { label: 'Intel', value: 2 },
        { label: 'Unknown', value: 1 }
      ]);
    }
  };
  
  // Simple pie chart
  app.drawSimplePieChart = function(ctx, data) {
    const centerX = ctx.canvas.width / 2;
    const centerY = ctx.canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 40;
    
    const total = data.reduce((sum, d) => sum + d.value, 0);
    let startAngle = -Math.PI / 2;
    
    data.forEach(item => {
      const sliceAngle = (item.value / total) * 2 * Math.PI;
      
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
      ctx.closePath();
      ctx.fillStyle = item.color;
      ctx.fill();
      
      startAngle += sliceAngle;
    });
    
    // Draw legend
    data.forEach((item, i) => {
      const y = ctx.canvas.height - 20 - (data.length - i - 1) * 20;
      ctx.fillStyle = item.color;
      ctx.fillRect(10, y - 10, 12, 12);
      ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--text-color') || '#333';
      ctx.font = '12px system-ui';
      ctx.fillText(`${item.label} (${item.value})`, 28, y);
    });
  };
  
  // Simple bar chart
  app.drawSimpleBarChart = function(ctx, data) {
    const barHeight = 20;
    const gap = 10;
    const maxValue = Math.max(...data.map(d => d.value));
    const maxWidth = ctx.canvas.width - 100;
    const startY = 30;
    
    ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--text-color') || '#333';
    ctx.font = '12px system-ui';
    
    data.forEach((item, i) => {
      const y = startY + i * (barHeight + gap);
      const barWidth = (item.value / maxValue) * maxWidth;
      
      // Label
      ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--text-muted') || '#666';
      ctx.fillText(item.label, 10, y + barHeight - 5);
      
      // Bar
      ctx.fillStyle = '#228be6';
      ctx.fillRect(70, y, barWidth, barHeight);
      
      // Value
      ctx.fillStyle = getComputedStyle(document.body).getPropertyValue('--text-color') || '#333';
      ctx.fillText(item.value.toString(), 70 + barWidth + 8, y + barHeight - 5);
    });
  };
  
  // Scan view initialization
  app.initScanView = function() {
    const cards = document.querySelectorAll('[data-scan-type]:not(button)');
    cards.forEach(card => {
      card.addEventListener('click', () => {
        const type = card.dataset.scanType;
        if (type !== 'custom') {
          this.startScan(type);
        }
      });
    });
  };
  
  // Devices view initialization
  app.initDevicesView = function() {
    // Filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.filterDevices(btn.dataset.filter);
      });
    });
    
    // View toggle
    const viewBtns = document.querySelectorAll('.view-toggle-btn');
    viewBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        viewBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.toggleDeviceView(btn.dataset.view);
      });
    });
  };
  
  // Filter devices
  app.filterDevices = function(filter) {
    const cards = document.querySelectorAll('.device-card');
    cards.forEach(card => {
      if (filter === 'all') {
        card.style.display = '';
      } else {
        card.style.display = card.dataset.status === filter ? '' : 'none';
      }
    });
  };
  
  // Toggle device view
  app.toggleDeviceView = function(view) {
    const container = document.getElementById('devices-container');
    if (container) {
      container.className = view === 'list' ? 'device-list' : 'device-grid';
    }
  };
  
  // Lookup view initialization
  app.initLookupView = function() {
    const form = document.getElementById('lookup-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const mac = document.getElementById('mac-input').value.trim();
        if (mac) {
          await this.lookupMac(mac);
        }
      });
    }
  };
  
  // MAC lookup
  app.lookupMac = async function(mac) {
    const resultDiv = document.getElementById('lookup-result');
    resultDiv.innerHTML = `
      <div class="card">
        <div class="loading-spinner"></div>
        <p class="text-center text-muted mt-2">Looking up ${mac}...</p>
      </div>
    `;
    
    try {
      const vendor = await window.netscan.lookupMac(mac);
      resultDiv.innerHTML = `
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Result</h3>
          </div>
          <div class="lookup-result-content">
            <div class="lookup-result-row">
              <span class="text-muted">MAC Address:</span>
              <code>${mac}</code>
            </div>
            <div class="lookup-result-row">
              <span class="text-muted">Manufacturer:</span>
              <strong>${vendor || 'Unknown'}</strong>
            </div>
          </div>
        </div>
      `;
    } catch (error) {
      resultDiv.innerHTML = `
        <div class="alert error">
          <div class="alert-icon">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
          </div>
          <div class="alert-content">
            <div class="alert-title">Lookup Failed</div>
            <div class="alert-message">${error.message}</div>
          </div>
        </div>
      `;
    }
  };
  
  // WoL view initialization
  app.initWolView = function() {
    const form = document.getElementById('wol-form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const mac = document.getElementById('wol-mac-input').value.trim();
        if (mac) {
          await this.sendWakePacket(mac);
        }
      });
    }
  };
  
  // Send Wake-on-LAN packet
  app.sendWakePacket = async function(mac) {
    try {
      await window.netscan.runPython('wol', ['--mac', mac]);
      this.showToast('Magic packet sent successfully!', 'success');
    } catch (error) {
      this.showToast('Failed to send magic packet: ' + error.message, 'error');
    }
  };
  
  // Security view initialization
  app.initSecurityView = function() {
    const btn = document.getElementById('run-audit-btn');
    if (btn) {
      btn.addEventListener('click', () => this.runSecurityAudit());
    }
  };
  
  // Run security audit
  app.runSecurityAudit = async function() {
    this.showToast('Security audit started...', 'info');
    try {
      const result = await window.netscan.runPython('security', ['--audit']);
      this.showToast('Security audit completed!', 'success');
      // Update the view with results
    } catch (error) {
      this.showToast('Audit failed: ' + error.message, 'error');
    }
  };
  
  // Monitor view initialization
  app.initMonitorView = function() {
    const btn = document.getElementById('start-monitor-btn');
    if (btn) {
      btn.addEventListener('click', () => this.toggleMonitoring());
    }
  };
  
  // Toggle monitoring
  app.toggleMonitoring = function() {
    // TODO: Implement real-time monitoring
    this.showToast('Monitoring feature coming soon!', 'info');
  };
  
  // Settings view initialization
  app.initSettingsView = function() {
    // Theme select
    const themeSelect = document.getElementById('theme-select');
    if (themeSelect) {
      themeSelect.value = this.settings.theme || 'system';
      themeSelect.addEventListener('change', (e) => {
        this.setTheme(e.target.value);
        this.settings.theme = e.target.value;
        this.saveSettings();
      });
    }
    
    // Setting toggles
    const toggles = document.querySelectorAll('.settings-toggle');
    toggles.forEach(toggle => {
      const setting = toggle.dataset.setting;
      if (setting && this.settings[setting] !== undefined) {
        toggle.checked = this.settings[setting];
      }
      toggle.addEventListener('change', (e) => {
        this.settings[e.target.dataset.setting] = e.target.checked;
        this.saveSettings();
      });
    });
  };
  
  // Save settings
  app.saveSettings = function() {
    localStorage.setItem('netscan-settings', JSON.stringify(this.settings));
  };
  
  // Load settings
  app.loadSettings = function() {
    const saved = localStorage.getItem('netscan-settings');
    if (saved) {
      this.settings = { ...this.settings, ...JSON.parse(saved) };
    }
  };
  
  // Export results
  app.exportResults = async function() {
    try {
      const data = JSON.stringify(this.devices, null, 2);
      await window.netscan.runPython('export', ['--format', 'json', '--data', data]);
      this.showToast('Export successful!', 'success');
    } catch (error) {
      this.showToast('Export failed: ' + error.message, 'error');
    }
  };
  
  // Navigate to view
  app.navigateTo = function(view) {
    this.switchView(view);
  };
  
  // Add progress circle styles
  const style = document.createElement('style');
  style.textContent = `
    .progress-circle {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .progress-circle svg {
      transform: rotate(-90deg);
    }
    .progress-circle-bg {
      fill: none;
      stroke: var(--bg-secondary);
      stroke-width: 8;
    }
    .progress-circle-fg {
      fill: none;
      stroke-width: 8;
      stroke-linecap: round;
      transition: stroke-dashoffset 0.5s ease;
    }
    .progress-circle-text {
      position: absolute;
      font-size: 1.5rem;
      font-weight: 600;
    }
    .timeline {
      padding: 1rem 0;
    }
    .timeline-item {
      position: relative;
      padding-left: 2rem;
      padding-bottom: 1.5rem;
      border-left: 2px solid var(--bg-secondary);
    }
    .timeline-item:last-child {
      padding-bottom: 0;
    }
    .timeline-item::before {
      content: '';
      position: absolute;
      left: -6px;
      top: 0;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--bg-secondary);
    }
    .timeline-item.success::before {
      background: var(--accent-success);
    }
    .timeline-item.warning::before {
      background: var(--accent-warning);
    }
    .timeline-item.error::before {
      background: var(--accent-danger);
    }
    .timeline-time {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .timeline-title {
      font-weight: 500;
    }
    .timeline-description {
      font-size: 0.875rem;
      color: var(--text-muted);
    }
    .lookup-result-content {
      padding: 1rem 0;
    }
    .lookup-result-row {
      display: flex;
      justify-content: space-between;
      padding: 0.5rem 0;
      border-bottom: 1px solid var(--bg-secondary);
    }
    .lookup-result-row:last-child {
      border-bottom: none;
    }
    .network-map {
      min-height: 400px;
      background: var(--bg-secondary);
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-muted);
    }
    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid var(--bg-secondary);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 2rem auto;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .device-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1rem;
    }
    .device-list .device-card {
      flex-direction: row;
      align-items: center;
    }
    .device-card {
      background: var(--bg-secondary);
      border-radius: var(--radius);
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    .device-avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: var(--accent);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .device-avatar svg {
      width: 24px;
      height: 24px;
      fill: white;
    }
    .device-name {
      font-weight: 600;
    }
    .device-ip, .device-mac {
      font-family: monospace;
      font-size: 0.875rem;
      color: var(--text-muted);
    }
    .device-vendor {
      font-size: 0.75rem;
      color: var(--text-muted);
    }
    .device-status {
      margin-top: auto;
    }
    .filter-btn {
      background: none;
      border: 1px solid var(--border-color);
      padding: 0.5rem 1rem;
      border-radius: var(--radius);
      cursor: pointer;
      color: var(--text-color);
    }
    .filter-btn.active {
      background: var(--accent);
      border-color: var(--accent);
      color: white;
    }
    .view-toggle {
      display: flex;
      border: 1px solid var(--border-color);
      border-radius: var(--radius);
      overflow: hidden;
    }
    .view-toggle-btn {
      background: none;
      border: none;
      padding: 0.5rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .view-toggle-btn svg {
      width: 20px;
      height: 20px;
      fill: var(--text-muted);
    }
    .view-toggle-btn.active {
      background: var(--accent);
    }
    .view-toggle-btn.active svg {
      fill: white;
    }
    .settings-section {
      padding: 1.5rem 0;
      border-bottom: 1px solid var(--border-color);
    }
    .settings-section:first-child {
      padding-top: 0;
    }
    .settings-section:last-child {
      border-bottom: none;
    }
    .settings-section-title {
      font-size: 0.875rem;
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 1rem;
    }
    .settings-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.75rem 0;
    }
    .settings-row-title {
      font-weight: 500;
    }
    .settings-row-description {
      font-size: 0.875rem;
      color: var(--text-muted);
    }
    .toggle {
      position: relative;
      display: inline-block;
      width: 48px;
      height: 24px;
    }
    .toggle input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .toggle-slider {
      position: absolute;
      cursor: pointer;
      inset: 0;
      background: var(--bg-tertiary);
      border-radius: 24px;
      transition: var(--transition);
    }
    .toggle-slider::before {
      content: '';
      position: absolute;
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background: white;
      border-radius: 50%;
      transition: var(--transition);
    }
    .toggle input:checked + .toggle-slider {
      background: var(--accent);
    }
    .toggle input:checked + .toggle-slider::before {
      transform: translateX(24px);
    }
    .alert {
      display: flex;
      gap: 1rem;
      padding: 1rem;
      border-radius: var(--radius);
      background: var(--bg-secondary);
      border: 1px solid var(--border-color);
    }
    .alert.info {
      background: rgba(34, 139, 230, 0.1);
      border-color: rgba(34, 139, 230, 0.3);
    }
    .alert.error {
      background: rgba(250, 82, 82, 0.1);
      border-color: rgba(250, 82, 82, 0.3);
    }
    .alert-icon svg {
      width: 24px;
      height: 24px;
      fill: var(--accent);
    }
    .alert.error .alert-icon svg {
      fill: var(--accent-danger);
    }
    .alert-title {
      font-weight: 600;
      margin-bottom: 0.25rem;
    }
    .stat-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
    }
    .filters {
      display: flex;
      gap: 0.5rem;
    }
    .text-center {
      text-align: center;
    }
    .grid-3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
    }
    @media (max-width: 768px) {
      .grid-3 {
        grid-template-columns: 1fr;
      }
    }
  `;
  document.head.appendChild(style);
  
  // Initial render
  app.renderView(app.currentView);
  
  console.log('NetScan GUI initialized');
});
