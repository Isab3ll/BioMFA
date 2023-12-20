<script>
    import { onMount } from 'svelte';
    import Hashes from 'jshashes';
    import { goto } from '$app/navigation';

    let socket;
    onMount(() => {
        socket = new WebSocket(
            `ws://frog01.mikr.us:30646`
        );
        socket.addEventListener('message', (event) => {
            const session = JSON.parse(event.data);
            content = session.content;
            // console.log('Message from server:', session);
            if (session.action == "SESSION") {
                session_id = session.content.session_id;
                // console.log('Session ID: ', session_id);
                goto("/logged/" + session_id);
            }
        });
        socket.addEventListener('close', (_event) => {
            console.log('Socket closed');
        });
    });

    const SHA512 = new Hashes.SHA512;

    let username = "";
    let password = "";
    let session_id;
    let content;

    function login() {
        let hashed_password = SHA512.hex(password);
        let message = {"action": "LOGIN", "content": {"username": username, "password": hashed_password}}
        socket.send(JSON.stringify(message));
    }

    function register() {
        let hashed_password = SHA512.hex(password);
        let message = {"action": "REGISTER", "content": {"username": username, "password": hashed_password}}
        socket.send(JSON.stringify(message));
    }
</script>

<h1>BioMFA Web</h1>

<h2>Home</h2>
<p>Welcome to BioMFA Web!</p>

<input bind:value={username} placeholder="Username" />
<input type="password" bind:value={password} placeholder="Password" />

<button on:click={() => login()}>Login</button>
<button on:click={() => register()}>Register</button>

{#if content}
    {#if content.operation_id}
        <p>content.operation_id: {content.operation_id}</p>
    {:else if content.session_id}
        <p>content.session_id: {content.session_id}</p>
    {:else}
        <p>content: {content}</p>
    {/if}
{/if}