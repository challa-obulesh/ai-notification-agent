package com.ainotification.agent

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.ainotification.agent.data.AnalysisResult
import com.ainotification.agent.data.NotificationItem
import kotlinx.coroutines.launch
import java.util.UUID

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val api = ApiService(application)

    private val _items = MutableLiveData<List<NotificationItem>>(emptyList())
    val items: LiveData<List<NotificationItem>> = _items

    private val _apiOnline = MutableLiveData(false)
    val apiOnline: LiveData<Boolean> = _apiOnline

    // Triple(total, important, routine)
    private val _stats = MutableLiveData(Triple(0, 0, 0))
    val stats: LiveData<Triple<Int, Int, Int>> = _stats

    fun checkHealth() {
        viewModelScope.launch { _apiOnline.value = api.checkHealth() }
    }

    fun addAndAnalyze(appName: String, pkg: String, text: String, timestamp: Long) {
        val item = NotificationItem(
            id          = UUID.randomUUID().toString(),
            appName     = appName,
            packageName = pkg,
            rawText     = text,
            timestamp   = timestamp,
            isAnalyzing = true
        )
        _items.value = listOf(item) + (_items.value ?: emptyList())

        viewModelScope.launch {
            api.analyzeNotification(text)
                .onSuccess  { result -> updateItem(item.id, result, null) }
                .onFailure  { err    -> updateItem(item.id, null, err.message ?: "Unknown error") }
        }
    }

    fun analyzeManual(text: String) =
        addAndAnalyze("✏️ Manual Test", "manual", text, System.currentTimeMillis())

    private fun updateItem(id: String, result: AnalysisResult?, error: String?) {
        val list = _items.value?.toMutableList() ?: return
        val idx  = list.indexOfFirst { it.id == id }
        if (idx == -1) return
        list[idx] = list[idx].copy(analysisResult = result, isAnalyzing = false, error = error)
        _items.value = list
        if (result != null) recalcStats(result)
    }

    private fun recalcStats(result: AnalysisResult) {
        val cur = _stats.value ?: Triple(0, 0, 0)
        val imp = if (result.label == "important") cur.second + 1 else cur.second
        val rot = if (result.label != "important") cur.third  + 1 else cur.third
        _stats.value = Triple(cur.first + 1, imp, rot)
    }

    fun clearAll() {
        _items.value  = emptyList()
        _stats.value  = Triple(0, 0, 0)
    }
}
