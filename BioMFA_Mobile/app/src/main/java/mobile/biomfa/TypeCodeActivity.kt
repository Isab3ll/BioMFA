package mobile.biomfa

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.KeyEvent
import android.view.inputmethod.InputMethodManager
import android.widget.Button
import android.widget.EditText
import androidx.appcompat.app.AppCompatActivity

class TypeCodeActivity : AppCompatActivity() {

    private lateinit var codeInput1: EditText
    private lateinit var codeInput2: EditText
    private lateinit var codeInput3: EditText
    private lateinit var codeInput4: EditText
    private lateinit var codeInput5: EditText
    private lateinit var codeInput6: EditText
    private lateinit var nextButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_type_code)

        codeInput1 = findViewById(R.id.code_input1)
        codeInput2 = findViewById(R.id.code_input2)
        codeInput3 = findViewById(R.id.code_input3)
        codeInput4 = findViewById(R.id.code_input4)
        codeInput5 = findViewById(R.id.code_input5)
        codeInput6 = findViewById(R.id.code_input6)
        nextButton = findViewById(R.id.next_button)

        codeInput1.requestFocus()

        val textWatcher = object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                if (s?.length == 1) {
                    when (s) {
                        codeInput1.text -> codeInput2.requestFocus()
                        codeInput2.text -> codeInput3.requestFocus()
                        codeInput3.text -> codeInput4.requestFocus()
                        codeInput4.text -> codeInput5.requestFocus()
                        codeInput5.text -> codeInput6.requestFocus()
                    }
                } else if (s?.length == 0) {
                    when (s) {
                        codeInput1.text -> codeInput1.requestFocus()
                        codeInput2.text -> codeInput1.requestFocus()
                        codeInput3.text -> codeInput2.requestFocus()
                        codeInput4.text -> codeInput3.requestFocus()
                        codeInput5.text -> codeInput4.requestFocus()
                        codeInput6.text -> codeInput5.requestFocus()
                    }
                }
            }

            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {
                // Empty implementation
            }

            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                // Empty implementation
            }
        }

        codeInput1.addTextChangedListener(textWatcher)
        codeInput2.addTextChangedListener(textWatcher)
        codeInput3.addTextChangedListener(textWatcher)
        codeInput4.addTextChangedListener(textWatcher)
        codeInput5.addTextChangedListener(textWatcher)
        codeInput6.addTextChangedListener(textWatcher)

        // Obsługa klawisza cofania (backspace)
        codeInput1.setOnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_DEL && event.action == KeyEvent.ACTION_DOWN) {
                codeInput1.text.clear()
                codeInput1.requestFocus()
                true
            } else {
                false
            }
        }

        codeInput2.setOnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_DEL && event.action == KeyEvent.ACTION_DOWN) {
                codeInput2.text.clear()
                codeInput1.requestFocus()
                true
            } else {
                false
            }
        }

        codeInput3.setOnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_DEL && event.action == KeyEvent.ACTION_DOWN) {
                codeInput3.text.clear()
                codeInput2.requestFocus()
                true
            } else {
                false
            }
        }

        codeInput4.setOnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_DEL && event.action == KeyEvent.ACTION_DOWN) {
                codeInput4.text.clear()
                codeInput3.requestFocus()
                true
            } else {
                false
            }
        }

        codeInput5.setOnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_DEL && event.action == KeyEvent.ACTION_DOWN) {
                codeInput5.text.clear()
                codeInput4.requestFocus()
                true
            } else {
                false
            }
        }

        codeInput6.setOnKeyListener { _, keyCode, event ->
            if (keyCode == KeyEvent.KEYCODE_DEL && event.action == KeyEvent.ACTION_DOWN) {
                codeInput6.text.clear()
                codeInput5.requestFocus()
                true
            } else {
                false
            }
        }

        nextButton.setOnClickListener {
            val code = "${codeInput1.text}${codeInput2.text}${codeInput3.text}${codeInput4.text}${codeInput5.text}${codeInput6.text}"
            if (isValidCode(code)) {
                val intent = Intent(this, ScanImplantActivity::class.java)
                startActivity(intent)
            } else {
                // Error message or invalid code handling
            }
        }
    }

    private fun isValidCode(code: String): Boolean {
        return code.length == 6 && code.matches(Regex("\\d+"))
    }
}
