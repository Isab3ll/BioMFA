package mobile.biomfa

import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity

class InfoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_info)

        val returnButton: Button = findViewById(R.id.return_button)
        returnButton.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#363636"))
        returnButton.setOnClickListener {
            finish()
        }
    }
}
