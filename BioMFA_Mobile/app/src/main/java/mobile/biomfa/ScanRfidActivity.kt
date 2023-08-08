package mobile.biomfa

import android.app.PendingIntent
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.Ndef
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class ScanRfidActivity : AppCompatActivity() {

    private var nfcAdapter: NfcAdapter? = null
    private val nfcCallback = NfcAdapter.ReaderCallback { tag -> readFromTag(tag) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_scan_rfid)

        val returnButton: Button = findViewById(R.id.return_button)
        returnButton.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#363636"))
        returnButton.setOnClickListener {
            finish()
        }

        nfcAdapter = NfcAdapter.getDefaultAdapter(this)
    }

    override fun onResume() {
        super.onResume()
        nfcAdapter?.enableReaderMode(this, nfcCallback, NfcAdapter.FLAG_READER_NFC_A or NfcAdapter.FLAG_READER_SKIP_NDEF_CHECK, null)
    }

    override fun onPause() {
        super.onPause()
        nfcAdapter?.disableReaderMode(this)
    }

    private fun readFromTag(tag: Tag) {
        val ndef = Ndef.get(tag)

        try {
            ndef?.connect()
            val ndefMessage = ndef?.ndefMessage
            if (ndefMessage != null) {
                val records = ndefMessage.records
                if (records.isNotEmpty()) {
                    val payload = records[0].payload
                    val text = String(payload, Charsets.UTF_8)

                    val showDataIntent = Intent(this, ShowDataActivity::class.java).apply {
                        putExtra(ShowDataActivity.EXTRA_SCANNED_DATA, text)
                        putExtra(ShowDataActivity.EXTRA_TAG_TYPE, "NFC")
                    }
                    startActivity(showDataIntent)
                }
            } else {
                runOnUiThread {
                    Toast.makeText(applicationContext, "No NDEF records found on the tag.", Toast.LENGTH_LONG).show()
                }
            }
            ndef?.close()
        } catch (e: Exception) {
            runOnUiThread {
                Toast.makeText(applicationContext, "Cannot Read From Tag.", Toast.LENGTH_LONG).show()
            }
        }
    }


}
