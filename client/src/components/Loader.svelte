<script>
  export let loaded;
  export let saving = false;
  export let listening = null;
</script>

{#if !loaded}
  <p class="progress-loader">Loading...</p>
{:else if saving}
  <p class="progress-loader">Saving...</p>
{:else if listening !== null}
  {#if listening}
    <p class="progress-loader listening">Connected</p>
  {:else}
    <p class="progress-loader disconnected">Disconnected</p>
  {/if}
{/if}

<style>
  .progress-loader {
    position: absolute;
    right: 0;
    background: grey;
    color: #fff;
    letter-spacing: 1px;
    font-size: 0.7em;
    padding: 0.2em 0.7em;
    margin: 0 1em 0 0;
    border-radius: 0.3em;
  }
  .progress-loader.listening {
    background: darkgreen;
    opacity: 0.4;
  }
  .progress-loader.disconnected {
    background: darkred;
  }
</style>
