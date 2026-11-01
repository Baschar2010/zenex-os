# Include from a pinned AOSP device/product makefile.
ZENEX_COMMON_PATH ?= device/zenex/common
ZENEX_BOOTANIMATION_DIR := $(ZENEX_COMMON_PATH)/boot-animation

PRODUCT_PACKAGES += ZenexLauncher ZenexPolicy
PRODUCT_PACKAGE_OVERLAYS += $(ZENEX_COMMON_PATH)/overlay

# PackageManager reads preferred HOME activities from system partition etc/preferred-apps.
PRODUCT_COPY_FILES += \
    $(ZENEX_COMMON_PATH)/preferred-apps/zenex-home.xml:$(TARGET_COPY_OUT_PRODUCT)/etc/preferred-apps/zenex-home.xml

# Keep the selected DoT endpoint and bootstrap address visible to system setup.
PRODUCT_COPY_FILES += \
    $(ZENEX_COMMON_PATH)/dns/dot-provider.json:$(TARGET_COPY_OUT_PRODUCT)/etc/zenex/dot-provider.json

include $(ZENEX_COMMON_PATH)/product/zenex_bootanimation.mk
