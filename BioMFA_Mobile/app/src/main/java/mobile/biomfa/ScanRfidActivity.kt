package mobile.biomfa

import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.MifareClassic
import android.nfc.tech.MifareUltralight
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class ScanRfidActivity : AppCompatActivity() {

    private var nfcAdapter: NfcAdapter? = null
    private val nfcCallback = NfcAdapter.ReaderCallback { tag -> readTagData(tag) }

    private val CLASSIC_SECTOR_INDEX = 0
    private val CLASSIC_DEFAULT_KEY = byteArrayOf(
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

    private fun readTagData(tag: Tag) {
        val techList = tag.techList

        if (techList.contains("android.nfc.tech.MifareClassic")) {
            readMifareClassicData(tag)
        } else if (techList.contains("android.nfc.tech.MifareUltralight")) {
            readMifareUltralightData(tag)
        } else {
            Toast.makeText(applicationContext, "Tag type not supported", Toast.LENGTH_LONG).show()
        }
    }

    private fun readMifareClassicData(tag: Tag) {
        val mifare = MifareClassic.get(tag)

        try {
            mifare?.connect()
            if (mifare?.authenticateSectorWithKeyA(CLASSIC_SECTOR_INDEX, CLASSIC_DEFAULT_KEY) == true) {
                val uid = tag.id.toHexString()
                val showDataIntent = Intent(this, ShowDataActivity::class.java).apply {
                    putExtra(ShowDataActivity.EXTRA_SCANNED_DATA, uid)
                    putExtra(ShowDataActivity.EXTRA_TAG_TYPE, "MIFARE Classic")
                }
                startActivity(showDataIntent)
            } else {
                runOnUiThread {
                    Toast.makeText(applicationContext, "Sector authentication failed", Toast.LENGTH_LONG).show()
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
            runOnUiThread {
                Toast.makeText(applicationContext, "Error reading MIFARE Classic data", Toast.LENGTH_LONG).show()
            }
        } finally {
            mifare?.close()
        }
    }

    private fun readMifareUltralightData(tag: Tag) {
        val ultralight = MifareUltralight.get(tag)

        try {
            ultralight?.connect()
            val uid = tag.id.toHexString()
            val showDataIntent = Intent(this, ShowDataActivity::class.java).apply {
                putExtra(ShowDataActivity.EXTRA_SCANNED_DATA, uid)
                putExtra(ShowDataActivity.EXTRA_TAG_TYPE, "MIFARE Ultralight")
            }
            startActivity(showDataIntent)
        } catch (e: Exception) {
            e.printStackTrace()
            runOnUiThread {
                Toast.makeText(applicationContext, "Error reading MIFARE Ultralight data", Toast.LENGTH_LONG).show()
            }
        } finally {
            ultralight?.close()
        }
    }


    private fun ByteArray.toHexString(): String {
        return joinToString("") { "%02x".format(it) }
    }
}
