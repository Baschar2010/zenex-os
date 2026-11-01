# Native ZENEX AOSP launcher scaffold

This is a first native Kotlin HOME activity scaffold, built against Android
platform APIs through Soong (`Android.bp`) with no third-party runtime libraries.
It stores the Android-style/iOS-inspired choice in private app preferences,
shows installed launchable apps, and adds a lightweight dock in the iOS-inspired
profile. It detects Android's low-RAM device flag (or a small memory class) and
reduces the grid to one compact set, omits widgets/dock effects, and keeps icons
loaded on demand.

To integrate in an AOSP product, add `ZenexLauncher` to the product package list
using `mobile/product/zenex_launcher.mk` and make it the configured default HOME component. Verify platform build support
for Kotlin source in the chosen pinned AOSP branch. This is a starter implementation:
it does not yet provide widget hosting, drag/drop ordering, app-library search,
system settings integration, persistent home placement, or the owner's image
assets. It has not been compiled because no AOSP checkout/Android SDK build tree
exists in this workspace.

Low-RAM qualification must include 1 GiB devices, process trimming, accessibility,
rotation/tablet layouts, package visibility, icon loading behavior, app launch
latency, and profile persistence through process/device restart. The launcher
does not request or modify Private DNS/network policy.
