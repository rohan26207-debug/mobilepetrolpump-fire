import { useEffect, useCallback } from 'react';
import localStorageService from '../services/localStorage';

const SEVEN_DAYS_MS = 7 * 24 * 60 * 60 * 1000; // 7 days in milliseconds
const AUTO_BACKUP_SETTINGS_KEY = 'mpump_auto_backup_weekly_settings';

export const useAutoBackupWeekly = (toast) => {
  // Check and perform auto backup if needed
  const checkAndPerformAutoBackup = useCallback(async () => {
    try {
      // Get settings from localStorage
      const settingsStr = localStorage.getItem(AUTO_BACKUP_SETTINGS_KEY);
      let settings = settingsStr ? JSON.parse(settingsStr) : null;

      // Initialize settings on first app open
      if (!settings) {
        const now = new Date().toISOString();
        settings = {
          enabled: true, // Enabled by default
          firstOpenTime: now,
          lastBackupTime: null,
          nextScheduledTime: new Date(Date.now() + SEVEN_DAYS_MS).toISOString()
        };
        localStorage.setItem(AUTO_BACKUP_SETTINGS_KEY, JSON.stringify(settings));
        console.log('Auto backup initialized:', settings);
        return;
      }

      // If disabled, don't perform backup
      if (!settings.enabled) {
        console.log('Auto backup is disabled');
        return;
      }

      // Check if 7 days have passed
      const now = Date.now();
      const nextScheduledTime = new Date(settings.nextScheduledTime).getTime();

      if (now >= nextScheduledTime) {
        console.log('7 days passed, performing auto backup...');
        
        // Perform backup
        const backupData = localStorageService.exportAllData();
        const dataStr = JSON.stringify(backupData, null, 2);
        const fileName = `mpump-auto-backup-${new Date().toISOString().split('T')[0]}.json`;

        // Check if running in Android WebView
        const isAndroid = typeof window.MPumpCalcAndroid !== 'undefined';
        const ownerEmail = (localStorage.getItem('mpump_backup_email') || '').trim();
        const emailSubject = `M.Pump Weekly Backup - ${new Date().toISOString().split('T')[0]}`;
        const emailBody = `Hi,\n\nAttached is the automatic weekly backup of Manager Petrol Pump data.\n\nFile: ${fileName}\nGenerated: ${new Date().toLocaleString()}\n\nKeep this file safe — you can restore data by importing it from Settings -> Backup -> Import Data.`;

        if (isAndroid && ownerEmail && typeof window.MPumpCalcAndroid.emailBackup === 'function') {
          // Save file + open Gmail compose pre-filled with owner's email
          const bytes = new TextEncoder().encode(dataStr);
          let binary = '';
          for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
          const base64 = btoa(binary);
          window.MPumpCalcAndroid.emailBackup(base64, fileName, 'application/json', ownerEmail, emailSubject, emailBody);
        } else if (isAndroid && typeof window.MPumpCalcAndroid.saveFileToDownloads === 'function') {
          // Android without owner email configured - just save locally
          const bytes = new TextEncoder().encode(dataStr);
          let binary = '';
          for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
          const base64 = btoa(binary);
          window.MPumpCalcAndroid.saveFileToDownloads(base64, fileName, 'application/json');
        } else {
          // Web browser - download file via anchor
          const dataBlob = new Blob([dataStr], { type: 'application/json' });
          const url = URL.createObjectURL(dataBlob);
          const link = document.createElement('a');
          link.href = url;
          link.download = fileName;
          link.style.display = 'none';

          document.body.appendChild(link);
          link.click();

          // Cleanup
          setTimeout(() => {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
          }, 100);

          // If on web + owner email set, open mailto fallback (no attachment possible via mailto)
          if (ownerEmail) {
            const mailto = `mailto:${encodeURIComponent(ownerEmail)}?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody + '\n\n(Please attach the downloaded file manually.)')}`;
            window.open(mailto, '_blank');
          }
        }

        // Update settings
        const backupTime = new Date().toISOString();
        settings.lastBackupTime = backupTime;
        settings.nextScheduledTime = new Date(Date.now() + SEVEN_DAYS_MS).toISOString();
        localStorage.setItem(AUTO_BACKUP_SETTINGS_KEY, JSON.stringify(settings));

        // Show success notification
        if (toast) {
          toast({
            title: "Auto Backup Successful",
            description: `Backup file downloaded: ${fileName}`,
          });
        }

        console.log('Auto backup completed:', settings);
      } else {
        console.log('Auto backup not due yet. Next backup:', settings.nextScheduledTime);
      }
    } catch (error) {
      console.error('Auto backup error:', error);
      if (toast) {
        toast({
          title: "Auto Backup Failed",
          description: "Could not perform automatic backup",
          variant: "destructive",
        });
      }
    }
  }, [toast]);

  // Run check on component mount
  useEffect(() => {
    checkAndPerformAutoBackup();
  }, [checkAndPerformAutoBackup]);

  // Return settings and control functions
  const getSettings = useCallback(() => {
    const settingsStr = localStorage.getItem(AUTO_BACKUP_SETTINGS_KEY);
    return settingsStr ? JSON.parse(settingsStr) : null;
  }, []);

  const toggleAutoBackup = useCallback((enabled) => {
    const settings = getSettings();
    if (settings) {
      settings.enabled = enabled;
      localStorage.setItem(AUTO_BACKUP_SETTINGS_KEY, JSON.stringify(settings));
      return true;
    }
    return false;
  }, [getSettings]);

  const getBackupStatus = useCallback(() => {
    const settings = getSettings();
    if (!settings) {
      return {
        enabled: false,
        lastBackupTime: null,
        nextScheduledTime: null
      };
    }
    return {
      enabled: settings.enabled,
      lastBackupTime: settings.lastBackupTime,
      nextScheduledTime: settings.nextScheduledTime
    };
  }, [getSettings]);

  return {
    checkAndPerformAutoBackup,
    toggleAutoBackup,
    getBackupStatus
  };
};
