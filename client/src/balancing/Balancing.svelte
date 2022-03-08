<script>
  import AutoBalance from "../components/AutoBalance.svelte";
  import Switcher from "../components/Switcher.svelte";
  import SwitcherOption from "../components/SwitcherOption.svelte";
  import Players from "./Players.svelte";
  import StatusBox from "./StatusBox.svelte";
  import { data } from "./stores";
  import Teams from "./Teams.svelte";
  import { formatSession, shuffle } from "./utils";

  let showDialog = false;
  export let nextStep = null;
  export let downloadPlayersUrl = null;
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
  $: unassignedPlayers = (
    currentSession === null ? allUnassigned : unassigned[currentSession] || []
  ).filter((p) => !p.inactive);

  const createTeam = ({ name = null, session = null } = {}) => {
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
      session: session || currentSession,
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

  const addPlayers = ({
    team,
    onlyUnassigned = false,
    adding = null,
    session = null,
  }) => {
    const teams = $data.teams;
    if (!team) {
      team = createTeam({ session });
      $data.teams = [...$data.teams, team];
    }
    if (adding === null) {
      adding = currentSessionSelected;
      if (onlyUnassigned) {
        const assigned = teams.flatMap((t) => t.players);
        const selectedAssigned = adding.filter((id) => assigned.includes(id));
        adding = adding.filter(
          (id) =>
            !selectedAssigned.includes(id) &&
            !allInactive.map((p) => p.id).includes(id)
        );
      }
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
    allInactive
      .filter((p) => adding.includes(p.id))
      .map((p) => {
        p.inactive = false;
      });
    // We mutated the teams internal arrays, so trigger reactive stuff.
    $data = $data;
    selected = selected.filter((id) => !team.players.includes(id));
    if (session && currentSession) {
      currentSession = session;
    }
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

{#each [currentSession] as s (s)}
  <div class="player-grid">
    {#if unassignedPlayers.length}
      <div class="player-col">
        <Players
          {selected}
          players={unassignedPlayers}
          on:selectPlayer={(e) => {
            clickPlayer(e.detail.id);
          }}
          on:addPlayers={(e) => {
            addPlayers(e.detail);
          }}
          unassignedIsError={useSessions && currentSession === null}
        />
      </div>
    {:else if !$data?.players?.length}
      <div class="all-players-managed">
        <h3 class="card-heading text-center">
          There are no players registered.
        </h3>
        <p class="text-center">
          Once players have accepted their invitation from the marketplace, they
          will appear in this list.
        </p>
        <p class="text-center">
          All unassigned players must either be assigned to teams or made
          inactive before the run may begin.
        </p>
      </div>
    {:else}
      <div class="all-players-managed">
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
          {#if !useSessions || currentSession === null}
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
      </div>
    {/if}

    <div class="player-col">
      <StatusBox
        unassigned={allUnassigned.length}
        teams={$data.teams}
        inactive={allInactive.length}
        {downloadPlayersUrl}
        {showAutoBalance}
        allowCreate={!useSessions || currentSession !== null}
        bind:currentSession
        on:clickCreateTeam={() => {
          const team = createTeam();
          $data.teams = [...$data.teams, team];
          addPlayers({ team, onlyUnassigned: true });
        }}
        on:openAutoBalance={() => {
          showDialog = true;
        }}
      />
    </div>
  </div>

  <Teams
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
    on:addPlayers={(e) => {
      addPlayers(e.detail);
    }}
  />

  {#if allInactive.length}
    <div class="player-grid">
      <div class="player-col">
        <Players
          inactive
          {selected}
          players={allInactive}
          on:selectPlayer={(e) => {
            clickPlayer(e.detail.id);
          }}
          on:addPlayers={(e) => {
            addPlayers(e.detail);
          }}
          unassignedIsError={useSessions && currentSession === null}
        />
      </div>
    </div>
  {/if}
{/each}
