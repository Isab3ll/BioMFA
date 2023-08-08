package mobile.biomfa

import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.MifareClassic
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class ScanRfidActivity : AppCompatActivity() {

    private var nfcAdapter: NfcAdapter? = null
    private val nfcCallback = NfcAdapter.ReaderCallback { tag -> readMifareData(tag) }

    private val BLOCK_INDEX = 4
    private val SECTOR_INDEX = 1
    private val DEFAULT_KEY = byteArrayOf(
        0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte(),
        0xFF.toByte(), 0xFF.toByte()
    )

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

    private fun readMifareData(tag: Tag) {
        val mifare = MifareClassic.get(tag)

        try {
            mifare?.connect()
            if (mifare?.authenticateSectorWithKeyA(SECTOR_INDEX, DEFAULT_KEY) == true) {
                val blockData = mifare.readBlock(BLOCK_INDEX)
                val dataAsString = blockData.toHexString()
                val showDataIntent = Intent(this, ShowDataActivity::class.java).apply {
                    putExtra(ShowDataActivity.EXTRA_SCANNED_DATA, dataAsString)
                    putExtra(ShowDataActivity.EXTRA_TAG_TYPE, "MIFARE Tag")
                }
                startActivity(showDataIntent)
            } else {
                runOnUiThread {
                    Toast.makeText(applicationContext, "Authentication failed.", Toast.LENGTH_LONG).show()
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
            runOnUiThread {
                Toast.makeText(applicationContext, "Error reading MIFARE data.", Toast.LENGTH_LONG).show()
            }
        } finally {
            mifare?.close()
        }
    }

    private fun ByteArray.toHexString(): String {
        return joinToString("") { "%02x".format(it) }
    }
}
