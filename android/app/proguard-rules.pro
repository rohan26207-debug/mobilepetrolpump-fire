# ProGuard rules
-keepattributes JavascriptInterface
-keepclassmembers class com.rohan.mpump.MainActivity$WebAppInterface {
    @android.webkit.JavascriptInterface <methods>;
}
