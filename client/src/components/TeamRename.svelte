<script>
  export let team;
  let editing = false;
  let value = "";

  function focus(el) {
    el.focus();
  }
</script>

{#if editing}
  <form
    on:submit|preventDefault={() => {
      team.name = value;
      editing = false;
    }}
  >
    <input
      bind:value
      on:keyup={(e) => {
        if (e.key === "Escape") {
          editing = false;
        }
      }}
      use:focus
    /><button>&check;</button><button
      type="button"
      on:click={() => {
        editing = false;
      }}>&cross;</button
    >
  </form>
{:else}
  <a
    href="."
    on:click|preventDefault={() => {
      value = team.name;
      editing = true;
    }}>{team.name}</a
  >
{/if}

<style>
  a {
    text-decoration: inherit;
    color: inherit;
  }
  a:hover::after,
  a:focus::after {
    content: " ✎edit";
    font-size: 0.9em;
    opacity: 0.6;
    cursor: text;
  }
</style>
