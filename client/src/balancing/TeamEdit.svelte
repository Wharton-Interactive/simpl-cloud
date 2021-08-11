<script>
  import dialogPolyfill from "dialog-polyfill";
  import { createEventDispatcher, onMount } from "svelte";

  export let team;

  export let open = false;

  const dispatch = createEventDispatcher();
  let teamName = team.name;

  function focus(el) {
    el.focus();
  }

  let dialogObj;
  onMount(() => {
    dialogPolyfill.registerDialog(dialogObj);
  });

  $: if (dialogObj) {
    if (open) {
      dialogObj.showModal();
    } else if (dialogObj?.open) {
      dialogObj.close();
    }
    document.body.classList.toggle("modal-is-open", open);
  }
</script>

<dialog class="modal large-pad" bind:this={dialogObj}>
  <button
    class="close-button"
    on:click={() => {
      open = false;
    }}
  >
    <svg
      class="icon"
      viewBox="0 0 16.59 16.59"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fill="currentColor"
        d="M11.38 7.75L16 3.14a1.86 1.86 0 00.25-2.38 1.79 1.79 0 00-2.74-.23L8.83 5.2a.76.76 0 01-1.08 0L3.14.6A1.86 1.86 0 00.76.33a1.79 1.79 0 00-.23 2.74L5.2 7.75a.76.76 0 010 1.08L.6 13.44a1.88 1.88 0 00-.27 2.39 1.81 1.81 0 002.74.23l4.68-4.68a.76.76 0 011.08 0L13.44 16a1.87 1.87 0 002.39.26 1.81 1.81 0 00.23-2.74l-4.68-4.69a.76.76 0 010-1.08z"
      />
    </svg>
  </button>
  <div class="scroll-wrap text-center">
    <form
      on:submit|preventDefault={() => {
        dispatch("rename", { name: teamName });
        open = false;
      }}
    >
      <h2 class="modal-heading">Rename Team</h2>
      <p>
        <input
          bind:value={teamName}
          use:focus
          on:keyup={(e) => {
            if (e.key === "Escape") dispatch("close");
          }}
        />
      </p>
      <div class="button-wrap align-center">
        <button class="button">Rename Team</button>
      </div>
    </form>
  </div>
</dialog>
