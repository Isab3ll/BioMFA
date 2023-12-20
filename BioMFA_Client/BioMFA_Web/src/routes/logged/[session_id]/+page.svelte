<script>
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';
    
    let session_id = $page.url.pathname.split("/")[2];
    
    function logout() {
        goto("/logout/" + session_id);
    }
</script>

<h1>Secret content</h1>

<button on:click={() => logout()}>Logout</button>
