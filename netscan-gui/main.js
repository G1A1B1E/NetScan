const { app, BrowserWindow, ipcMain, Menu, Tray, nativeTheme, shell, dialog } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const os = require('os');

// Simple store implementation (fallback if electron-store not available)
let store;
try {
  const Store = require('electron-store');
  store = new Store({
    defaults: {
      theme: 'system',
      notifications: true,
      scanInterval: 60,
      autoStart: false,
      minimizeToTray: true,
      windowBounds: { width: 1400, height: 900 }
    }
  });
} catch (e) {
  // Fallback store using simple JSON file
  const settingsPath = path.join(app.getPath('userData'), 'settings.json');
  const defaults = {
    theme: 'system',
    notifications: true,
    scanInterval: 60,
    autoStart: false,
    minimizeToTray: true,
    windowBounds: { width: 1400, height: 900 }
  };
  
  store = {
    data: defaults,
    get(key, defaultValue) {
      if (this.data[key] !== undefined) return this.data[key];
      return defaultValue;
    },
    set(key, value) {
      this.data[key] = value;
      try {
        fs.writeFileSync(settingsPath, JSON.stringify(this.data, null, 2));
      } catch (e) {}
    },
    get store() { return this.data; }
  };
  
  try {
    if (fs.existsSync(settingsPath)) {
      store.data = { ...defaults, ...JSON.parse(fs.readFileSync(settingsPath, 'utf8')) };
    }
  } catch (e) {}
}

let mainWindow;
let tray = null;
let isQuitting = false;

// Get helpers path (works in dev and production)
function getHelpersPath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'helpers');
  }
  return path.join(__dirname, '..', 'helpers');
}

// Get Python executable
function getPythonPath() {
  if (process.platform === 'win32') {
    return 'python';
  }
  return 'python3';
}

// Create the main window
function createWindow() {
  const bounds = store.get('windowBounds');
  
  mainWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    minWidth: 1000,
    minHeight: 700,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    trafficLightPosition: { x: 20, y: 20 },
    frame: process.platform !== 'darwin',
    transparent: false,
    vibrancy: 'under-window',
    visualEffectState: 'active',
    backgroundColor: nativeTheme.shouldUseDarkColors ? '#1a1a2e' : '#ffffff',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'build', process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
    show: false
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Open DevTools in development
    if (process.env.NODE_ENV === 'development') {
      mainWindow.webContents.openDevTools();
    }
  });

  // Save window bounds on resize
  mainWindow.on('resize', () => {
    store.set('windowBounds', mainWindow.getBounds());
  });

  // Handle close to tray
  mainWindow.on('close', (event) => {
    if (!isQuitting && store.get('minimizeToTray', true)) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
  });

  // Create application menu
  createMenu();
  
  // Create tray icon
  createTray();
}

