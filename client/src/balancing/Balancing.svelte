<script>
  import AutoBalance from "../components/AutoBalance.svelte";
  import Switcher from "../components/Switcher.svelte";
  import SwitcherOption from "../components/SwitcherOption.svelte";
  import Players from "./Players.svelte";
  import StatusBox from "./StatusBox.svelte";
  import { data } from "./stores";
  import Teams from "./Teams.svelte";
  import { shuffle } from "./utils";

  let showDialog = false;
  export let nextStep = null;
  export let downloadPlayersUrl = null;

  const exampleData = {
    sessions: [
      // comment all but one session to see different behaviour
      { id: "10:00:00", name: "10 a.m." },
      { id: "14:00:00", name: "2 p.m." },
      { id: 1, name: "other" },
    ],
    players: [
      { id: 1, session: "10:00:00", name: "John Sampson", inactive: false },
      { id: 2, session: "10:00:00", name: "Jill Fisher", inactive: false },
      { id: 3, session: "10:00:00", name: "Jane Beard", inactive: false },
      { id: 4, session: "14:00:00", name: "Lucy Lawless", inactive: false },
      { id: 5, session: "14:00:00", name: "Gengis Khan", inactive: true },
      { id: 6, session: 1, name: "Michael Trythall", inactive: false },
      { id: 7, name: "The Wellerman", inactive: false },
    ],
    teams: [{ id: 1, session: "10:00:00", name: "First", players: [2] }],
    minimumPlayers: 2,
    maximumPlayers: 3,
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
          unassigned[session.id] = allUnassigned.filter(
            (p) => !p.inactive && (!p.session || p.session === session.id)
          );
        }
      } else {
        if ($data?.sessions?.length === 1) {
          currentSession = $data.sessions[0].id;
        }
        unassigned[currentSession] = allUnassigned;
      }
      if (useSessions && currentSession === undefined) {
        currentSession =
          assigned && !allUnassigned.length ? null : $data.sessions[0].id;
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

  $: showAutoBalance = (
    unassigned[currentSession]?.filter((p) => !p.inactive) || []
  ).length;

  let fillCount = 3;
</script>

{#if $data.sessions && useSessions}
  <Switcher>
    {#each switcherSessions as session (session?.id)}
      <SwitcherOption
        bind:state={currentSession}
        badge={(unassigned[session?.id] &&
          unassigned[session?.id].filter((p) => !p.inactive).length) ||
          null}
        outline={!session && !allUnassigned.length}
        value={session?.id || null}
        >{session ? session.name : "Summary"}</SwitcherOption
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
          inactive before the game may begin.
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
        <p class="text-center">
          {#if !useSessions || currentSession === null}
            {#if allInactive.length}
              All players are assigned to teams or marked <a
                href="#inactive-players">Inactive</a
              >.
            {:else}
              All players are assigned to teams.
            {/if}
          {:else}
            All players are assigned for this session group.
          {/if}
        </p>

        <!-- todo: this is error state, it needs wired up. -->
        <svg class="icon theme-caution-color" width="57" height="57" viewBox="0 0 57 57" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M55.1312 23.9513L33.0152 1.81268C31.7993 0.649266 30.182 0 28.5 0C26.818 0 25.2007 0.649266 23.9848 1.81268L1.86884 23.9513C0.672212 25.1497 0 26.7747 0 28.4691C0 30.1635 0.672212 31.7885 1.86884 32.9869L23.9848 55.1255C24.5774 55.7197 25.2812 56.1912 26.0559 56.5128C26.8307 56.8344 27.6612 57 28.5 57C29.3388 57 30.1693 56.8344 30.9441 56.5128C31.7188 56.1912 32.4226 55.7197 33.0152 55.1255L55.1312 32.9828C56.3278 31.7844 57 30.1594 57 28.465C57 26.7706 56.3278 25.1456 55.1312 23.9472V23.9513ZM25.4464 14.2066C25.4464 13.3959 25.7681 12.6184 26.3408 12.0452C26.9135 11.4719 27.6901 11.1499 28.5 11.1499C29.3099 11.1499 30.0865 11.4719 30.6592 12.0452C31.2319 12.6184 31.5536 13.3959 31.5536 14.2066V26.4333C31.5536 27.244 31.2319 28.0215 30.6592 28.5948C30.0865 29.168 29.3099 29.49 28.5 29.49C27.6901 29.49 26.9135 29.168 26.3408 28.5948C25.7681 28.0215 25.4464 27.244 25.4464 26.4333V14.2066ZM28.5 42.7357C27.6947 42.7357 26.9076 42.4967 26.238 42.0489C25.5685 41.601 25.0467 40.9645 24.7385 40.2198C24.4303 39.4751 24.3497 38.6556 24.5068 37.865C24.6639 37.0744 25.0517 36.3482 25.6211 35.7782C26.1905 35.2083 26.9159 34.8201 27.7057 34.6628C28.4955 34.5056 29.3141 34.5863 30.0581 34.8948C30.802 35.2032 31.4379 35.7256 31.8853 36.3958C32.3326 37.0661 32.5714 37.854 32.5714 38.6601C32.5714 39.741 32.1425 40.7777 31.3789 41.542C30.6154 42.3063 29.5798 42.7357 28.5 42.7357Z" fill="#FFBE15"/>
        </svg>
        <p class="text-center">
          <strong>Team B</strong> must have <strong>3</strong> to <strong>6</strong> players to begin.
        </p>
          
      </div>
    {/if}

    <div class="player-col">
      <StatusBox
        unassigned={allUnassigned.length}
        {data}
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
    {showAutoBalance}
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
