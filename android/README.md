# Manager Pump - Android App

## How to Build in Android Studio

### Step 1: Download the `android` folder
Download the entire `/app/android/` folder from this project using "Save to Github" then clone, or download as ZIP.

### Step 2: Open in Android Studio
1. Open Android Studio
2. Click **File > Open**
3. Select the `android` folder
4. Wait for Gradle sync to complete

### Step 3: The web app is already bundled
The React web app build files are already in `app/src/main/assets/www/`. No extra setup needed.

### Step 4: Add App Icon
Replace the placeholder icons in `app/src/main/res/mipmap-*/` with your app icon.
You can use Android Studio's **Image Asset Studio**: Right-click `res` > New > Image Asset.

### Step 5: Build & Run
1. Connect your Android phone via USB (enable Developer Mode + USB Debugging)
2. Click the green **Run** button in Android Studio
3. Select your device
4. The app will install and open

### Step 6: Generate APK
1. Go to **Build > Build Bundle(s)/APK(s) > Build APK(s)**
2. Wait for build to complete
3. Click **locate** in the notification to find the APK
4. The APK will be in `app/build/outputs/apk/debug/app-debug.apk`

### Step 7: Generate Signed APK (for Play Store)
1. Go to **Build > Generate Signed Bundle/APK**
2. Choose APK
3. Create a new keystore or use existing
4. Build release APK

---

## Project Structure
```
android/
├── build.gradle                    # Root build config
├── settings.gradle                 # Project settings
├── gradle/wrapper/                 # Gradle wrapper
├── app/
│   ├── build.gradle                # App build config (minSdk 24, targetSdk 34)
│   ├── proguard-rules.pro          # ProGuard rules
│   └── src/main/
│       ├── AndroidManifest.xml     # App permissions & config
│       ├── java/com/rohan/mpump/
│       │   └── MainActivity.java   # WebView + JavaScript bridge
│       ├── assets/www/             # Bundled React web app (from build)
│       │   ├── index.html
│       │   └── static/
│       └── res/
│           ├── values/styles.xml   # App theme
│           ├── values/strings.xml  # App name
│           ├── xml/file_paths.xml  # FileProvider config
│           └── mipmap-*/           # App icons (add your own)
```

## Features
- **100% Offline** - All data stored in WebView localStorage
- **File Import/Export** - File chooser works for backup import/merge
- **Print Support** - Uses Android PrintManager for PDF generation
- **PDF Save** - Saves PDFs to app-specific storage, opens with PDF viewer
- **Back Button** - Navigates back in WebView history

## Updating the Web App
When you make changes to the React app:
1. Run `yarn build` in the frontend folder
2. Copy `build/*` to `android/app/src/main/assets/www/`
3. Rebuild the Android app

## Requirements
- Android Studio Arctic Fox or newer
- Android SDK 34
- Min Android version: 7.0 (API 24)
- Java 8+
