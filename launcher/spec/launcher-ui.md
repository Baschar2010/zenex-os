# ZENEX Launcher UI engine

## Product behavior

- A single launcher shell supports two persisted presentation profiles:
  `android` (home pages, widgets, app drawer) and `ios` (icon pages, dock,
  app library and a control-center surface).
- This is a ZENEX design language inspired by familiar interaction patterns;
  it must not copy Apple artwork, proprietary icons, fonts, or exact screen
  layouts. The owner's ZENEX bolt/wordmark is the identity.
- Switching profile changes layout and navigation only. Installed apps,
  permissions, account data, accessibility choices and DNS policy remain intact.
- Switch is available at Settings → Appearance → Home layout. Apply immediately;
  announce the selected profile for screen readers and preserve the user's app
  ordering where possible. Offer undo for the current session.
- Motion can be disabled globally. Respect Android animator scale and reduced
  motion; do not use blur/transparency on low-RAM profile.

## Engine contract

`launcher/prototype/index.html` is a dependency-free responsive reference
prototype for the profile picker and home-screen layout preview. Production
mobile implementation belongs in an AOSP launcher app (Kotlin/Java) using
platform launcher APIs, persistent settings, adaptive layouts and system icon
badges. Desktop implementation is a separate shell frontend; this prototype is
not a native launcher or Android APK.

Profile schema:

```json
{
  "schema": 1,
  "homeStyle": "android",
  "reducedMotion": false,
  "iconScale": "large"
}
```

Validate `homeStyle` against `android|ios`; migrate unknown schema versions to a
safe default without resetting unrelated settings. Never use the choice to
weaken permission prompts, app sandboxing, verified boot, or network policy.

## Performance and accessibility gates

- Keep the 1 GiB profile to one page, no widgets, no live blur, no animation,
  and a small fixed number of cached icons; load app catalog on demand.
- Target 60 Hz on qualified hardware, but allow 30 Hz and static transitions
  under memory/GPU pressure. Avoid persistent background animation.
- Support keyboard, touch, screen-reader labels/focus order, scalable text,
  contrast, RTL, and reduced motion.
- Persist only layout preferences; no analytics or usage telemetry.
