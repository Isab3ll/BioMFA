import { redirect } from '@sveltejs/kit';

export async function load({ cookies }) {
	const res = await fetch('http://127.0.0.1:20646/logout', {
		method: 'POST',
		body: JSON.stringify({
			session_id: cookies.get('session_id', { path: '/' }),
			username: cookies.get('username', { path: '/' })
		}),
		headers: {
			'Content-Type': 'application/json'
		}
	});

	cookies.delete('session_id', { path: '/' });
	cookies.delete('username', { path: '/' });
	redirect(303, '/');
}
