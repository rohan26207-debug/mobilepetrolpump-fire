# 🧪 Test Device Linking Feature

## Step-by-Step Testing Guide

### Pre-requisites ✅

Before testing, ensure:
1. ✅ Firestore security rules are updated (see `/app/FIRESTORE_RULES_UPDATE_REQUIRED.md`)
2. ✅ Anonymous auth is enabled in Firebase Console
3. ✅ App is running at https://data-management-hub-3.preview.emergentagent.com

---

## Test 1: Generate Link Code

### Steps:
1. Open app in **Browser 1** (Chrome)
2. Click **Settings** (⚙️) icon
3. Click **Device Sync** tab
4. Click **"Generate Link Code"** button

### Expected Result:
✅ A 6-digit code appears (e.g., `485921`)
✅ Code is displayed in a blue box
✅ "Valid for 10 minutes" message shows
✅ Copy button appears next to code

### If It Fails:
❌ **Error: "Permission denied"**
- Cause: Firestore rules not updated
- Fix: Update rules in Firebase Console (see guide)

❌ **Error: "User not authenticated"**
- Cause: Anonymous auth failed
- Fix: Check Firebase Console → Authentication → Anonymous enabled

---

## Test 2: Link Another Device

### Steps:
1. **Keep Browser 1 open** with the generated code
2. Open app in **Browser 2** (Firefox/Edge/Incognito Chrome)
3. Click **Settings** → **Device Sync** tab
4. Enter the **6-digit code** from Browser 1
5. Click **"Link This Device"**

### Expected Result:
✅ Success message: "Device Linked Successfully! 🎉"
✅ Page reloads automatically after 2 seconds
✅ Browser 2 is now linked to Browser 1's account

### If It Fails:
❌ **Error: "Invalid Code"**
- Cause: Code doesn't exist or already used
- Fix: Generate a fresh code

❌ **Error: "Code Expired"**
- Cause: More than 10 minutes passed
- Fix: Generate a new code

❌ **Error: "Permission denied"**
- Cause: Firestore rules not allowing reads
- Fix: Update rules (ensure `allow read: if isAuthenticated()`)

---

## Test 3: Verify Cross-Device Sync

### Steps:
1. In **Browser 1**: Add a customer
   - Settings → Customer tab
   - Add customer: "Test Customer"
   - Save

2. In **Browser 2**: Check if customer appears
   - Go to Sales Tracker (main page)
   - Look for sync indicators in console (F12)

### Expected Result:
✅ Customer appears in Browser 2 within 1-2 seconds
✅ Console logs show: `🔔 Customer snapshot received!`
✅ UI updates automatically

### Browser Console Commands:

In Browser 2, open console (F12) and run:
```javascript
// Check sync status
window.diagnoseFirebaseSync()

// Manually pull data
window.manualPullFirebase()
```

---

## Test 4: Verify User ID Linking

### Steps:
1. In **Browser 1** console (F12):
```javascript
console.log('Browser 1 User ID:', auth.currentUser.uid)
console.log('Linked ID:', localStorage.getItem('linkedUserId'))
```

2. In **Browser 2** console (F12):
```javascript
console.log('Browser 2 User ID:', auth.currentUser.uid)
console.log('Linked ID:', localStorage.getItem('linkedUserId'))
```

### Expected Result:
✅ Browser 1: `linkedUserId` = `null` (primary device)
✅ Browser 2: `linkedUserId` = matches Browser 1's `uid`

Example:
```
Browser 1:
  currentUser.uid: aXScj1A0Cnd1kOU5n3X9yfbknvA3
  linkedUserId: null

Browser 2:
  currentUser.uid: KaV0JsDH97gh7UssBRFzwY5XuBx1
  linkedUserId: aXScj1A0Cnd1kOU5n3X9yfbknvA3  ← Points to Browser 1!
```

---

## Test 5: Code Expiry (Optional)

### Steps:
1. Generate a code in Browser 1
2. Wait 11 minutes (code expires after 10 minutes)
3. Try to use the code in Browser 2

### Expected Result:
✅ Error: "Code Expired"
✅ Code is automatically deleted from Firestore

---

## Test 6: One-Time Use (Optional)

### Steps:
1. Generate a code in Browser 1
2. Use it successfully in Browser 2
3. Try to use the same code again in Browser 3

### Expected Result:
✅ Error: "Invalid Code" (code was deleted after first use)

---

## Debugging Checklist

If tests fail, check:

### 1. Firestore Rules
```bash
# In Firebase Console → Firestore → Rules
# Verify this section exists:
match /deviceLinks/{linkCode} {
  allow create: if isAuthenticated();
  allow read: if isAuthenticated();
  allow delete: if isAuthenticated() && isOwner(resource.data.userId);
}
```

### 2. Anonymous Auth
- Firebase Console → Authentication
- Sign-in method → Anonymous → Enabled

### 3. Browser Console Logs
Look for:
- `🔗 Generating link code...`
- `📝 Writing to Firestore:`
- `🔗 Attempting to link device with code:`
- `📥 Link document retrieved:`

### 4. Firestore Data
- Firebase Console → Firestore Database
- Check if `deviceLinks` collection appears
- Documents should have 10-minute TTL

---

## Success Criteria ✅

All tests pass when:
1. ✅ Code generation works without errors
2. ✅ Device linking succeeds
3. ✅ Data syncs between devices in real-time
4. ✅ Linked device uses primary device's user ID
5. ✅ Codes expire after 10 minutes
6. ✅ Codes are single-use

---

## Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| Permission denied | Rules not updated | Update Firestore rules |
| User not authenticated | Anonymous auth off | Enable in Firebase Console |
| Invalid Code | Code expired/used | Generate new code |
| Code Expired | >10 minutes passed | Generate new code |
| No sync happening | Not properly linked | Re-link devices |

---

## Manual Testing Script

Run this in Browser 2 console after linking:

```javascript
// Test sync manually
(async () => {
  const { db, auth } = window;
  const { collection, getDocs, query, where } = await import('firebase/firestore');
  
  const userId = localStorage.getItem('linkedUserId') || auth.currentUser.uid;
  console.log('Testing with User ID:', userId);
  
  // Check customers
  const customersQuery = query(collection(db, 'customers'), where('userId', '==', userId));
  const customersSnapshot = await getDocs(customersQuery);
  console.log('✅ Customers found:', customersSnapshot.size);
  
  // Check sales
  const salesQuery = query(collection(db, 'sales'), where('userId', '==', userId));
  const salesSnapshot = await getDocs(salesQuery);
  console.log('✅ Sales found:', salesSnapshot.size);
})();
```

---

**After all tests pass, the Device Linking feature is fully functional!** 🚀
