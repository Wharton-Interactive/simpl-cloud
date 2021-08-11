<script>
  import AutoBalance from "../components/AutoBalance.svelte";
  import Switcher from "../components/Switcher.svelte";
  import SwitcherOption from "../components/SwitcherOption.svelte";
  import Players from "./Players.svelte";
  import { data } from "./stores";
  import Teams from "./Teams.svelte";
  import { formatSession, shuffle } from "./utils";

  let showDialog = false;
  export let nextStep;
  $: activePlayerIds =
    $data?.players && $data.players.filter((p) => !p.inactive).map((p) => p.id);

  const exampleData = {
    sessions: [], // ["10:00:00", "14:00:00", "17:00:00"],
    players: [
      { id: 1, session: "10:00:00", name: "John Sampson" },
      { id: 2, session: "10:00:00", name: "Jill Fisher" },
      { id: 3, session: "10:00:00", name: "Jane Beard" },
      { id: 4, session: "14:00:00", name: "Lucy Lawless" },
      { id: 5, session: "14:00:00", name: "Gengis Khan" },
      { id: 6, session: "14:00:00", name: "Michael Trythall" },
      { id: 7, name: "The Wellerman" },
    ],
    teams: [{ id: 1, session: "10:00:00", name: "First", players: [2] }],
  };
  exampleData.players.map(
    (p) => (p.email = `${p.name.replace(" ", ".").toLowerCase()}@wharton.edu`)
  );

  export let example = null;
  if (example) {
    $data = exampleData;
  }

  let currentSession;
  $: switcherSessions =
    $data.teams.length && $data.sessions?.length
      ? [...$data.sessions, null]
      : $data.sessions;

  let unassigned = {};
  $: {
    if ($data?.players) {
      const assigned = $data.teams.flatMap((t) => t.players);
      unassigned = {};
      let totalUnassigned = 0;
      if ($data.sessions) {
        for (const session of $data.sessions) {
          unassigned[session] = $data.players.filter(
            (p) =>
              (!p.session || p.session === session) && !assigned.includes(p.id)
          );
          totalUnassigned += unassigned[session].length;
        }
      }
      if (!$data.sessions?.length) {
        unassigned[undefined] = $data.players.filter(
          (p) => !assigned.includes(p.id)
        );
      }
      if ($data.sessions?.length && currentSession === undefined) {
        currentSession =
          assigned && !totalUnassigned ? null : $data.sessions[0];
      }
    }
  }

  const createTeam = (name) => {
    if (!name) {
      const existingTeams = $data.teams.length;
      name = `Team ${existingTeams + 1}`;
    }
    return {
      id: `tmp${Math.random() * 1000000000 + 1000}`,
      name,
      session: currentSession,
      players: [],
    };
  };

  let selected = [];
  const clickPlayer = (id) => {
    if (selected.includes(id)) {
      selected = selected.filter((val) => val !== id);
    } else {
      selected = [...selected, id];
    }
  };

  let currentSessionSelected = [];
  $: {
    if ($data.sessions?.length) {
      const currentSessionPlayers = $data.players
        .filter(
          (p) =>
            currentSession !== null &&
            (!p.session || p.session === currentSession)
        )
        .map((p) => p.id);
      currentSessionSelected = selected.filter((id) =>
        currentSessionPlayers.includes(id)
      );
    } else {
      currentSessionSelected = selected;
    }
  }

  const unassignPlayer = (id) => {
    for (const team of $data.teams) {
      team.players = team.players.filter((playerId) => playerId !== id);
    }
    $data = $data;
  };

  let fillCount = 3;
</script>

{#if $data.sessions && $data.sessions.length > 1}
  <Switcher>
    {#each switcherSessions as session (session)}
      <SwitcherOption
        bind:state={currentSession}
        badge={(unassigned[session] && unassigned[session].length) || null}
        value={session}
        >{session ? formatSession(session) : "Overview"}</SwitcherOption
      >
    {/each}
  </Switcher>
{/if}

<AutoBalance
  bind:open={showDialog}
  unassigned={unassigned[currentSession]?.filter((p) => !p.inactive) || []}
  on:submit={(e) => {
    const fillCount = e.detail.fillCount;

    const availableTeams = $data.teams.filter(
      (team) =>
        (!team.session || team.session === currentSession) &&
        team.players.length < fillCount
    );
    let team;
    let shuffled = unassigned[currentSession].filter((p) => !p.inactive);
    shuffle(shuffled);
    for (const player of shuffled) {
      if (availableTeams.length) {
        team = availableTeams.shift();
      } else {
        team = createTeam();
        $data.teams.unshift(team);
      }
      team.players.push(player.id);
      if (team.players.length < fillCount) {
        availableTeams.unshift(team);
      }
    }
    $data = $data;
    selected = [];
  }}
/>

{#if $data.players}
  {#each [currentSession] as s (s)}
    <div class="player-grid">
      {#if currentSession !== null}
        <Players
          {selected}
          unassigned={unassigned[currentSession] || []}
          on:selectPlayer={(e) => {
            clickPlayer(e.detail.id);
          }}
          {nextStep}
        />
      {/if}

      <Teams
        bind:selected
        {data}
        bind:currentSession
        {currentSessionSelected}
        {createTeam}
        showAutoBalance={(
          unassigned[currentSession]?.filter((p) => !p.inactive) || []
        ).length}
        bind:showDialog
        on:selectPlayer={(e) => {
          clickPlayer(e.detail.id);
        }}
        on:unassignPlayer={(e) => {
          unassignPlayer(e.detail.id);
        }}
      />
    </div>
  {/each}
{/if}
