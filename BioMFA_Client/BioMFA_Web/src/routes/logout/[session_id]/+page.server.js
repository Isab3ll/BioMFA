import { redirect } from '@sveltejs/kit';

export async function load({params}) {
    const res = await fetch('http://frog01.mikr.us:20646/logout', {
            method: 'POST',
            body: JSON.stringify({"session_id": params.session_id}),
            headers: {
                'Content-Type': 'application/json'
            }
      });
    redirect(303, '/');
}
