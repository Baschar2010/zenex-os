package org.zenex.policy

import android.app.admin.DeviceAdminReceiver
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.UserManager
import android.util.Log

class ZenexAdminReceiver : DeviceAdminReceiver() {
    override fun onEnabled(context: Context, intent: Intent) {
        super.onEnabled(context, intent)
        val dpm = context.getSystemService(DevicePolicyManager::class.java)
        if (!dpm.isDeviceOwnerApp(context.packageName)) {
            Log.e(TAG, "ZENEX DNS policy requires fresh-device Device Owner enrollment")
            return
        }
        val host = context.getString(R.string.zenex_private_dns_host).trim()
        if (!HOST.matches(host)) {
            Log.e(TAG, "Private DNS host is missing or invalid; not claiming DNS is enforced")
            return
        }
        val admin = ComponentName(context, ZenexAdminReceiver::class.java)
        val result = dpm.setGlobalPrivateDnsModeSpecifiedHost(admin, host)
        if (result != DevicePolicyManager.PRIVATE_DNS_SET_NO_ERROR) {
            Log.e(TAG, "Could not set strict Private DNS (result=$result); configuration remains unmanaged")
            return
        }
        dpm.addUserRestriction(admin, UserManager.DISALLOW_CONFIG_PRIVATE_DNS)
        Log.i(TAG, "Strict Private DNS configured and user changes restricted")
    }

    companion object {
        private const val TAG = "ZenexPolicy"
        private val HOST = Regex("(?i)^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z]{2,63}$")
    }
}
