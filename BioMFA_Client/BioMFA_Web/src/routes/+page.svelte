<script>
	import { onMount } from 'svelte';
	import Hashes from 'jshashes';
	import { goto } from '$app/navigation';

	let socket;
	onMount(() => {
		socket = new WebSocket(`ws://frog01.mikr.us:30646`);
		socket.addEventListener('message', (event) => {
			const session = JSON.parse(event.data);
			content = session.content;
			if (session.action == 'SESSION') {
				session_id = session.content.session_id;
				goto('/login/' + session_id + '/' + username);
			}
			if (session.content.operation_id) {
				block_input = true;
			} else if (!session.content.operation_id) {
				block_input = false;
			}
		});
		socket.addEventListener('close', (_event) => {
			console.log('Socket closed');
		});
	});

	const SHA512 = new Hashes.SHA512();

	let username = '';
	let password = '';
	let session_id;
	let content;
	let block_input = false;

	function login() {
		let hashed_password = SHA512.hex(password);
		let message = { action: 'LOGIN', content: { username: username, password: hashed_password } };
		socket.send(JSON.stringify(message));
	}

	function register() {
		let hashed_password = SHA512.hex(password);
		let message = {
			action: 'REGISTER',
			content: { username: username, password: hashed_password }
		};
		socket.send(JSON.stringify(message));
	}
</script>

<style>
	.main {
		text-align: center;
		background-color: white;
		padding: 50px;
		border-radius: 10px;
		height: 380px;
	}

	.logo {
		max-width: 200px;
		width: 60%;
		height: auto;
	}

	input {
		margin-top: 10px;
		display: block;
		width: 100%;
		height: 7%;
		margin-left: auto;
		margin-right: auto;
		padding: 10px;
		border: 1px solid #363636;
		border-radius: 5px;
	}

	button {
		margin-top: 10px;
		background-color: #363636;
		color: white;
		padding: 10px;
		cursor: pointer;
		border: none;
		border-radius: 5px;
		flex: 1;
	}

	.button-container {
		display: flex;
		justify-content: space-between;
		width: 100%;
		margin: 0 auto;
		margin-top: 10px;
	}

	.button-container button {
		margin-right: 5px;
	}
</style>

<main class="main">
	<h1>BioMFA Web</h1>
	<img src="/biomfa_logo.png" alt="BioMFA Logo" class="logo" />

    <br><br>

	<input bind:value={username} placeholder="Username" disabled={block_input} />
	<input type="password" bind:value={password} placeholder="Password" disabled={block_input} />

	<div class="button-container">
		<button on:click={() => login()}>Login</button>
		<button on:click={() => register()}>Register</button>
	</div>

	{#if content}
		{#if content.operation_id}
			<p>Operation ID: {content.operation_id}</p>
		{:else if content.session_id}
			<p>Session ID: {content.session_id}</p>
		{:else}
			<p>{content}</p>
		{/if}
	{/if}
</main>
