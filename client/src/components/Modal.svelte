<script>
  import { onMount } from "svelte";
  import dialogPolyfill from "dialog-polyfill";

  export let open = false;

  let dialogObj;
  onMount(() => {
    dialogPolyfill.registerDialog(dialogObj);
  });

  $: open ? dialogObj?.showModal() : dialogObj && dialogObj.open && dialogObj.close();
</script>

<dialog
  class="modal"
  bind:this={dialogObj}>
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
  <div class="scroll-wrap">
    <slot />
  </div>
</dialog>
