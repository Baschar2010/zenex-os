package org.zenex.launcher

import android.content.Context

class LauncherPreferences(context: Context) {
    private val store = context.getSharedPreferences("launcher_preferences", Context.MODE_PRIVATE)

    var homeStyle: String
        get() = store.getString(KEY_HOME_STYLE, ANDROID)?.takeIf { it == ANDROID || it == IOS } ?: ANDROID
        set(value) { store.edit().putString(KEY_HOME_STYLE, if (value == IOS) IOS else ANDROID).apply() }

    companion object {
        const val ANDROID = "android"
        const val IOS = "ios"
        private const val KEY_HOME_STYLE = "homeStyle"
    }
}
