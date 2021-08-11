<script>
  import { createEventDispatcher } from "svelte";
  import { flip } from "svelte/animate";
  import { slide } from "svelte/transition";
  import Player from "../components/Player.svelte";
  import { receive, send } from "./crossfade";
  import TeamEdit from "./TeamEdit.svelte";

  export let team;
  export let players;
  export let selected = [];
  export let readOnly = false;
  let editing = false;
  const dispatch = createEventDispatcher();

  $: selectedElsewhere = selected.filter((id) => !team.players.includes(id));

</script>

<div class="player-item is-header">
  <h2
    class="player-card-heading"
    on:dblclick={() => {
      editing = true;
    }}
  >
    {team.name}
  </h2>
  {#if selectedElsewhere.length}
    <button
      class="button small hollow theme-tint"
      on:click={() => {
        dispatch("addPlayers");
      }}
      >Add {#if selectedElsewhere.length > 1}{selectedElsewhere.length} players{:else}player{/if}</button
    >
  {/if}
  <p class="player-card-summary">
    {team.players.length || "No"} Players
  </p>
  <div class="player-card-actions">
    <div class="has-dropdown narrow-dropdown">
      <a
        href="."
        on:click|preventDefault
        class="dropdown-button settings-button"
      >
        <svg
          class="icon"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
        >
          <path
            fill="var(--tint)"
            d="M14.25 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 0114.25 12zM6.75 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 016.75 12zM21.75 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 0121.75 12z"
          />
        </svg>
      </a>
      <div class="dropdown">
        <ul class="dropdown-list">
          <li class="dropdown-item">
            <a
              class="dropdown-link"
              href="."
              on:click|preventDefault={() => {
                editing = true;
              }}>Edit Team</a
            >
          </li>
          <li class="dropdown-item">
            <a
              class="dropdown-link"
              href="."
              on:click|preventDefault={() => {
                dispatch("delete");
              }}>Delete Team</a
            >
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>
<div transition:slide|local>
  {#if players.length == 0}
    <div class="card text-center">
      <p style="margin-top: 1rem;">
        Assign Players to this Team to get started.
      </p>
      <p>
        Click
        <svg
          class="icon icon-small"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          style="margin:0 8px -6px;"
        >
          <path
            fill="currentColor"
            d="M14.25 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 0114.25 12zM6.75 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 016.75 12zM21.75 12a2.25 2.25 0 11-4.501-.001A2.25 2.25 0 0121.75 12z"
          />
        </svg>
        to
        <a
          href="."
          on:click|preventDefault={() => {
            editing = true;
          }}>rename</a
        >
        or
        <a
          href="."
          on:click|preventDefault={() => {
            dispatch("delete");
          }}
        >
          delete</a
        >.
      </p>
    </div>
  {/if}
  {#each players as player (player?.id)}
    <div
      animate:flip
      in:receive|local={{ key: player.id }}
      out:send|local={{ key: player.id }}
    >
      <Player
        isSelected={selected.includes(player.id)}
        {player}
        assigned
        {readOnly}
        on:selectPlayer
        on:unassignPlayer
      />
    </div>
  {/each}
</div>

<TeamEdit
  {team}
  bind:open={editing}
  on:close={() => {
    editing = false;
  }}
  on:rename={(e) => {
    dispatch("rename", e.detail);
    editing = false;
  }}
/>
