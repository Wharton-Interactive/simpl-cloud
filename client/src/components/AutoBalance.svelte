<script>
  import { createEventDispatcher } from "svelte";
  import { data } from "../balancing/stores";
  import Modal from "../components/Modal.svelte";

  let fillCount;

  function setFillCount(min, max) {
    if (min && max) {
      fillCount = Math.floor((max + min) / 2);
    } else if (min) {
      fillCount = Math.max(min, 3);
    } else if (max) {
      fillCount = Math.min(max, 3);
    } else {
      fillCount = 3;
    }
  }

  // Set fillCount half way between minimum and maximum players if both are provided (or fall back to 3 if neither is provided).
  $: setFillCount($data.minimumPlayers, $data.maximumPlayers);

  export let open;
  export let unassigned;
  const dispatch = createEventDispatcher();
</script>

<Modal bind:open>
  <div class="text-center">
    <form
      on:submit|preventDefault={() => {
        dispatch("submit", { fillCount });
        open = false;
      }}
    >
      <h2 class="modal-heading">Auto Assign</h2>
      <p>
        Fill or create teams of up to {#if $data.minimumPlayers && $data.maximumPlayers && $data.minimumPlayers === $data.maximumPlayers}
          {fillCount}{:else}
          <input
            class="auto-assign-input"
            type="number"
            min={$data.minimumPlayers || 1}
            max={$data.maximumPlayers}
            step="1"
            bind:value={fillCount}
          />{/if}
        {fillCount == 1 ? "player" : "players"}
        {#if $data.minimumPlayers !== $data.maximumPlayers}
          {#if $data.minimumPlayers > 1 && $data.maximumPlayers}
            <em
              >(between {$data.minimumPlayers} and
              {$data.maximumPlayers})</em
            >
          {:else if $data.minimumPlayers > 1}
            <em>(at least {$data.minimumPlayers})</em>
          {:else if $data.maximumPlayers}
            <em>(at most {$data.maximumPlayers})</em>
          {/if}
        {/if}
      </p>
      <div class="button-wrap align-center">
        <button class="button">Assign {unassigned.length} Players</button>
      </div>
    </form>
  </div>
</Modal>
