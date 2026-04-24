# Petrol Pump Management App - PRD

## Overview
React-based petrol pump management application. 100% offline with localStorage only. No Firebase, no cloud sync, no login required.

## Tech Stack
- Frontend: React.js, TailwindCSS, Shadcn/UI
- Data Storage: Browser localStorage (fully offline)
- Process Control: Supervisor

## Core Features
- Sales tracking with nozzle/fuel type management
- Customer management with case-insensitive duplicate detection
- Credit sales and payment tracking
- Stock management (MPP Stock)
- Income/Expense tracking
- Settlement management
- Daily reports with PDF/print export
- Manual backup (export/import JSON)
- Auto backup (weekly)
- Pro Mode for advanced features

## Completed Work
- Case-insensitive duplicate customer name validation
- Settings UI fixes (scrolling, layout reordering)
- QR backup features removed
- Delete Data restricted to Pro Mode
- Merge Backup repositioned above Auto Backup
- MPP checkbox always visible in Add Sale form
- MPP-tagged sales excluded from stock calculations
- MPP section removed from dashboard summary
- Fixed "change is not defined" runtime error in Firestore listeners
- **Made app 100% offline**: Removed Firebase Auth, Firestore sync, login screen. App loads directly with localStorage only.
- **PDF optimization**: jsPDF with built-in Helvetica; file size reduced from ~138KB to ~2.5KB (well below 20KB target).
- **PDF font sizes matched to reference PDF (Feb 2026)**: Header title 14pt (bar 14mm), date 9pt, section headings 13pt, table body 9pt, table headers 10pt, footer 8pt.
- **Android wrapper with auto-download + auto-open (Feb 2026)**: `MPumpCalcAndroid.openPdfWithViewer` now saves to public `Downloads/MPumpCalc/` via MediaStore (API 29+) or `Environment.DIRECTORY_DOWNLOADS` (older), and then fires `Intent.ACTION_VIEW` via FileProvider to open the file. Toast confirms "Downloaded: Downloads/MPumpCalc/<filename>".

## Pending/Future Tasks
- Refactor `ZAPTRStyleCalculator.jsx` (>3,500 lines) into smaller logical components.
- Add app icon for Android build.

## Code Review Cleanup (Feb 2026)
- **Deleted dead Firebase/Auth files** (~1500 lines): `services/firebase.js`, `services/firebaseSync.js`, `contexts/AuthContext.js`, `components/{LoginScreen,SyncStatus,DeviceLinking,SyncDebugPanel}.jsx`. Removed `firebase` npm dep (`yarn remove firebase`). Verified no live imports remain.
- **Slimmed backend to stub** (442 → 35 lines): Replaced `server.py` with minimal FastAPI stub serving `/api/status`. Deleted unused `auth_models.py`, `auth_utils.py`, `token_utils.py`, `sync_models.py`. Supervisor-safe; frontend unaffected (app is offline).
- **Empty catch hardened**: `HeaderSettings.jsx:270` now logs `console.warn` for corrupt contact-info parse instead of silent swallow.
- **Perf**: Added `useMemo` for ledger totals in `CustomerLedger.jsx` (two `.reduce()` calls previously running on every render) — totals now computed once per `ledgerData` change.
- **Hook deps audited** (`use-auto-backup.js`, `use-auto-backup-weekly.js`, `ZAPTRStyleCalculator.jsx`): No genuine bugs. Existing dep arrays correctly exclude stable refs (imports, module-level constants, `useRef`, state setters). ESLint (`react-hooks/exhaustive-deps`) reports 0 issues.
- **Security note**: localStorage "sensitive data" findings rejected — this app by design stores non-sensitive business data entirely on-device for offline use; encryption adds no security since an attacker with device access also has the decryption code.
- Synced fresh `yarn build` to `/app/android/app/src/main/assets/www/` — ready for APK rebuild.
