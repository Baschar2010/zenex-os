# ZENEX Private DNS device policy

`ZenexPolicy` is a small AOSP privileged Device Policy Controller receiver. On
`onEnabled`, it checks that it is the device owner, sets strict Private DNS to
the build-selected hostname, and only then applies
`UserManager.DISALLOW_CONFIG_PRIVATE_DNS`. A bad or unavailable host leaves the
policy unenforced and is logged; it never reports success on a failed API call.

The Settings overlay hides the ordinary Private DNS editor. That is a usability
measure; the Device Owner restriction is the enforcement mechanism. The app
must be enrolled as Device Owner during initial device provisioning, which is
only available on an eligible freshly provisioned device. It cannot silently
take ownership on a normal already-configured phone. Reflash/factory reset by
the device owner remains outside this policy boundary.

The build bundle substitutes `ZENEX_PRIVATE_DNS_HOST` into the policy resource.
It must be a hostname served by a real DoT resolver with a valid certificate;
no provider is selected or invented in this repository. This DPC does not
implement DNS filtering itself; the selected resolver must apply the ZENEX list.

The Settings resource overlay hides the manual editor. The framework overlay at
`mobile/overlay/frameworks/base/core/res/res/values/config.xml` only selects the
ZENEX launcher for secondary displays; Android has no primary-launcher selector
there. Primary HOME is assigned by the product preferred-activities file.
