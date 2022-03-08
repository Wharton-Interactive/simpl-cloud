<script>
  import { createEventDispatcher } from "svelte";
  import { formatSession } from "./utils";

  export let showAutoBalance;
  export let unassigned;
  export let teams;
  export let inactive;
  export let currentSession;
  export let allowCreate = true;
  export let downloadPlayersUrl;

  const dispatch = createEventDispatcher();
</script>

<ul class="pill-list is-horizontal">
  <li class="pill-item">
    <span class="pill-var">{unassigned}</span>
    <span class="pill-label">Unassigned Player{unassigned != 1 ? "s" : ""}</span
    >
  </li>
  <li class="pill-item">
    <span class="pill-var">{teams.length}</span>
    <span class="pill-label"
      ><a href="#teams">Team{teams.length != 1 ? "s" : ""}</a></span
    >
  </li>
  <li class="pill-item">
    <span class="pill-var">{inactive}</span>
    <span class="pill-label">
      {#if inactive}
        <a href="#inactive-players">Inactive Player{inactive != 1 ? "s" : ""}</a
        >
      {:else}
        Inactive Players
      {/if}
    </span>
  </li>
</ul>

<div class="team-status-box well">
  {#if teams.length}
    {#if downloadPlayersUrl}
      <a href={downloadPlayersUrl} class="button no-border download-button">Download CSV</a>
    {/if}
    <ul class="pill-list is-large">
      {#each teams as team (team.internalId || team.id)}
        <li class="pill-item">
          <span class="pill-var">{team.players.length}</span>
          <span class="pill-label"
            ><a
              href="#{team.internalId || team.id}"
              on:click={() => {
                if (team.session && currentSession)
                  currentSession = team.session;
              }}>{team.name}</a
            >
            {#if team.session}<small>
                ({formatSession(team.session)})</small
              >{/if}</span
          >
        </li>
      {/each}
    </ul>
  {/if}

  <div class="button-wrap" style="padding-bottom: 0;">
    {#if allowCreate}
      <button class="button" on:click={() => dispatch("clickCreateTeam")}>
        <svg
          class="icon"
          style="margin-left: -8px;"
          viewBox="0 0 17.928 22.481"
          id="people"
          xmlns="http://www.w3.org/2000/svg"
          ><g fill="currentColor"
            ><path
              d="M16.731 7.152h-1.274a.59.59 0 00-.581.689.939.939 0 01.028.104v.003a2.487 2.487 0 01.068.707l-.514 5.696-.008.087a.331.331 0 01-.004.033l-.008.062a2.055 2.055 0 01-1.402 1.64l-.032.01a.589.589 0 00-.389.468c-.002 0-.002 0 0 0l-.008.088v.001l-.254 3.178-.004.036v.029c0 .326.264.59.59.59h1.791a.774.774 0 00.762-.637l.012-.15.416-5.191a.515.515 0 01.483-.502l.033-.001.033.001h.231v-.001a.776.776 0 00.766-.657v-.009l.008-.077.451-5a1.192 1.192 0 00-1.194-1.197zm-3.802-1.13a2.62 2.62 0 00.78.118A2.647 2.647 0 1013.42.862a.589.589 0 00-.454.811 4.179 4.179 0 01-.349 3.45l-.002.005-.033.056a.59.59 0 00.347.838z"
            /><path
              d="M12.402 15.095a.884.884 0 00.873-.749v-.01l.008-.087.514-5.699c0-.753-.609-1.363-1.362-1.363H5.547c-.753 0-1.363.61-1.363 1.363l.51 5.656.016.17a.884.884 0 00.867.719v.001h.268l.037-.001.039.001a.591.591 0 01.551.581l.474 5.928.011.133a.883.883 0 00.871.744h2.331a.883.883 0 00.868-.727l.014-.17.473-5.918c0-.02.002-.038.004-.057a.594.594 0 01.548-.515l.038-.001.037.001h.261zM8.99 6.032a3.013 3.013 0 003.018-3.016A3.016 3.016 0 108.99 6.032z"
            /><path
              d="M5.625 19.913l-.252-3.173v-.001l-.008-.088v-.001a.59.59 0 00-.435-.482h-.003a2.066 2.066 0 01-1.393-1.686l-.016-.171-.508-5.656a.924.924 0 01-.006-.105c0-.207.025-.406.072-.599.008-.039.02-.077.03-.115a.59.59 0 00-.582-.684H1.25c-.66 0-1.195.535-1.195 1.196l.447 4.964.013.149c.067.358.383.63.762.63v.001h.233l.034-.001.033.001a.519.519 0 01.485.509l.415 5.201.01.117a.776.776 0 00.765.652h1.79a.59.59 0 00.59-.59l-.001-.02-.006-.048zM4.272 6.14a2.652 2.652 0 00.78-.117l.006-.002a.59.59 0 00.342-.835l-.033-.057-.003-.005a4.173 4.173 0 01-.348-3.45v-.003l.022-.063a.589.589 0 00-.477-.746C4.556.86 4.55.86 4.543.859a2.296 2.296 0 00-.271-.014 2.648 2.648 0 000 5.295z"
            /></g
          ></svg
        >
        Create New Team
      </button>

      {#if showAutoBalance}
        <button class="button" on:click={() => dispatch("openAutoBalance")}>
          <svg
            class="icon"
            style="margin-left: -8px;"
            viewBox="0 0 17.928 22.481"
            id="people"
            xmlns="http://www.w3.org/2000/svg"
            ><g fill="currentColor"
              ><path
                d="M16.731 7.152h-1.274a.59.59 0 00-.581.689.939.939 0 01.028.104v.003a2.487 2.487 0 01.068.707l-.514 5.696-.008.087a.331.331 0 01-.004.033l-.008.062a2.055 2.055 0 01-1.402 1.64l-.032.01a.589.589 0 00-.389.468c-.002 0-.002 0 0 0l-.008.088v.001l-.254 3.178-.004.036v.029c0 .326.264.59.59.59h1.791a.774.774 0 00.762-.637l.012-.15.416-5.191a.515.515 0 01.483-.502l.033-.001.033.001h.231v-.001a.776.776 0 00.766-.657v-.009l.008-.077.451-5a1.192 1.192 0 00-1.194-1.197zm-3.802-1.13a2.62 2.62 0 00.78.118A2.647 2.647 0 1013.42.862a.589.589 0 00-.454.811 4.179 4.179 0 01-.349 3.45l-.002.005-.033.056a.59.59 0 00.347.838z"
              /><path
                d="M12.402 15.095a.884.884 0 00.873-.749v-.01l.008-.087.514-5.699c0-.753-.609-1.363-1.362-1.363H5.547c-.753 0-1.363.61-1.363 1.363l.51 5.656.016.17a.884.884 0 00.867.719v.001h.268l.037-.001.039.001a.591.591 0 01.551.581l.474 5.928.011.133a.883.883 0 00.871.744h2.331a.883.883 0 00.868-.727l.014-.17.473-5.918c0-.02.002-.038.004-.057a.594.594 0 01.548-.515l.038-.001.037.001h.261zM8.99 6.032a3.013 3.013 0 003.018-3.016A3.016 3.016 0 108.99 6.032z"
              /><path
                d="M5.625 19.913l-.252-3.173v-.001l-.008-.088v-.001a.59.59 0 00-.435-.482h-.003a2.066 2.066 0 01-1.393-1.686l-.016-.171-.508-5.656a.924.924 0 01-.006-.105c0-.207.025-.406.072-.599.008-.039.02-.077.03-.115a.59.59 0 00-.582-.684H1.25c-.66 0-1.195.535-1.195 1.196l.447 4.964.013.149c.067.358.383.63.762.63v.001h.233l.034-.001.033.001a.519.519 0 01.485.509l.415 5.201.01.117a.776.776 0 00.765.652h1.79a.59.59 0 00.59-.59l-.001-.02-.006-.048zM4.272 6.14a2.652 2.652 0 00.78-.117l.006-.002a.59.59 0 00.342-.835l-.033-.057-.003-.005a4.173 4.173 0 01-.348-3.45v-.003l.022-.063a.589.589 0 00-.477-.746C4.556.86 4.55.86 4.543.859a2.296 2.296 0 00-.271-.014 2.648 2.648 0 000 5.295z"
              /></g
            ></svg
          >
          Auto-assign 10 players to teams
        </button>
      {/if}
    {/if}
  </div>

  {#if !teams.length}
    <h3 class="card-heading text-center">Create your first team</h3>
    <p class="text-center">
      Teams may be created manually now. Alternatively once players arrive, you
      may randomly distribute players into teams.
    </p>
  {/if}
</div>
