<script>
  import { flip } from "svelte/animate";
  import Player from "../components/Player.svelte";
  import { receive, send } from "./crossfade";

  export let selected;
  export let players;
  export let unassignedIsError = false;
  export let inactive = false;
</script>

<div class="player-header" class:pad-top={inactive}>
  <p
    class="walkthrough-chapter-heading"
    id={inactive ? "inactive-players" : "unassigned-players"}
    class:note={!inactive && players.length && unassignedIsError}
    class:theme-alert-color={!inactive && players.length && unassignedIsError}
  >
    {#if !inactive}
      Unassigned Players
    {:else}
      Inactive Players
    {/if}
    ({players.length})
  </p>
</div>
  <div
    class="card player-card tab-pane"
    class:glow-shadow={!inactive}
    class:is-inactive-player={inactive}
    role="tabpanel"
    aria-labelledby="tabby-toggle_active"
  >
    {#each players as player (player.id)}
      <div
        animate:flip
        out:send|local={{ key: player.id }}
        in:receive|local={{ key: player.id }}
      >
        <Player
          isSelected={selected.includes(player.id)}
          {player}
          on:selectPlayer
          on:addPlayers
        />
      </div>
    {/each}
  </div>
