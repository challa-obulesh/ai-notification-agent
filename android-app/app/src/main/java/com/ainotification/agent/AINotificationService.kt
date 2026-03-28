package com.ainotification.agent

import android.content.Intent
import android.os.Build
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log

class AINotificationService : NotificationListenerService() {

    companion object {
        private const val TAG = "AINotifService"
        const val ACTION_NEW_NOTIFICATION = "com.ainotification.agent.NEW_NOTIFICATION"
        const val EXTRA_PACKAGE    = "extra_package"
        const val EXTRA_APP_NAME  = "extra_app_name"
        const val EXTRA_TEXT      = "extra_text"
        const val EXTRA_TIMESTAMP = "extra_timestamp"

        private val IGNORED_PACKAGES = setOf(
            "android",
            "com.android.systemui",
            "com.google.android.googlequicksearchbox",
            "com.android.settings"
        )
    }

    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val pkg = sbn.packageName ?: return
        if (pkg in IGNORED_PACKAGES) return

        val extras = sbn.notification?.extras ?: return
        val title   = extras.getString("android.title") ?: ""
        val text    = extras.getCharSequence("android.text")?.toString() ?: ""
        val bigText = extras.getCharSequence("android.bigText")?.toString() ?: ""

        val fullText = buildString {
            if (title.isNotBlank()) append(title)
            val body = bigText.ifBlank { text }
            if (body.isNotBlank()) {
                if (isNotEmpty()) append(": ")
                append(body)
            }
        }.trim()

        if (fullText.isBlank()) return
        Log.d(TAG, "[$pkg] $fullText")

        val intent = Intent(ACTION_NEW_NOTIFICATION).apply {
            setPackage(packageName)
            putExtra(EXTRA_PACKAGE,    pkg)
            putExtra(EXTRA_APP_NAME,  getAppLabel(pkg))
            putExtra(EXTRA_TEXT,      fullText)
            putExtra(EXTRA_TIMESTAMP, sbn.postTime)
        }
        sendBroadcast(intent)
    }

    private fun getAppLabel(pkg: String): String = try {
        val info = packageManager.getApplicationInfo(pkg, 0)
        packageManager.getApplicationLabel(info).toString()
    } catch (e: Exception) { pkg }
}
