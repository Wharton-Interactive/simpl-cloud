<script>
  import { createEventDispatcher } from "svelte";
  import { alterPlayer } from "../balancing/stores";
  import { stringToColour } from "../balancing/utils";

  export let isSelected = false;
  export let player;

  export let readOnly = false;
  export let assigned = false;

  const dispatch = createEventDispatcher();

  const initials = player.name
    .replace(/(\w)[^ ]+/g, "$1")
    .replace(/[^\w]/g, "");
  var letters = initials[0] + initials[initials.length - 1];
</script>

<div
  class="player-item"
  class:is-selected={isSelected}
  aria-readonly={readOnly}
  on:click={() => {
    if (!readOnly) dispatch("selectPlayer", { id: player.id });
  }}
>
  <div class="avatar-detail">
    <div class="avatar" style="background: {stringToColour(player.name)};">
      <div class="avatar-inner">{letters}</div>
    </div>
    <p class="avatar-detail-meta">
      {player.name}
      <span class="avatar-detail-desc">
        {#if player.email}{player.email}
        {:else}<em>No email</em>
        {/if}
      </span>
    </p>
    <!-- <p>{#if player.ready}Ready{:else}Not Ready{/if}</p> -->
  </div>

  {#if !assigned || !readOnly}
    <div class="has-dropdown narrow-dropdown">
      <a
        href="."
        on:click|preventDefault|stopPropagation
        class="dropdown-button settings-button"
      >
        <svg
          class="icon"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
        >
          <path
            fill="var(--text-color)"
            d="M14.25 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 0114.25 12zM6.75 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 016.75 12zM21.75 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 0121.75 12z"
          />
        </svg>
      </a>
      <div class="dropdown">
        <ul class="dropdown-list">
          {#if assigned}
            <li class="dropdown-item">
              <a
                class="dropdown-link"
                href="."
                on:click|preventDefault|stopPropagation={() => {
                  dispatch("unassignPlayer", { id: player.id });
                }}>Unassign</a
              >
            </li>
          {:else if readOnly}
            <li class="dropdown-item">
              <a
                class="dropdown-link"
                href="."
                on:click|preventDefault|stopPropagation={() => {
                  alterPlayer.notify({ playerId: player.id, active: true });
                }}>Mark active</a
              >
            </li>
          {/if}
          {#if !player.inactive}
            <li class="dropdown-item">
              <a
                class="dropdown-link"
                href="."
                on:click|preventDefault|stopPropagation={() => {
                  alterPlayer.notify({ playerId: player.id, active: false });
                  if (isSelected) dispatch("selectPlayer", { id: player.id });
                  if (assigned) dispatch("unassignPlayer", { id: player.id });
                }}>Mark inactive</a
              >
            </li>
          {/if}
        </ul>
      </div>
    </div>
    <input class="show-for-sr-only" type="checkbox" checked={isSelected} />
  {/if}
</div>

<style>
  .player-item:hover input {
    transform: scale(1.1);
  }
</style>
