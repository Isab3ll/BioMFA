import { error } from '@sveltejs/kit';

export async function load({params}) {
    const res = await fetch('http://localhost:20646/is_logged', {
            method: 'POST',
            body: JSON.stringify({"session_id": params.session_id}),
            headers: {
                'Content-Type': 'application/json'
            }
      });

    const json = await res.json();
    if (json.is_logged == false) {
        throw error(401);
    }
}
