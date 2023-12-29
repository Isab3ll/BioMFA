import { error, redirect } from '@sveltejs/kit';

export async function load({ params, cookies }) {
	const res = await fetch('http://127.0.0.1:20646/is_logged', {
		method: 'POST',
		body: JSON.stringify({ session_id: params.session_id, username: params.username }),
		headers: {
			'Content-Type': 'application/json'
		}
	});

	const json = await res.json();
	if (json.is_logged == false) {
		throw error(401);
	}

	cookies.set('session_id', params.session_id, { path: '/', secure: true, maxage: 60 * 60});
	cookies.set('username', params.username, { path: '/' , secure: true, maxage: 60 * 60});
	redirect(303, '/secret');
}
