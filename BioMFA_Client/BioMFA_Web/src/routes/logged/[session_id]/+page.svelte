<script>
    import { goto } from '$app/navigation';
    
    let session_id = window.location.pathname.split("/")[2];
    
    function logout() {
        goto("/logout/" + session_id);
    }
</script>

<h1>Secret content</h1>

<button on:click={() => logout()}>Logout</button>
