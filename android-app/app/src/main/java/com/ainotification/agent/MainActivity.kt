package com.ainotification.agent

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.View
import android.view.inputmethod.EditorInfo
import android.view.inputmethod.InputMethodManager
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import com.ainotification.agent.databinding.ActivityMainBinding
import com.google.android.material.dialog.MaterialAlertDialogBuilder

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val vm: MainViewModel by viewModels()
    private lateinit var adapter: NotificationAdapter

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(ctx: Context, intent: Intent) {
            if (intent.action != AINotificationService.ACTION_NEW_NOTIFICATION) return
            val pkg       = intent.getStringExtra(AINotificationService.EXTRA_PACKAGE) ?: return
            val appName   = intent.getStringExtra(AINotificationService.EXTRA_APP_NAME) ?: pkg
            val text      = intent.getStringExtra(AINotificationService.EXTRA_TEXT) ?: return
            val timestamp = intent.getLongExtra(AINotificationService.EXTRA_TIMESTAMP, System.currentTimeMillis())
            vm.addAndAnalyze(appName, pkg, text, timestamp)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setupToolbar()
        setupRecycler()
        setupInput()
        setupObservers()
        checkPermission()
        vm.checkHealth()
    }

    override fun onResume() {
        super.onResume()
        refreshPermissionBanner()
        vm.checkHealth()
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter(AINotificationService.ACTION_NEW_NOTIFICATION)
        if (Build.VERSION.SDK_INT >= 33)
            registerReceiver(receiver, filter, RECEIVER_NOT_EXPORTED)
        else
            registerReceiver(receiver, filter)
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(receiver)
    }

    // ── Setup ──────────────────────────────────────────────────────────────────

    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        binding.btnSettings.setOnClickListener {
            startActivity(Intent(this, SettingsActivity::class.java))
        }
    }

    private fun setupRecycler() {
        adapter = NotificationAdapter()
        binding.recyclerView.layoutManager = LinearLayoutManager(this)
        binding.recyclerView.adapter = adapter
        binding.btnClear.setOnClickListener { vm.clearAll() }
    }

    private fun setupInput() {
        binding.editTextTest.setOnEditorActionListener { _, id, _ ->
            if (id == EditorInfo.IME_ACTION_SEND) { submit(); true } else false
        }
        binding.btnAnalyze.setOnClickListener { submit() }
    }

    private fun setupObservers() {
        vm.items.observe(this) { list ->
            adapter.submitList(list.toList())
            binding.emptyState.visibility   = if (list.isEmpty()) View.VISIBLE else View.GONE
            binding.recyclerView.visibility = if (list.isEmpty()) View.GONE   else View.VISIBLE
            binding.btnClear.isEnabled      = list.isNotEmpty()
        }
        vm.apiOnline.observe(this) { online ->
            binding.statusDot.setCardBackgroundColor(
                ContextCompat.getColor(this,
                    if (online) R.color.status_online else R.color.status_offline)
            )
            binding.statusText.text = if (online) "API Online" else "API Offline"
        }
        vm.stats.observe(this) { (total, imp, rot) ->
            binding.tvTotal.text       = total.toString()
            binding.tvImportant.text   = imp.toString()
            binding.tvRoutine.text     = rot.toString()
        }
    }

    // ── Actions ────────────────────────────────────────────────────────────────

    private fun submit() {
        val text = binding.editTextTest.text?.toString()?.trim() ?: return
        if (text.isBlank()) { binding.editTextTest.error = "Enter notification text"; return }
        vm.analyzeManual(text)
        binding.editTextTest.setText("")
        hideKeyboard()
    }

    private fun hideKeyboard() {
        (getSystemService(INPUT_METHOD_SERVICE) as InputMethodManager)
            .hideSoftInputFromWindow(binding.root.windowToken, 0)
    }

    // ── Permissions ────────────────────────────────────────────────────────────

    private fun checkPermission() {
        if (!isListenerEnabled()) showPermissionDialog()
        refreshPermissionBanner()
    }

    private fun refreshPermissionBanner() {
        binding.permissionBanner.visibility =
            if (isListenerEnabled()) View.GONE else View.VISIBLE
        binding.btnGrantPermission.setOnClickListener { openListenerSettings() }
    }

    private fun isListenerEnabled(): Boolean {
        val flat = Settings.Secure.getString(contentResolver, "enabled_notification_listeners") ?: return false
        return flat.contains(packageName)
    }

    private fun showPermissionDialog() {
        MaterialAlertDialogBuilder(this)
            .setTitle("Notification Access Required")
            .setMessage("Allow AI Notification Agent to read notifications so it can classify them automatically.")
            .setPositiveButton("Grant Access") { _, _ -> openListenerSettings() }
            .setNegativeButton("Later", null)
            .show()
    }

    private fun openListenerSettings() =
        startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
}
