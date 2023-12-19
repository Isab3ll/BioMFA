import { redirect } from '@sveltejs/kit';
import { error } from '@sveltejs/kit';

export async function load() {
    const res = await fetch('http://127.0.0.1:8000/is_logged', {
            method: 'POST',
            // body: cos_tu_sie_wpisze,
            // headers: {
            //     'Content-Type': 'application/json'
            // }
      });

    const json = await res.json();

    if (json.is_logged == true) {
        throw error(401);
    }
}