const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  onMenuAction: (callback) => {
    ipcRenderer.on('menu-new-file', callback);
    ipcRenderer.on('menu-save-file', callback);
    ipcRenderer.on('menu-run-code', callback);
    ipcRenderer.on('menu-generate-code', callback);
    ipcRenderer.on('menu-start-voice', callback);
  },
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel)
});
