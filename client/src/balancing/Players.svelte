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
    {#if inactive}
      <span class="has-dropdown tooltip-dropdown align-right">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 0C3.58214 0 0 3.58145 0 8C0 12.4186 3.58214 16 8 16C12.4179 16 16 12.4186 16 8C16 3.58145 12.4186 0 8 0ZM9.76368 11.3255L9.72831 11.3581C8.58674 12.4088 7.40564 12.8194 6.92779 12.8194C6.41248 12.8194 6.0345 12.5011 6.39514 11.1022L6.98674 8.62141C7.09007 8.22471 7.10672 8.06381 6.98674 8.06381C6.86814 8.06381 6.44855 8.22471 6.08028 8.42375C6.05564 8.43625 6.03135 8.44943 6.00746 8.46329C5.94653 8.48463 5.88004 8.48389 5.8196 8.46119C5.75917 8.43848 5.70863 8.39527 5.67682 8.33909C5.64502 8.28291 5.63396 8.21734 5.64559 8.15384C5.65722 8.09034 5.69079 8.03294 5.74044 7.99168L5.75085 7.98266C6.94443 7.03945 8.2469 6.49085 8.82531 6.49085C9.33992 6.49085 9.42592 7.11157 9.16931 8.06519L8.49103 10.675C8.37105 11.1355 8.42237 11.2943 8.54235 11.2943C8.66303 11.2943 8.9987 11.1778 9.37737 10.9365H9.37807L9.44603 10.8921C9.48794 10.8731 9.53395 10.8649 9.57985 10.8682C9.62574 10.8716 9.67007 10.8864 9.70877 10.9113C9.74747 10.9362 9.77931 10.9704 9.80138 11.0108C9.82345 11.0511 9.83505 11.0964 9.83511 11.1424C9.83551 11.2103 9.80996 11.2758 9.76368 11.3255ZM8.61101 5.2515C7.99237 5.2515 7.63173 4.886 7.64907 4.28192C7.64907 3.77356 8.07837 3.07447 8.93697 3.07447C9.5889 3.07447 9.91487 3.52042 9.91487 4.02809C9.91625 4.66407 9.34963 5.2515 8.61101 5.2515Z" fill="#2E373F" fill-opacity="0.6"></path></svg>
        <div class="dropdown">
          Inactive players will not be able to participate or follow along once the game is set to play.
        </div>
      </span>
    {/if}
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
