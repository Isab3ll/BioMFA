package mobile.biomfa

import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity

class InfoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_info)

        val returnButton: Button = findViewById(R.id.return_button)
        returnButton.setOnClickListener {
            finish()
        }
    }
}
