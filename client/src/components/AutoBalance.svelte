<script>
  import { createEventDispatcher } from "svelte";

  import Modal from "../components/Modal.svelte";

  let fillCount = 3;

  export let open;
  export let unassigned;
  const dispatch = createEventDispatcher();
</script>

<Modal bind:open={open}>
  <div class="text-center">
    <form
      on:submit|preventDefault={() => {
        dispatch("submit", { fillCount });
        open = false;
      }}
    >
      <h2 class="modal-heading">Auto Assign</h2>
      <p>
        Fill or create teams of up to <input
          class="auto-assign-input"
          type="number"
          min="1"
          bind:value={fillCount}
        />
        players
      </p>
      <div class="button-wrap align-center">
        <button class="button">Assign {unassigned.length} Players</button>
      </div>
    </form>
  </div>
</Modal>
