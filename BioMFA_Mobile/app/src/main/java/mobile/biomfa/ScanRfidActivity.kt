package mobile.biomfa

import android.os.Bundle
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import android.nfc.NfcAdapter

class ScanRfidActivity : AppCompatActivity() {

    private var nfcAdapter: NfcAdapter? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_scan_rfid)

        val returnButton: Button = findViewById(R.id.return_button)
        returnButton.setOnClickListener {
            finish()
        }
    }


}
