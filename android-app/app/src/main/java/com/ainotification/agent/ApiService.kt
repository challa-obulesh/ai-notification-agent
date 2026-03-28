package com.ainotification.agent

import android.content.Context
import android.util.Log
import androidx.preference.PreferenceManager
import com.ainotification.agent.data.AnalysisResult
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

class ApiService(private val context: Context) {

    companion object {
        private const val TAG = "ApiService"
        const val DEFAULT_URL = "http://10.0.2.2:5000"
    }

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()

    fun getBaseUrl(): String {
        val prefs = PreferenceManager.getDefaultSharedPreferences(context)
        return prefs.getString("api_url", DEFAULT_URL)?.trimEnd('/') ?: DEFAULT_URL
    }

    suspend fun analyzeNotification(text: String): Result<AnalysisResult> {
        return withContext(Dispatchers.IO) {
            try {
                val json = gson.toJson(mapOf("text" to text))
                val body = json.toRequestBody("application/json".toMediaType())
                val request = Request.Builder()
                    .url("${getBaseUrl()}/api/analyze")
                    .post(body)
                    .build()
                val response = client.newCall(request).execute()
                val responseBody = response.body?.string() ?: ""
                if (response.isSuccessful) {
                    val result = gson.fromJson(responseBody, AnalysisResult::class.java)
                    Result.success(result)
                } else {
                    Result.failure(Exception("HTTP ${response.code}: $responseBody"))
                }
            } catch (e: Exception) {
                Log.e(TAG, "API call failed", e)
                Result.failure(e)
            }
        }
    }

    suspend fun checkHealth(): Boolean {
        return withContext(Dispatchers.IO) {
            try {
                val request = Request.Builder()
                    .url("${getBaseUrl()}/api/health")
                    .get()
                    .build()
                client.newCall(request).execute().isSuccessful
            } catch (e: Exception) {
                false
            }
        }
    }
}
