import { redirect } from '@sveltejs/kit';

export async function load({params}) {
    const res = await fetch('http://127.0.0.1:20646/logout', {
            method: 'POST',
            body: JSON.stringify({"session_id": params.session_id}),
            headers: {
                'Content-Type': 'application/json'
            }
      });
    redirect(303, '/');
}
