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
    <!-- <span>{#if team.ready}Ready{:else}Not Ready{/if}</span> -->
  </h2>
  {#if selectedElsewhere.length}
    <button
      class="button small hollow theme-tint animate-in"
      on:click={() => {
        dispatch("addPlayers");
      }}
      >Add {#if selectedElsewhere.length > 1}{selectedElsewhere.length} players{:else}player{/if}
    </button>
  {/if}
  <p class="player-card-summary">
    {team.players.length || "No"} Players
  </p>
  <div class="player-card-actions">
    <a class="button icon-button circle "
        href="."
        on:click|preventDefault={() => {
          editing = true;
        }}>
          <svg class="icon" viewBox="0 0 23.744 23.745" id="pencil" xmlns="http://www.w3.org/2000/svg"><path d="M23.323 2.883L20.861.422a1.44 1.44 0 00-2.036 0l-2.122 2.122a.64.64 0 000 .905l3.593 3.593c.25.25.655.25.905 0l2.122-2.122a1.441 1.441 0 000-2.037zm-7.39 1.336a.639.639 0 00-.905 0l-11.75 11.75a.639.639 0 000 .905l3.593 3.593c.25.25.655.25.905 0l11.75-11.75a.64.64 0 000-.905l-3.593-3.593zM2.597 17.732a.48.48 0 00-.775.138l-.032.095-1.746 5.099-.032.093a.48.48 0 00.576.576l.093-.033 5.099-1.746.095-.032a.48.48 0 00.138-.775l-3.416-3.415z" fill="currentColor"/></svg>
      </a>

      <a  class="button icon-button circle "
        href="."
        on:click|preventDefault={() => {
          dispatch("delete");
        }}>
        <svg class="icon" viewBox="0 0 15.679 21.169" id="trash" xmlns="http://www.w3.org/2000/svg"><path d="M15.67 4.446l-.057-.215-.409-1.545a.876.876 0 00-.692-.588l-.034-.005a51.6 51.6 0 00-3.453-.33l-.04.002a.638.638 0 01-.614-.46C10.234.993 9.978.311 9.663.184A1.438 1.438 0 009.448.12C9.39.11 9.331.103 9.272.095a10.745 10.745 0 00-2.867 0C6.348.103 6.288.11 6.23.12a1.225 1.225 0 00-.213.065C5.709.308 5.459.98 5.32 1.28a.634.634 0 01-.62.485c-.011 0-.021 0-.032-.002-1.146.071-2.28.18-3.404.325l-.142.018a.876.876 0 00-.648.581L.065 4.231l-.057.215a.904.904 0 00.874 1.027h13.915a.905.905 0 00.873-1.027zm-1.695 2.69H1.704a.906.906 0 00-.812.859l.02.232 1.005 12.18a.88.88 0 00.869.762h10.107c.44 0 .812-.326.869-.762l1.007-12.18.019-.232a.908.908 0 00-.813-.859z" fill="currentColor"/></svg>
      </a>
    </div>
</div>
<div transition:slide|local>
  {#if players.length == 0}
    <div class="card text-center">
      <p style="margin-top: 1rem;">
        Assign players to this team to get started.
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
