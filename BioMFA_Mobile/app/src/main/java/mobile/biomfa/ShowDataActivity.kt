package mobile.biomfa

import android.annotation.SuppressLint
import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.text.Html
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

class ShowDataActivity : AppCompatActivity() {

    companion object {
        const val EXTRA_SCANNED_DATA = "extra_scanned_data"
        const val EXTRA_TAG_TYPE = "extra_tag_type"
    }

    @SuppressLint("MissingInflatedId", "SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_show_data)

        val returnButton: Button = findViewById(R.id.return_button)
        returnButton.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#363636"))
        returnButton.setOnClickListener {
            finish()
        }

        val dataTextView: TextView = findViewById(R.id.data_textview)
        val tagTypeTextView: TextView = findViewById(R.id.tag_type_textview)

        val scannedData = intent.getStringExtra(EXTRA_SCANNED_DATA)
        val tagType = intent.getStringExtra(EXTRA_TAG_TYPE)

        if (scannedData != null) {
            val formattedData = "<b>UID</b><br/>$scannedData"
            dataTextView.text = Html.fromHtml(formattedData, Html.FROM_HTML_MODE_COMPACT)
        } else {
            dataTextView.text = "No data found"
        }

        if (tagType != null) {
            val formattedData = "<b>Tag Type</b><br/>$tagType"
            tagTypeTextView.text = Html.fromHtml(formattedData, Html.FROM_HTML_MODE_COMPACT)
        } else {
            tagTypeTextView.text = "Unknown Tag Type"
        }
    }
}

