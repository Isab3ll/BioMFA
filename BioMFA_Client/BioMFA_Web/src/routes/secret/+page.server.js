import { redirect } from '@sveltejs/kit';
import { error } from '@sveltejs/kit';

export async function load({ cookies }) {
	if (!cookies.get('session_id', { path: '/' }) || !cookies.get('username', { path: '/' })) {
		throw error(401);
	}

	const res = await fetch('http://127.0.0.1:20646/is_logged', {
		method: 'POST',
		body: JSON.stringify({
			session_id: cookies.get('session_id', { path: '/' }),
			username: cookies.get('username', { path: '/' })
		}),
		headers: {
			'Content-Type': 'application/json'
		}
	});

	const json = await res.json();
    
	if (json.is_logged == false) {
		throw error(401);
	}

    return {
        username: cookies.get('username', { path: '/' })
    };
}
