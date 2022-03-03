<script>
  import { flip } from "svelte/animate";
  import Player from "../components/Player.svelte";
  import { receive, send } from "./crossfade";

  export let selected;
  export let unassigned;
  export let allInactive;
  export let nextStep = null;
  export let unassignedIsError = false;
  export let inactive = false;
  
  $: players = inactive ? allInactive : unassigned.filter((p) => !p.inactive);
  $: if (!allInactive.length) inactive = false;
</script>

  <div class="player-header">
    <p
      class="walkthrough-chapter-heading"
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
    {#if !inactive}
      <div
        class="card player-card glow-shadow tab-pane"
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
            />
          </div>
        {/each}
      </div>
    {/if}
    {#if !players.length}
      <div class="all-players-managed">
        <h3 class="card-heading text-center">There are no players registered.</h3>
        <p class="text-center">Once players have accepted their invitation from the marketplace, they will appear in this list.</p>
        <p class="text-center">All unassigned players must either be assigned to teams or made inactive before the run may begin.</p>


         <p><em>TODO: If zero unassigned players AND there is at least one player assigned to a team, print this:</em></p>
         <svg
         xmlns="http://www.w3.org/2000/svg"
         viewBox="0 0 23.043 17.154"
         class="icon"
         ><path
           fill="currentColor"
           d="M22.501.542a1.852 1.852 0 00-2.526-.086l-.178.179-7.551 7.554-3.383 3.384c-.019.021-.038.043-.059.063l-.063.058-.007.006-.008.006a1.022 1.022 0 01-1.325-.027l-.009-.008a1.19 1.19 0 01-.073-.073l-.007-.009-3.404-3.403-.737-.738a1.855 1.855 0 00-2.627 0 1.852 1.852 0 00-.042 2.58l.087.088 6.7 6.7.056.057.019.018c.383.344.962.352 1.351.021l.12-.121 1.84-1.839-.001-.001.535-.534 4.7-4.699.042-.045.046-.042.678-.68.006.005L22.347 3.3l.291-.292a1.852 1.852 0 00-.137-2.466z"
         /></svg
       >
         <p>
           {#if nextStep !== false}
             All players are assigned to teams and ready to play. You may now
             enable Players Prepare and Start Game in
             <strong
               >{#if nextStep}<a href={nextStep}>Game Status</a>{:else}Game
                 Status{/if}</strong
             >.
           {:else}
             All players are assigned for this session group.
           {/if}
         </p>
         <!-- /above conditional-->
      </div>
    {/if}