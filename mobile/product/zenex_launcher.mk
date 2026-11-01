# Include from the ZENEX AOSP product definition.
PRODUCT_PACKAGES += ZenexLauncher

# Product integration must set the branch-specific default HOME component to
# org.zenex.launcher/.MainActivity through the supported framework mechanism.
# This file intentionally does not guess an overlay key that may vary by branch.
