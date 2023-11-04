package mobile.biomfa

import android.annotation.SuppressLint
import android.content.Intent
import android.nfc.NfcAdapter
import android.nfc.Tag
import android.nfc.tech.MifareClassic
import android.nfc.tech.MifareUltralight
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.neovisionaries.ws.client.*
import com.neovisionaries.ws.client.WebSocket
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.internal.ws.RealWebSocket
import java.io.IOException

class ScanImplantActivity : AppCompatActivity() {

    private var nfcAdapter: NfcAdapter? = null
    private val nfcCallback = NfcAdapter.ReaderCallback { tag -> readTagData(tag) }

    private val ULTRALIGHT_PAGE_INDEX = 0
    private val CLASSIC_BLOCK_INDEX = 0
    private val CLASSIC_SECTOR_INDEX = 0
    private val CLASSIC_DEFAULT_KEY = byteArrayOf(
        0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte(), 0xFF.toByte(),
        0xFF.toByte(), 0xFF.toByte()
    )

    private lateinit var dataTextView: TextView
    private lateinit var nextButton: Button

    @SuppressLint("MissingInflatedId")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_scan_implant)
        nfcAdapter = NfcAdapter.getDefaultAdapter(this)
        dataTextView = findViewById(R.id.data_textview)
        nextButton = findViewById(R.id.next_button)
        nextButton.visibility = View.INVISIBLE

        nextButton.setOnClickListener {
            val code = intent.getStringExtra("code")
            val mfa = dataTextView.text.toString()
            sendDataToServer(code, mfa)
        }
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
            runOnUiThread {
                Toast.makeText(applicationContext, "Tag type not supported.", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun readMifareClassicData(tag: Tag) {
        val mifare = MifareClassic.get(tag)

        try {
            mifare?.connect()
            if (mifare?.authenticateSectorWithKeyA(CLASSIC_SECTOR_INDEX, CLASSIC_DEFAULT_KEY) == true) {
                val blockData = mifare.readBlock(CLASSIC_BLOCK_INDEX)
                val dataAsString = blockData.toHexString()
                runOnUiThread {
                    dataTextView.text = dataAsString
                    nextButton.visibility = View.VISIBLE
                }
            } else {
                runOnUiThread {
                    Toast.makeText(applicationContext, "Authentication failed.", Toast.LENGTH_LONG).show()
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
            runOnUiThread {
                Toast.makeText(applicationContext, "Error reading MIFARE Classic data.", Toast.LENGTH_LONG).show()
            }
        } finally {
            mifare?.close()
        }
    }

    private fun readMifareUltralightData(tag: Tag) {
        val ultralight = MifareUltralight.get(tag)

        try {
            ultralight?.connect()

            val pageData = ultralight?.readPages(ULTRALIGHT_PAGE_INDEX)
            if (pageData != null) {
                val dataAsString = pageData.toHexString()
                runOnUiThread {
                    dataTextView.text = dataAsString
                    nextButton.visibility = View.VISIBLE
                }
            } else {
                runOnUiThread {
                    Toast.makeText(applicationContext, "No data found.", Toast.LENGTH_LONG).show()
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
            runOnUiThread {
                Toast.makeText(applicationContext, "Error reading MIFARE Ultralight data.", Toast.LENGTH_LONG).show()
            }
        } finally {
            ultralight?.close()
        }
    }

    private fun ByteArray.toHexString(): String {
        return joinToString("") { "%02x".format(it) }
    }

    private fun sendDataToServer(code: String?, mfa: String) {
        val url = "ws://frog01.mikr.us:30646"
        val json = """{"action": "MFA", "content": {"operation_id": "$code", "mfa_id": "$mfa"}}"""

        GlobalScope.launch(Dispatchers.IO) {
            val websocket = WebSocketFactory().createSocket(url)
            websocket.addListener(object : WebSocketAdapter() {
                override fun onTextMessage(websocket: WebSocket?, text: String?) {
                    super.onTextMessage(websocket, text)
                }

                override fun onError(websocket: WebSocket?, cause: WebSocketException?) {
                    super.onError(websocket, cause)
                    runOnUiThread {
                        Toast.makeText(applicationContext, "Server not found", Toast.LENGTH_LONG).show()
                    }
                }

            })

            websocket.connect()
            websocket.sendText(json)
            websocket.disconnect()
            runOnUiThread {
                Toast.makeText(applicationContext, "Authentication successful", Toast.LENGTH_LONG).show()
                goToMainActivity()
            }
        }

    }

    private fun goToMainActivity() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
    }
}