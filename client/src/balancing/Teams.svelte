<script>
  import { fade, slide } from "svelte/transition";
  import Team from "./Team.svelte";
  import Instructions from "./Instructions.svelte";
  import Modal from "../components/Modal.svelte";
  import { formatSession } from "./utils";

  export let data;
  export let currentSession = undefined;
  export let currentSessionSelected;
  export let selected;
  export let createTeam;
  export let showDialog;
  export let showAutoBalance;

  let showInstructionsDialog;

  $: readOnly = currentSession === null;
  $: teams = readOnly
    ? $data.teams
    : $data.teams.filter(
        (t) =>
          !t.session ||
          t.session === currentSession ||
          currentSession === undefined
      );
  let groupedTeams = new Map();
  $: {
    if (readOnly) {
      groupedTeams = new Map();
      $data.sessions.forEach((session) => groupedTeams.set(session, []));
      teams.forEach((team) => {
        if (!team.players.length) return;
        if (!groupedTeams.has(team.session)) {
          groupedTeams.set(team.session, []);
        }
        groupedTeams.get(team.session).push(team);
      });
    }
  }

  const addPlayers = (team, onlyUnassigned) => {
    let adding = currentSessionSelected;
    if (onlyUnassigned) {
      const assigned = teams.flatMap((t) => t.players);
      const selectedAssigned = currentSessionSelected.filter((id) =>
        assigned.includes(id)
      );
      adding = adding.filter((id) => !selectedAssigned.includes(id));
    }
    team.players = [
      ...team.players,
      ...adding.filter((id) => !team.players.includes(id)),
    ];
    for (const otherTeam of teams.filter((t) => t !== team)) {
      otherTeam.players = otherTeam.players.filter(
        (id) => !adding.includes(id)
      );
    }
    // We mutated the teams internal arrays, so trigger reactive stuff.
    $data = $data;
    selected = selected.filter((id) => !team.players.includes(id));
  };

  function deleteTeam(team) {
    $data.teams = $data.teams.filter((t) => t !== team);
  }
  function renameTeam(e, team) {
    if (e.detail.name) {
      team.name = e.detail.name;
      $data = $data;
    }
  }
</script>

  {#if !readOnly}
    <div class="player-header pad-top" id="teams">
      <p class="walkthrough-chapter-heading">Teams ({teams.length})</p>
    </div>
    <div class="team-grid-wrap">
      {#each teams as team (team.internalId || team.id)}
        <div
          class="card player-card glow-shadow team-card"
          transition:fade|local={{ duration: 200 }}
        >
          <Team
            {team}
            players={team.players
              .map((id) => $data.players.find((p) => p.id === id))
              .filter(Boolean)}
            selected={currentSessionSelected}
            on:selectPlayer
            on:delete={() => {
              deleteTeam(team);
            }}
            on:rename={(e) => {
              renameTeam(e, team);
            }}
            on:addPlayers={(e) => {
              addPlayers(team);
            }}
            on:unassignPlayer={(e) => {
              team.players = team.players.filter((id) => id !== e.detail.id);
              $data = $data;
            }}
          />
        </div>
      {/each}
    </div>
  {:else}
    {#each [...groupedTeams] as [session, sessionTeams] (session)}
      {#if sessionTeams.length}
        <div class="card well" transition:slide|local={{ duration: 200 }}>
          <div id={`session-${session}`} class="card-header">
            <h3>
              {#if session}
                <a
                  href="."
                  on:click|preventDefault={() => {
                    currentSession = session;
                  }}
                >
                  {formatSession(session)}
                </a>
              {:else}
                <em>No Session Group</em>
              {/if}
            </h3>
            ({sessionTeams.length}
            {sessionTeams.length == 1 ? "team" : "teams"})
          </div>

          {#each sessionTeams as team (team.internalId || team.id)}
            <div
              class="card player-card team-card"
              transition:fade|local={{ duration: 200 }}
            >
              <Team
                {team}
                players={team.players.map((id) =>
                  $data.players.find((p) => p.id === id)
                )}
                readOnly
                on:delete={() => {
                  deleteTeam(team);
                }}
                on:rename={(e) => {
                  renameTeam(e, team);
                }}
              />
            </div>
          {/each}
        </div>
      {/if}
    {/each}
  {/if}

<Modal bind:open={showInstructionsDialog}>
  <Instructions
    {showAutoBalance}
    on:clickCreateTeam={() => {
      const team = createTeam();
      addPlayers(team, true);
      $data.teams = [team, ...$data.teams];
      showInstructionsDialog = false;
    }}
    on:openAutoBalance={() => {
      showDialog = true;
      showInstructionsDialog = false;
    }}
  />
</Modal>

<style>
  h3 {
    font-size: 1rem;
  }
</style>
