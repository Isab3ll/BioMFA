package mobile.biomfa

import android.content.Intent
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }

    fun openTypeCodeActivity(view: View) {
        val intent = Intent(this, TypeCodeActivity::class.java)
        startActivity(intent)
    }

    fun openInfoActivity(view: View) {
        val intent = Intent(this, InfoActivity::class.java)
        startActivity(intent)
    }

    fun openScanRfidActivity(view: View) {
        val intent = Intent(this, ScanRfidActivity::class.java)
        startActivity(intent)
    }

    fun openScanImplantActivity(view: View) {
        val intent = Intent(this, ScanImplantActivity::class.java)
        startActivity(intent)
    }

}

