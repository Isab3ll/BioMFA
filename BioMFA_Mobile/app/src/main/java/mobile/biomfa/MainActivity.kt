package mobile.biomfa

import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Color
import android.os.Bundle
import android.view.View
import android.view.animation.Animation
import android.view.animation.AnimationUtils
import android.widget.Button
import android.widget.LinearLayout
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var menuLayout: LinearLayout
    private lateinit var toggleButton: Button
    private var isMenuOpen = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        menuLayout = findViewById(R.id.menu_layout)
        toggleButton = findViewById(R.id.toggle_button)
        toggleButton.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#363636"))

        hideMenu()

        toggleButton.setOnClickListener {
            toggleMenu()
        }
    }

    private fun toggleMenu() {
        if (isMenuOpen) {
            hideMenu()
        } else {
            showMenu()
        }
        isMenuOpen = !isMenuOpen
    }

    private fun showMenu() {
        val slideUpAnimation: Animation = AnimationUtils.loadAnimation(this, R.anim.slide_up)

        menuLayout.visibility = View.VISIBLE
        for (i in 0 until menuLayout.childCount) {
            val child: View = menuLayout.getChildAt(i)
            child.visibility = View.VISIBLE
            child.startAnimation(slideUpAnimation)
        }
        toggleButton.setCompoundDrawablesWithIntrinsicBounds(0, 0, 0, R.drawable.arrow_down)

        toggleButton.setOnClickListener {
            toggleMenu()
        }

        val infoButton: Button = findViewById(R.id.app_info)
        infoButton.setOnClickListener {
            val intent = Intent(this, InfoActivity::class.java)
            startActivity(intent)
        }
    }

    private fun hideMenu() {
        val slideDownAnimation: Animation = AnimationUtils.loadAnimation(this, R.anim.slide_down)

        for (i in 0 until menuLayout.childCount) {
            val child: View = menuLayout.getChildAt(i)
            child.startAnimation(slideDownAnimation)
            child.postDelayed({
                if (i != 0) {
                    child.visibility = View.GONE
                }
            },300)
        }
        toggleButton.setCompoundDrawablesWithIntrinsicBounds(0, 0, 0, R.drawable.arrow_up)
    }
}

