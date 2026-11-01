# Include from the ZENEX AOSP product makefile. Set ZENEX_LOW_RAM_PROFILE=true
# from a model's product configuration for the two-frame, static fallback.
# Select an explicit resource profile. LOW_RAM means 1 GiB; standard targets
# 2 GiB and above. Do not infer RAM from host/VM configuration at build time.
ZENEX_LOW_RAM_PROFILE ?= false
ZENEX_BOOTANIMATION_DIR ?= device/zenex/common/boot-animation

ifeq ($(ZENEX_LOW_RAM_PROFILE),true)
ZENEX_BOOTANIMATION_ZIP := $(ZENEX_BOOTANIMATION_DIR)/bootanimation-lowram.zip
else
ZENEX_BOOTANIMATION_ZIP := $(ZENEX_BOOTANIMATION_DIR)/bootanimation.zip
endif

ifeq ($(wildcard $(ZENEX_BOOTANIMATION_ZIP)),)
$(error Missing selected ZENEX boot animation: $(ZENEX_BOOTANIMATION_ZIP))
endif

PRODUCT_COPY_FILES += \
    $(ZENEX_BOOTANIMATION_ZIP):system/media/bootanimation.zip
