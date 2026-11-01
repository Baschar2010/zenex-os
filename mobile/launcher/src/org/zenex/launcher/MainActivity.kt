package org.zenex.launcher

import android.app.Activity
import android.app.ActivityManager
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.GridLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

class MainActivity : Activity() {
    private lateinit var prefs: LauncherPreferences
    private lateinit var root: LinearLayout
    private lateinit var content: LinearLayout
    private var lowRam = false
    private var showSettings = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        prefs = LauncherPreferences(this)
        val manager = getSystemService(ACTIVITY_SERVICE) as ActivityManager
        lowRam = manager.isLowRamDevice || manager.memoryClass <= 128
        render()
    }

    private fun render() {
        root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(18), dp(20), dp(14))
            setBackgroundColor(Color.rgb(8, 11, 19))
        }
        setContentView(root)
        val header = LinearLayout(this).apply {
            gravity = Gravity.CENTER_VERTICAL
            orientation = LinearLayout.HORIZONTAL
        }
        val brand = label("ϟ  ZENEX", 22, Color.rgb(70, 195, 255), true)
        header.addView(brand, LinearLayout.LayoutParams(0, dp(48), 1f))
        val settingsButton = button(if (showSettings) "Home" else "⚙") {
            showSettings = !showSettings
            render()
        }
        settingsButton.contentDescription = if (showSettings) "Return to home screen" else "Launcher appearance settings"
        header.addView(settingsButton)
        root.addView(header)

        content = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        root.addView(content, LinearLayout.LayoutParams(-1, 0, 1f))
        if (showSettings) renderSettings() else renderHome()
    }

    private fun renderSettings() {
        content.addView(label("Home layout", 28, Color.WHITE, true).apply { setPadding(0, dp(26), 0, dp(6)) })
        content.addView(label("Change the look of your home screen. Apps and privacy settings stay unchanged.", 15, 0xFFAFBDD0.toInt()))
        content.addView(profileButton("Android style", "Pages and app drawer", LauncherPreferences.ANDROID))
        content.addView(profileButton("iOS-inspired", "Icon pages and dock", LauncherPreferences.IOS))
        content.addView(label(if (lowRam) "Low-memory mode is active: effects and widgets are disabled." else "Low-memory mode is selected automatically on constrained devices.", 14, 0xFFAFBDD0.toInt()).apply { setPadding(0, dp(18), 0, 0) })
        if (lowRam) content.addView(label("Apps load on demand; the home screen uses one compact page.", 14, 0xFFAFBDD0.toInt()))
    }

    private fun profileButton(title: String, subtitle: String, profile: String): View {
        val selected = prefs.homeStyle == profile
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(17), dp(15), dp(17), dp(15))
            background = rounded(if (selected) 0xFF153B61.toInt() else 0xFF141E2E.toInt(), dp(18), if (selected) 0xFF168CFF.toInt() else 0xFF29364B.toInt())
            isClickable = true
            isFocusable = true
            contentDescription = "$title. $subtitle${if (selected) ". Selected" else ""}"
            setOnClickListener { prefs.homeStyle = profile; render() }
        }
        row.addView(label(title, 17, Color.WHITE, true))
        row.addView(label(subtitle + if (selected) "  ✓" else "", 14, 0xFFAFBDD0.toInt()))
        val lp = LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(14) }
        row.layoutParams = lp
        return row
    }

    private fun renderHome() {
        content.addView(label(if (prefs.homeStyle == LauncherPreferences.IOS) "Your apps" else "Home", 27, Color.WHITE, true).apply { setPadding(0, dp(18), 0, dp(2)) })
        if (!lowRam && prefs.homeStyle == LauncherPreferences.ANDROID) {
            content.addView(label("Favorites and apps", 14, 0xFFAFBDD0.toInt()))
        }
        val apps = loadLauncherApps().take(if (lowRam) 12 else 48)
        if (apps.isEmpty()) {
            content.addView(label("No launchable apps found", 16, 0xFFAFBDD0.toInt()))
            return
        }
        val scroll = ScrollView(this)
        val grid = GridLayout(this).apply {
            columnCount = if (lowRam) 3 else if (resources.configuration.smallestScreenWidthDp >= 600) 6 else 4
            useDefaultMargins = true
            setPadding(0, dp(10), 0, dp(8))
        }
        apps.forEach { app -> grid.addView(appTile(app), GridLayout.LayoutParams().apply {
            width = 0
            height = dp(92)
            columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f)
            setMargins(dp(3), dp(5), dp(3), dp(5))
        }) }
        scroll.addView(grid)
        content.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        if (prefs.homeStyle == LauncherPreferences.IOS && !lowRam) {
            val dock = LinearLayout(this).apply {
                gravity = Gravity.CENTER
                setPadding(dp(9), dp(7), dp(9), dp(7))
                background = rounded(0xFF172235.toInt(), dp(24))
            }
            apps.take(4).forEach { app ->
                val icon = iconView(app, compact = true)
                dock.addView(icon, LinearLayout.LayoutParams(dp(50), dp(54)).apply { marginStart = dp(4); marginEnd = dp(4) })
            }
            root.addView(dock, LinearLayout.LayoutParams(-1, dp(66)).apply { topMargin = dp(8) })
        }
    }

    private fun loadLauncherApps(): List<ApplicationInfo> {
        val pm = packageManager
        val intent = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        return try {
            pm.queryIntentActivities(intent, PackageManager.MATCH_ALL)
                .map { it.activityInfo.applicationInfo }
                .distinctBy { it.packageName }
                .filterNot { it.packageName == packageName }
                .sortedBy { pm.getApplicationLabel(it).toString().lowercase() }
        } catch (_: RuntimeException) { emptyList() }
    }

    private fun appTile(info: ApplicationInfo): View {
        val box = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            isClickable = true
            isFocusable = true
            setOnClickListener { launch(info) }
            contentDescription = packageManager.getApplicationLabel(info).toString()
        }
        box.addView(iconView(info, compact = false), LinearLayout.LayoutParams(dp(if (lowRam) 48 else 54), dp(if (lowRam) 48 else 54)))
        val title = packageManager.getApplicationLabel(info).toString()
        box.addView(label(title, 12, Color.WHITE).apply { gravity = Gravity.CENTER; maxLines = 1; ellipsize = android.text.TextUtils.TruncateAt.END })
        return box
    }

    private fun iconView(info: ApplicationInfo, compact: Boolean): View {
        val size = if (compact) 50 else if (lowRam) 48 else 54
        return ImageView(this).apply {
            background = rounded(0xFF18283D.toInt(), dp(if (prefs.homeStyle == LauncherPreferences.IOS) 17 else 12))
            scaleType = ImageView.ScaleType.FIT_CENTER
            setPadding(dp(6), dp(6), dp(6), dp(6))
            try { setImageDrawable(packageManager.getApplicationIcon(info)) } catch (_: Exception) { setImageResource(android.R.drawable.sym_def_app_icon) }
            contentDescription = packageManager.getApplicationLabel(info)
            layoutParams = ViewGroup.LayoutParams(dp(size), dp(size))
        }
    }

    private fun launch(info: ApplicationInfo) {
        val intent = packageManager.getLaunchIntentForPackage(info.packageName) ?: return
        try { startActivity(intent) } catch (_: RuntimeException) { }
    }

    private fun label(text: String, size: Int, color: Int, bold: Boolean = false) = TextView(this).apply {
        this.text = text
        textSize = size.toFloat()
        setTextColor(color)
        if (bold) typeface = Typeface.create("sans-serif", Typeface.BOLD)
        gravity = Gravity.CENTER_VERTICAL
    }

    private fun button(text: String, action: () -> Unit) = Button(this).apply {
        this.text = text
        setTextColor(Color.WHITE)
        setBackgroundColor(Color.TRANSPARENT)
        contentDescription = text
        setOnClickListener { action() }
    }

    private fun rounded(color: Int, radius: Int, stroke: Int? = null) = GradientDrawable().apply {
        setColor(color); cornerRadius = radius.toFloat()
        stroke?.let { setStroke(dp(1), it) }
    }

    private fun dp(value: Int) = (value * resources.displayMetrics.density + 0.5f).toInt()
}
