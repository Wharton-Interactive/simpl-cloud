<script>
  import AutoBalance from "../components/AutoBalance.svelte";
  import Switcher from "../components/Switcher.svelte";
  import SwitcherOption from "../components/SwitcherOption.svelte";
  import Players from "./Players.svelte";
  import InactivePlayers from "./InactivePlayers.svelte";
  import StatusBox from "./StatusBox.svelte";
  import { data } from "./stores";
  import Teams from "./Teams.svelte";
  import { formatSession, shuffle } from "./utils";

  let showDialog = false;
  export let nextStep = null;
  let showAutoBalance;

  const exampleData = {
    sessions: [
      // comment all but one session to see different behaviour
      "10:00:00",
      "14:00:00",
      "other",
    ],
    players: [
      { id: 1, session: "10:00:00", name: "John Sampson", inactive: false },
      { id: 2, session: "10:00:00", name: "Jill Fisher", inactive: false },
      { id: 3, session: "10:00:00", name: "Jane Beard", inactive: false },
      { id: 4, session: "14:00:00", name: "Lucy Lawless", inactive: false },
      { id: 5, session: "14:00:00", name: "Gengis Khan", inactive: true },
      { id: 6, session: "other", name: "Michael Trythall", inactive: false },
      { id: 7, name: "The Wellerman", inactive: false },
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

  $: useSessions = $data?.sessions?.length > 1;
  let currentSession;
  $: switcherSessions = useSessions
    ? [...$data.sessions, null]
    : $data.sessions;

  let unassigned = {};
  let allUnassigned = [];
  $: {
    if ($data?.players) {
      const assigned = $data.teams.flatMap((t) => t.players);
      allUnassigned = $data.players.filter(
        (p) => !assigned.includes(p.id) && !p.inactive
      );
      unassigned = {};
      if (useSessions) {
        for (const session of $data.sessions) {
          unassigned[session] = allUnassigned.filter(
            (p) => !p.inactive && (!p.session || p.session === session)
          );
        }
      } else {
        if ($data?.sessions?.length === 1) {
          currentSession = $data.sessions[0];
        }
        unassigned[currentSession] = allUnassigned;
      }
      if (useSessions && currentSession === undefined) {
        currentSession =
          assigned && !allUnassigned.length ? null : $data.sessions[0];
      }
    }
  }
  $: allInactive = $data?.players?.filter((p) => p.inactive) || [];

  const createTeam = (name) => {
    if (!name) {
      const existingNames = $data.teams.map((team) => team.name);
      var i = 0;
      while (!name || existingNames.includes(name)) {
        name = `Team ${++i}`;
      }
    }
    return {
      internalId: `tmp${Math.random() * 1000000000 + 1000}`,
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
    if (useSessions) {
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

{#if $data.sessions && useSessions}
  <Switcher>
    {#each switcherSessions as session (session)}
      <SwitcherOption
        bind:state={currentSession}
        badge={(unassigned[session] &&
          unassigned[session].filter((p) => !p.inactive).length) ||
          null}
        outline={!session && !allUnassigned.length}
        value={session}
        >{session ? formatSession(session) : "Summary"}</SwitcherOption
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
    $data.teams.forEach((team) => {
      delete team.ready;
    });
    $data = $data;
    selected = [];
  }}
/>

{#if $data.players}
  {#each [currentSession] as s (s)}
    <div class="player-grid">
      <div class="player-col">
        <Players
          {selected}
          unassigned={currentSession === null
            ? allUnassigned
            : unassigned[currentSession] || []}
          {allInactive}
          on:selectPlayer={(e) => {
            clickPlayer(e.detail.id);
          }}
          nextStep={useSessions && currentSession !== null ? false : nextStep}
          unassignedIsError={useSessions && currentSession === null}
        />
      </div>

      <div class="player-col">
        <StatusBox
          {showAutoBalance}
          on:clickCreateTeam={() => {
            const team = createTeam();
            addPlayers(team, true);
            $data.teams = [team, ...$data.teams];
          }}
          on:openAutoBalance={() => {
            showDialog = true;
          }}
        />
      </div>
    </div>

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

    <div class="player-grid">
      <div class="player-col">
        <InactivePlayers
          {selected}
          unassigned={currentSession === null
            ? allUnassigned
            : unassigned[currentSession] || []}
          {allInactive}
          on:selectPlayer={(e) => {
            clickPlayer(e.detail.id);
          }}
          unassignedIsError={useSessions && currentSession === null}
        />
      </div>
    </div>
  {/each}
{/if}
