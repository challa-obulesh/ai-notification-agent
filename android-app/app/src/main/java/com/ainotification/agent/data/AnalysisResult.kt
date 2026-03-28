package com.ainotification.agent.data

import com.google.gson.annotations.SerializedName

data class AnalysisResult(
    @SerializedName("status") val status: String = "",
    @SerializedName("original_message") val originalMessage: String = "",
    @SerializedName("label") val label: String = "",
    @SerializedName("confidence") val confidence: Double = 0.0,
    @SerializedName("importance") val importance: String = "",
    @SerializedName("category") val category: String = "",
    @SerializedName("icon") val icon: String = "📩",
    @SerializedName("explanation") val explanation: String = "",
    @SerializedName("detail") val detail: String? = null,
    @SerializedName("action_required") val actionRequired: Boolean = false,
    @SerializedName("model_used") val modelUsed: String? = null,
    @SerializedName("processing_time_ms") val processingTimeMs: Double = 0.0
)

data class NotificationItem(
    val id: String,
    val appName: String,
    val packageName: String,
    val rawText: String,
    val timestamp: Long,
    val analysisResult: AnalysisResult? = null,
    val isAnalyzing: Boolean = false,
    val error: String? = null
)
