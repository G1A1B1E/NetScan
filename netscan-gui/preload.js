const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to renderer
contextBridge.exposeInMainWorld('netscan', {
  // Python helper execution
  runPython: (script, args) => ipcRenderer.invoke('run-python', script, args),
  
  // Shell command execution
  runCommand: (command) => ipcRenderer.invoke('run-command', command),
  
  // Network interfaces
  getInterfaces: () => ipcRenderer.invoke('get-interfaces'),
  
  // Settings
  getSetting: (key) => ipcRenderer.invoke('get-setting', key),
  setSetting: (key, value) => ipcRenderer.invoke('set-setting', key, value),
  getAllSettings: () => ipcRenderer.invoke('get-all-settings'),
  
  // Theme
  getTheme: () => ipcRenderer.invoke('get-theme'),
  setTheme: (theme) => ipcRenderer.invoke('set-theme', theme),
  
  // File operations
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  writeFile: (path, content) => ipcRenderer.invoke('write-file', path, content),
  readFile: (path) => ipcRenderer.invoke('read-file', path),
  
  // External links
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  
  // Event listeners
  onNavigate: (callback) => ipcRenderer.on('navigate', (event, view) => callback(view)),
  onAction: (callback) => ipcRenderer.on('action', (event, action) => callback(action)),
  onThemeChanged: (callback) => ipcRenderer.on('theme-changed', (event, theme) => callback(theme)),
  
  // Platform info
  platform: process.platform,
  isDarwin: process.platform === 'darwin',
  isWindows: process.platform === 'win32',
  isLinux: process.platform === 'linux'
});
