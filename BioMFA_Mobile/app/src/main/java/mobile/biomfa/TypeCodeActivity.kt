package mobile.biomfa

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity

class TypeCodeActivity : AppCompatActivity() {

    private lateinit var codeInput: EditText
    private lateinit var nextButton: Button

    @SuppressLint("MissingInflatedId")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_type_code)

        codeInput = findViewById(R.id.code_input)
        nextButton = findViewById(R.id.next_button)

        codeInput.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                nextButton.isEnabled = s?.length == 6
            }

            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {
            }

            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
            }
        })

        nextButton.setOnClickListener {
            val code = codeInput.text.toString()
            if (isValidCode(code)) {
                val intent = Intent(this, ScanImplantActivity::class.java)
                startActivity(intent)
            } else {
                // error message or invalid code handling
            }
        }
    }

    private fun isValidCode(code: String): Boolean {
        return code.length == 6 && code.matches(Regex("\\d+"))
    }
}