// Create application menu
function createMenu() {
  const template = [
    ...(process.platform === 'darwin' ? [{
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        {
          label: 'Preferences...',
          accelerator: 'Cmd+,',
          click: () => mainWindow.webContents.send('navigate', 'settings')
        },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    }] : []),
    {
      label: 'File',
      submenu: [
        {
          label: 'New Scan',
          accelerator: 'CmdOrCtrl+N',
          click: () => mainWindow.webContents.send('action', 'new-scan')
        },
        {
          label: 'Export Results...',
          accelerator: 'CmdOrCtrl+E',
          click: () => mainWindow.webContents.send('action', 'export')
        },
        { type: 'separator' },
        process.platform === 'darwin' ? { role: 'close' } : { role: 'quit' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        {
          label: 'Dashboard',
          accelerator: 'CmdOrCtrl+1',
          click: () => mainWindow.webContents.send('navigate', 'dashboard')
        },
        {
          label: 'Devices',
          accelerator: 'CmdOrCtrl+2',
          click: () => mainWindow.webContents.send('navigate', 'devices')
        },
        {
          label: 'Topology',
          accelerator: 'CmdOrCtrl+3',
          click: () => mainWindow.webContents.send('navigate', 'topology')
        },
        {
          label: 'Security',
          accelerator: 'CmdOrCtrl+4',
          click: () => mainWindow.webContents.send('navigate', 'security')
        },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Scan',
      submenu: [
        {
          label: 'Quick Scan',
          accelerator: 'CmdOrCtrl+Shift+Q',
          click: () => mainWindow.webContents.send('action', 'quick-scan')
        },
        {
          label: 'Full Scan',
          accelerator: 'CmdOrCtrl+Shift+F',
          click: () => mainWindow.webContents.send('action', 'full-scan')
        },
        { type: 'separator' },
        {
          label: 'Security Audit',
          click: () => mainWindow.webContents.send('action', 'security-audit')
        },
        {
          label: 'Device Fingerprinting',
          click: () => mainWindow.webContents.send('action', 'fingerprint')
        }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize' },
        { role: 'zoom' },
        ...(process.platform === 'darwin' ? [
          { type: 'separator' },
          { role: 'front' }
        ] : [
          { role: 'close' }
        ])
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'Documentation',
          click: () => shell.openExternal('https://g1a1b1e.github.io/NetScan/')
        },
        {
          label: 'Report Issue',
          click: () => shell.openExternal('https://github.com/G1A1B1E/NetScan/issues')
        },
        { type: 'separator' },
        {
          label: 'View on GitHub',
          click: () => shell.openExternal('https://github.com/G1A1B1E/NetScan')
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// Create system tray
function createTray() {
  const iconPath = path.join(__dirname, 'build', 
    process.platform === 'darwin' ? 'tray-icon.png' : 'icon.ico');
  
  // Use a fallback if icon doesn't exist
  if (!fs.existsSync(iconPath)) {
    return;
  }
  
  tray = new Tray(iconPath);
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Show NetScan',
      click: () => mainWindow.show()
    },
    { type: 'separator' },
    {
      label: 'Quick Scan',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('action', 'quick-scan');
      }
    },
    {
      label: 'View Devices',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('navigate', 'devices');
      }
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('NetScan');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
  });
}

// IPC Handlers

// Run Python helper
ipcMain.handle('run-python', async (event, script, args = []) => {
  return new Promise((resolve, reject) => {
    const pythonPath = getPythonPath();
    const scriptPath = path.join(getHelpersPath(), script);
    
    const process = spawn(pythonPath, [scriptPath, ...args]);
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    process.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, data: stdout });
      } else {
        resolve({ success: false, error: stderr || `Process exited with code ${code}` });
      }
    });
    
    process.on('error', (err) => {
      reject({ success: false, error: err.message });
    });
  });
});

// Run shell command
ipcMain.handle('run-command', async (event, command) => {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        resolve({ success: false, error: stderr || error.message });
      } else {
        resolve({ success: true, data: stdout });
      }
    });
  });
});

// Get network interfaces
ipcMain.handle('get-interfaces', async () => {
  const interfaces = os.networkInterfaces();
  const result = [];
  
  for (const [name, addrs] of Object.entries(interfaces)) {
    for (const addr of addrs) {
      if (addr.family === 'IPv4' && !addr.internal) {
        result.push({
          name,
          address: addr.address,
          netmask: addr.netmask,
          mac: addr.mac
        });
      }
    }
  }
  
  return result;
});

// Settings handlers
ipcMain.handle('get-setting', (event, key) => store.get(key));
ipcMain.handle('set-setting', (event, key, value) => store.set(key, value));
ipcMain.handle('get-all-settings', () => store.store);

// Theme handling
ipcMain.handle('get-theme', () => {
  const theme = store.get('theme', 'system');
  if (theme === 'system') {
    return nativeTheme.shouldUseDarkColors ? 'dark' : 'light';
  }
  return theme;
});

ipcMain.handle('set-theme', (event, theme) => {
  store.set('theme', theme);
  if (theme === 'system') {
    nativeTheme.themeSource = 'system';
  } else {
    nativeTheme.themeSource = theme;
  }
});

// File dialogs
ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

// Write file
ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    fs.writeFileSync(filePath, content);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Read file
ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = fs.readFileSync(filePath, 'utf-8');
    return { success: true, data: content };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

// Open external link
ipcMain.handle('open-external', (event, url) => {
  shell.openExternal(url);
});

// App lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else {
    mainWindow.show();
  }
});

app.on('before-quit', () => {
  isQuitting = true;
});

// Handle theme changes
nativeTheme.on('updated', () => {
  mainWindow.webContents.send('theme-changed', 
    nativeTheme.shouldUseDarkColors ? 'dark' : 'light');
});
