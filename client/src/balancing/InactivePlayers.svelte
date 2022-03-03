<script>
  import { flip } from "svelte/animate";
  import Player from "../components/Player.svelte";
  import { receive, send } from "./crossfade";

  export let selected;
  export let unassigned;
  export let allInactive;
  export let unassignedIsError = false;

  let inactive = true;
  $: players = inactive ? allInactive : unassigned.filter((p) => !p.inactive);
  $: if (!allInactive.length) inactive = false;
</script>

{#if inactive}
  <div class="player-header pad-top">
    <p
      id="inactive-players"
      class="walkthrough-chapter-heading"
      class:note={!inactive && players.length && unassignedIsError}
      class:theme-alert-color={!inactive && players.length && unassignedIsError}
    >
        Inactive Players
      ({allInactive.length})
    </p>
  </div>
  <div class="card player-card tab-pane is-inactive-player">
    {#each players as player (player.id)}
      <div
        animate:flip
        out:send|local={{ key: player.id }}
        in:receive|local={{ key: player.id }}
      >
        <Player
          isSelected={selected.includes(player.id)}
          readOnly
          {player}
          on:selectPlayer
        />
      </div>
    {/each}
  </div>

  {/if}