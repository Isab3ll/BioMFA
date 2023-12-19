<script>
    import { onMount } from 'svelte';
    import Hashes from 'jshashes';

    let socket;
    onMount(() => {
        socket = new WebSocket(
            `ws://frog01.mikr.us:30646`
        );
        socket.addEventListener('message', (event) => {
            console.log('Message from server ', event.data);
        });
        socket.addEventListener('close', (_event) => {
            console.log('Socket closed');
        });
    });

    const SHA512 = new Hashes.SHA512;

    let username = "";
    let password = "";

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

<input bind:value={username} placeholder="Usename" />
<input type="password" bind:value={password} placeholder="Password" />

<button on:click={() => login()}>Login</button>
<button on:click={() => register()}>Register</button>


<a href="/logged">Go to logged</a>


