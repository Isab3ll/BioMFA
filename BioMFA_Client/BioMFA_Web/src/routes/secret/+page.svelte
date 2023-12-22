<script>
	import { goto } from '$app/navigation';

	export let data;
    const username = data.username;

	function logout() {
		goto('/logout');
	}
</script>

<style>
    .main {
        text-align: center;
        background-color: white;
        padding: 50px;
        border-radius: 10px;
        height: 350px;
    }

    .logo {
        max-width: 200px;
        width: 60%;
        height: auto;
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
</style>

<main class="main">
    <h1>BioMFA<br>Secret page</h1>
    <img src="/biomfa_logo.png" alt="BioMFA Logo" class="logo" />

    <br><br>

    <p>Welcome, <b>{username}</b>!</p>

	<!-- <p>You successfully logged in to the secret page.</p> -->

    <div class="button-container">
        <button on:click={() => logout()}>Logout</button>
    </div>
</main>
