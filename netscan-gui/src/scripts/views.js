/**
 * NetScan GUI - View Templates
 */

const Views = {
  dashboard(app) {
    const devices = app.devices || [];
    const onlineCount = devices.filter(d => d.status === 'online').length;
    const recentDevices = devices.slice(0, 5);
    
    return `
      <div class="dashboard">
        <!-- Stats Grid -->
        <div class="stat-grid">
          <div class="stat-card">
            <div class="stat-icon blue">
              <svg viewBox="0 0 24 24"><path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/></svg>
            </div>
            <div class="stat-content">
              <div class="stat-value" id="stat-devices">${devices.length}</div>
              <div class="stat-label">Total Devices</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon green">
              <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
            </div>
            <div class="stat-content">
              <div class="stat-value" id="stat-online">${onlineCount}</div>
              <div class="stat-label">Online Now</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon orange">
              <svg viewBox="0 0 24 24"><path d="M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z"/></svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">0</div>
              <div class="stat-label">Security Alerts</div>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon purple">
              <svg viewBox="0 0 24 24"><path d="M17 16l-4-4V8.82C14.16 8.4 15 7.3 15 6c0-1.66-1.34-3-3-3S9 4.34 9 6c0 1.3.84 2.4 2 2.82V12l-4 4H3v5h5v-3.05l4-4.2 4 4.2V21h5v-5h-4z"/></svg>
            </div>
            <div class="stat-content">
              <div class="stat-value">1</div>
              <div class="stat-label">Networks</div>
            </div>
          </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="grid-2 mb-3">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Quick Actions</h2>
            </div>
            <div class="flex gap-2" style="flex-wrap: wrap;">
              <button class="btn btn-primary" data-scan-type="quick">
                <svg viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
                Quick Scan
              </button>
              <button class="btn btn-secondary" onclick="app.navigateTo('security')">
                <svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
                Security Audit
              </button>
              <button class="btn btn-secondary" onclick="app.navigateTo('topology')">
                <svg viewBox="0 0 24 24"><path d="M17 16l-4-4V8.82C14.16 8.4 15 7.3 15 6c0-1.66-1.34-3-3-3S9 4.34 9 6c0 1.3.84 2.4 2 2.82V12l-4 4H3v5h5v-3.05l4-4.2 4 4.2V21h5v-5h-4z"/></svg>
                View Topology
              </button>
              <button class="btn btn-ghost" onclick="app.exportResults()">
                <svg viewBox="0 0 24 24"><path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2v9.67z"/></svg>
                Export
              </button>
            </div>
          </div>
          
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Network Status</h2>
            </div>
            <div class="flex items-center gap-3">
              <div class="progress-circle">
                <svg width="100" height="100" viewBox="0 0 100 100">
                  <circle class="progress-circle-bg" cx="50" cy="50" r="42"/>
                  <circle class="progress-circle-fg" cx="50" cy="50" r="42" 
                          stroke-dasharray="264" 
                          stroke-dashoffset="${264 - (264 * (onlineCount / Math.max(devices.length, 1)))}"
                          style="stroke: var(--accent-success);"/>
                </svg>
                <div class="progress-circle-text">${devices.length > 0 ? Math.round((onlineCount / devices.length) * 100) : 0}%</div>
              </div>
              <div>
                <div class="text-muted">Devices Online</div>
                <div style="font-size: 1.25rem; font-weight: 600;">${onlineCount} of ${devices.length}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Recent Devices & Activity -->
        <div class="grid-2">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Recent Devices</h2>
              <a href="#" class="btn btn-ghost btn-sm" onclick="app.navigateTo('devices')">View All →</a>
            </div>
            ${recentDevices.length > 0 ? `
              <div class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Device</th>
                      <th>IP Address</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${recentDevices.map(d => `
                      <tr>
                        <td>
                          <div class="device-type">
                            <svg viewBox="0 0 24 24"><path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/></svg>
                            <span>${d.hostname || d.ip}</span>
                          </div>
                        </td>
                        <td><code>${d.ip}</code></td>
                        <td><span class="status-badge ${d.status}">${d.status}</span></td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            ` : `
              <div class="empty-state">
                <svg class="empty-state-icon" viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
                <p class="empty-state-title">No devices found</p>
                <p class="empty-state-description">Run a scan to discover devices on your network</p>
                <button class="btn btn-primary" data-scan-type="quick">Start Scan</button>
              </div>
            `}
          </div>
          
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Activity</h2>
            </div>
            <div class="timeline">
              <div class="timeline-item success">
                <div class="timeline-time">Just now</div>
                <div class="timeline-title">Application started</div>
                <div class="timeline-description">NetScan GUI initialized</div>
              </div>
              ${devices.length > 0 ? `
                <div class="timeline-item success">
                  <div class="timeline-time">Recent</div>
                  <div class="timeline-title">Scan completed</div>
                  <div class="timeline-description">Found ${devices.length} devices</div>
                </div>
              ` : ''}
            </div>
          </div>
        </div>
        
        <!-- Charts -->
        <div class="grid-2 mt-3">
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Device Types</h2>
            </div>
            <canvas id="device-types-chart" height="200"></canvas>
          </div>
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Vendor Distribution</h2>
            </div>
            <canvas id="vendor-chart" height="200"></canvas>
          </div>
        </div>
      </div>
    `;
  },
  
  scan(app) {
    return `
      <div class="scan-view">
        <div class="card mb-3">
          <div class="card-header">
            <h2 class="card-title">Scan Options</h2>
          </div>
          <div class="grid-3 mb-3">
            <div class="card" style="cursor: pointer;" data-scan-type="quick">
              <h3>Quick Scan</h3>
              <p class="text-muted">Fast ARP scan to discover active devices</p>
              <div class="mt-2">
                <span class="status-badge online">~10 seconds</span>
              </div>
            </div>
            <div class="card" style="cursor: pointer;" data-scan-type="full">
              <h3>Full Scan</h3>
              <p class="text-muted">Complete scan with port detection</p>
              <div class="mt-2">
                <span class="status-badge warning">~2 minutes</span>
              </div>
            </div>
            <div class="card" style="cursor: pointer;" data-scan-type="custom">
              <h3>Custom Scan</h3>
              <p class="text-muted">Configure your own scan parameters</p>
              <div class="mt-2">
                <span class="status-badge">Variable</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Custom Scan Settings</h2>
          </div>
          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">Target Network</label>
              <input type="text" class="form-input" placeholder="192.168.1.0/24" id="scan-target">
              <p class="form-hint">CIDR notation or IP range</p>
            </div>
            <div class="form-group">
              <label class="form-label">Scan Speed</label>
              <select class="form-input form-select" id="scan-speed">
                <option value="fast">Fast (less accurate)</option>
                <option value="normal" selected>Normal</option>
                <option value="thorough">Thorough (slower)</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" id="scan-ports">
              <span>Include port scanning</span>
            </label>
          </div>
          <div class="form-group">
            <label class="form-checkbox">
              <input type="checkbox" id="scan-fingerprint">
              <span>Enable device fingerprinting</span>
            </label>
          </div>
          <button class="btn btn-primary btn-lg" data-scan-type="custom">Start Custom Scan</button>
        </div>
      </div>
    `;
  },
  
  devices(app) {
    const devices = app.devices || [];
    
    return `
      <div class="devices-view">
        <div class="flex justify-between items-center mb-3">
          <div class="filters">
            <button class="filter-btn active" data-filter="all">All (${devices.length})</button>
            <button class="filter-btn" data-filter="online">Online (${devices.filter(d => d.status === 'online').length})</button>
            <button class="filter-btn" data-filter="offline">Offline (${devices.filter(d => d.status === 'offline').length})</button>
          </div>
          <div class="flex gap-2">
            <div class="view-toggle">
              <button class="view-toggle-btn active" data-view="grid" title="Grid View">
                <svg viewBox="0 0 24 24"><path d="M3 3v8h8V3H3zm6 6H5V5h4v4zm-6 4v8h8v-8H3zm6 6H5v-4h4v4zm4-16v8h8V3h-8zm6 6h-4V5h4v4zm-6 4v8h8v-8h-8zm6 6h-4v-4h4v4z"/></svg>
              </button>
              <button class="view-toggle-btn" data-view="list" title="List View">
                <svg viewBox="0 0 24 24"><path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z"/></svg>
              </button>
            </div>
            <button class="btn btn-secondary" onclick="app.startScan()">
              <svg viewBox="0 0 24 24"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
              Refresh
            </button>
          </div>
        </div>
        
        ${devices.length > 0 ? `
          <div class="device-grid" id="devices-container">
            ${devices.map(d => `
              <div class="device-card" data-status="${d.status}">
                <div class="device-avatar">
                  <svg viewBox="0 0 24 24"><path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/></svg>
                </div>
                <div class="device-info">
                  <div class="device-name">${d.hostname || 'Unknown Device'}</div>
                  <div class="device-ip">${d.ip}</div>
                  <div class="device-mac">${d.mac}</div>
                  <div class="device-vendor">${d.vendor || 'Unknown Vendor'}</div>
                </div>
                <div class="device-status">
                  <span class="status-badge ${d.status}">${d.status}</span>
                </div>
              </div>
            `).join('')}
          </div>
        ` : `
          <div class="card">
            <div class="empty-state">
              <svg class="empty-state-icon" viewBox="0 0 24 24"><path d="M4 6h18V4H4c-1.1 0-2 .9-2 2v11H0v3h14v-3H4V6zm19 2h-6c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V9c0-.55-.45-1-1-1zm-1 9h-4v-7h4v7z"/></svg>
              <p class="empty-state-title">No devices found</p>
              <p class="empty-state-description">Run a network scan to discover devices</p>
              <button class="btn btn-primary" onclick="app.startScan()">Start Scan</button>
            </div>
          </div>
        `}
      </div>
    `;
  },
  
  topology(app) {
    return `
      <div class="topology-view">
        <div class="card mb-3">
          <div class="card-header">
            <h2 class="card-title">Network Topology</h2>
            <div class="flex gap-2">
              <button class="btn btn-secondary btn-sm" id="topology-refresh">
                <svg viewBox="0 0 24 24" width="16" height="16"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8z"/></svg>
                Refresh
              </button>
              <button class="btn btn-secondary btn-sm" id="topology-export">
                <svg viewBox="0 0 24 24" width="16" height="16"><path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2v9.67z"/></svg>
                Export
              </button>
            </div>
          </div>
          <div class="network-map">
            <div id="topology-canvas"></div>
          </div>
        </div>
        
        <div class="grid-2">
          <div class="card">
            <h3 class="card-title">Legend</h3>
            <div class="flex gap-3 mt-2">
              <div class="flex items-center gap-2">
                <div style="width: 16px; height: 16px; background: #228be6; border-radius: 50%;"></div>
                <span>Router/Gateway</span>
              </div>
              <div class="flex items-center gap-2">
                <div style="width: 16px; height: 16px; background: #40c057; border-radius: 50%;"></div>
                <span>Device</span>
              </div>
              <div class="flex items-center gap-2">
                <div style="width: 16px; height: 16px; background: #868e96; border-radius: 50%;"></div>
                <span>Offline</span>
              </div>
            </div>
          </div>
          <div class="card">
            <h3 class="card-title">Statistics</h3>
            <div class="flex gap-3 mt-2">
              <div><strong>${app.devices.length}</strong> Nodes</div>
              <div><strong>${app.devices.length}</strong> Connections</div>
              <div><strong>1</strong> Gateway</div>
            </div>
          </div>
        </div>
      </div>
    `;
  },
  
  security(app) {
    return `
      <div class="security-view">
        <div class="alert info mb-3">
          <div class="alert-icon">
            <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
          </div>
          <div class="alert-content">
            <div class="alert-title">Security Audit</div>
            <div class="alert-message">Run a security audit to check for vulnerabilities, open ports, and potential security issues on your network.</div>
          </div>
        </div>
        
        <div class="card mb-3">
          <div class="card-header">
            <h2 class="card-title">Security Overview</h2>
            <button class="btn btn-primary" id="run-audit-btn">
              <svg viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
              Run Security Audit
            </button>
          </div>
          
          <div class="stat-grid">
            <div class="stat-card">
              <div class="stat-icon green">
                <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
              </div>
              <div class="stat-content">
                <div class="stat-value">0</div>
                <div class="stat-label">Safe Devices</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon orange">
                <svg viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
              </div>
              <div class="stat-content">
                <div class="stat-value">0</div>
                <div class="stat-label">Warnings</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon red">
                <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
              </div>
              <div class="stat-content">
                <div class="stat-value">0</div>
                <div class="stat-label">Critical Issues</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Audit Results</h2>
          </div>
          <div class="empty-state">
            <svg class="empty-state-icon" viewBox="0 0 24 24"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
            <p class="empty-state-title">No audit results</p>
            <p class="empty-state-description">Click "Run Security Audit" to check your network for vulnerabilities</p>
          </div>
        </div>
      </div>
    `;
  },
  
  monitor(app) {
    return `
      <div class="monitor-view">
        <div class="card mb-3">
          <div class="card-header">
            <h2 class="card-title">Network Monitor</h2>
            <div class="flex gap-2">
              <button class="btn btn-primary" id="start-monitor-btn">
                <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                Start Monitoring
              </button>
            </div>
          </div>
          <p class="text-muted">Real-time monitoring will detect new devices connecting to your network and alert you to any changes.</p>
        </div>
        
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Activity Log</h2>
          </div>
          <div class="timeline">
            <div class="timeline-item">
              <div class="timeline-time">Waiting...</div>
              <div class="timeline-title">Monitoring not started</div>
              <div class="timeline-description">Click "Start Monitoring" to begin watching for network changes</div>
            </div>
          </div>
        </div>
      </div>
    `;
  },
  
  lookup(app) {
    return `
      <div class="lookup-view">
        <div class="card mb-3">
          <div class="card-header">
            <h2 class="card-title">MAC Address Lookup</h2>
          </div>
          <p class="text-muted mb-3">Enter a MAC address to identify the device manufacturer.</p>
          <form id="lookup-form">
            <div class="flex gap-2">
              <input type="text" class="form-input" id="mac-input" placeholder="00:11:22:33:44:55" style="max-width: 300px;">
              <button type="submit" class="btn btn-primary">Lookup</button>
            </div>
            <p class="form-hint">Supports formats: 00:11:22:33:44:55, 00-11-22-33-44-55, 001122334455</p>
          </form>
        </div>
        
        <div id="lookup-result"></div>
        
        <div class="card mt-3">
          <div class="card-header">
            <h2 class="card-title">Recent Lookups</h2>
          </div>
          <p class="text-muted">No recent lookups</p>
        </div>
      </div>
    `;
  },
  
  wol(app) {
    return `
      <div class="wol-view">
        <div class="card mb-3">
          <div class="card-header">
            <h2 class="card-title">Wake-on-LAN</h2>
          </div>
          <p class="text-muted mb-3">Send a magic packet to wake up a device on your network.</p>
          <form id="wol-form">
            <div class="flex gap-2">
              <input type="text" class="form-input" id="wol-mac-input" placeholder="00:11:22:33:44:55" style="max-width: 300px;">
              <button type="submit" class="btn btn-primary">
                <svg viewBox="0 0 24 24"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>
                Wake Device
              </button>
            </div>
          </form>
        </div>
        
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Saved Devices</h2>
            <button class="btn btn-secondary btn-sm">Add Device</button>
          </div>
          <div class="empty-state">
            <svg class="empty-state-icon" viewBox="0 0 24 24"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>
            <p class="empty-state-title">No saved devices</p>
            <p class="empty-state-description">Save frequently used devices for quick access</p>
          </div>
        </div>
      </div>
    `;
  },
  
  settings(app) {
    return `
      <div class="settings-view">
        <div class="card">
          <div class="settings-section">
            <h3 class="settings-section-title">Appearance</h3>
            <div class="settings-row">
              <div class="settings-row-content">
                <div class="settings-row-title">Theme</div>
                <div class="settings-row-description">Choose your preferred color scheme</div>
              </div>
              <select class="form-input form-select" id="theme-select" style="width: auto;">
                <option value="system">System</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </div>
          </div>
          
          <div class="settings-section">
            <h3 class="settings-section-title">Notifications</h3>
            <div class="settings-row">
              <div class="settings-row-content">
                <div class="settings-row-title">Desktop Notifications</div>
                <div class="settings-row-description">Show notifications for new devices and alerts</div>
              </div>
              <label class="toggle">
                <input type="checkbox" class="settings-toggle" data-setting="notifications" checked>
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="settings-row">
              <div class="settings-row-content">
                <div class="settings-row-title">Sound Alerts</div>
                <div class="settings-row-description">Play sound when new devices are detected</div>
              </div>
              <label class="toggle">
                <input type="checkbox" class="settings-toggle" data-setting="soundAlerts">
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          <div class="settings-section">
            <h3 class="settings-section-title">Scanning</h3>
            <div class="settings-row">
              <div class="settings-row-content">
                <div class="settings-row-title">Auto-scan on startup</div>
                <div class="settings-row-description">Automatically scan network when app starts</div>
              </div>
              <label class="toggle">
                <input type="checkbox" class="settings-toggle" data-setting="autoScan">
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="settings-row">
              <div class="settings-row-content">
                <div class="settings-row-title">Scan Interval</div>
                <div class="settings-row-description">How often to refresh device list (in minutes)</div>
              </div>
              <select class="form-input form-select" id="scan-interval" style="width: auto;">
                <option value="1">1 minute</option>
                <option value="5">5 minutes</option>
                <option value="15">15 minutes</option>
                <option value="30">30 minutes</option>
                <option value="60" selected>1 hour</option>
              </select>
            </div>
          </div>
          
          <div class="settings-section">
            <h3 class="settings-section-title">System</h3>
            <div class="settings-row">
              <div class="settings-row-content">
                <div class="settings-row-title">Minimize to Tray</div>
                <div class="settings-row-description">Keep running in system tray when closed</div>
              </div>
              <label class="toggle">
                <input type="checkbox" class="settings-toggle" data-setting="minimizeToTray" checked>
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
          
          <div class="settings-section">
            <h3 class="settings-section-title">About</h3>
            <div class="settings-row">
              <div class="settings-row-content">
                <div class="settings-row-title">NetScan</div>
                <div class="settings-row-description">Version 2.1.0</div>
              </div>
              <button class="btn btn-ghost btn-sm" onclick="window.netscan.openExternal('https://github.com/G1A1B1E/NetScan')">View on GitHub</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }
};
