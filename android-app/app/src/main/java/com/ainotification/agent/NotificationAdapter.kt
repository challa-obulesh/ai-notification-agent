package com.ainotification.agent

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.ainotification.agent.data.NotificationItem
import com.ainotification.agent.databinding.ItemNotificationBinding
import java.text.SimpleDateFormat
import java.util.*

class NotificationAdapter :
    ListAdapter<NotificationItem, NotificationAdapter.VH>(Diff()) {

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = VH(
        ItemNotificationBinding.inflate(LayoutInflater.from(parent.context), parent, false)
    )

    override fun onBindViewHolder(holder: VH, position: Int) = holder.bind(getItem(position))

    class VH(private val b: ItemNotificationBinding) : RecyclerView.ViewHolder(b.root) {
        private val fmt = SimpleDateFormat("HH:mm:ss", Locale.getDefault())

        fun bind(item: NotificationItem) {
            b.tvAppName.text = item.appName
            b.tvMessage.text = item.rawText
            b.tvTime.text    = fmt.format(Date(item.timestamp))

            // States
            b.loadingGroup.visibility  = if (item.isAnalyzing) View.VISIBLE else View.GONE
            b.errorGroup.visibility    = if (!item.isAnalyzing && item.error != null) View.VISIBLE else View.GONE
            b.analysisGroup.visibility = if (item.analysisResult != null) View.VISIBLE else View.GONE

            if (item.error != null) b.tvError.text = "⚠ ${item.error}"

            val r = item.analysisResult ?: return
            b.tvIcon.text        = r.icon
            b.tvCategory.text    = r.category
            b.tvImportance.text  = r.importance
            b.tvExplanation.text = r.explanation
            b.tvConfidence.text  = "%.0f%%".format(r.confidence * 100)

            val color = when (r.importance) {
                "HIGH"   -> ContextCompat.getColor(b.root.context, R.color.importance_high)
                "MEDIUM" -> ContextCompat.getColor(b.root.context, R.color.importance_medium)
                else     -> ContextCompat.getColor(b.root.context, R.color.importance_low)
            }
            b.importanceStripe.setBackgroundColor(color)
            b.tvImportance.setTextColor(color)

            b.tvDetail.visibility = if (!r.detail.isNullOrBlank()) View.VISIBLE else View.GONE
            b.tvDetail.text       = r.detail ?: ""

            b.tvActionRequired.visibility = if (r.actionRequired) View.VISIBLE else View.GONE
        }
    }

    class Diff : DiffUtil.ItemCallback<NotificationItem>() {
        override fun areItemsTheSame(o: NotificationItem, n: NotificationItem) = o.id == n.id
        override fun areContentsTheSame(o: NotificationItem, n: NotificationItem) = o == n
    }
}
