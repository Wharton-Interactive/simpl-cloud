<script>
  import { fade, slide } from "svelte/transition";
  import Team from "./Team.svelte";
  import { formatSession } from "./utils";

  export let data;
  export let currentSession = undefined;
  export let currentSessionSelected;
  export let selected;
  export let createTeam;
  export let showDialog;
  export let showAutoBalance;

  $: readOnly = currentSession === null;
  $: teams = readOnly
    ? $data.teams
    : $data.teams.filter((t) => !t.session || t.session === currentSession);
  let groupedTeams = new Map();
  let total = 0;
  let unassigned = 0;
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
      const assigned = $data.teams.flatMap((t) => t.players);
      unassigned = $data.players.filter((p) => !assigned.includes(p.id)).length;
      total = $data.players.length;
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

<div class="player-col">
  {#if !readOnly}
    <div class="player-header">
      <p class="walkthrough-chapter-heading">Teams ({teams.length})</p>

      {#if showAutoBalance}
        <button
          class="button no-border strong theme-info-color"
          on:click={() => {
            showDialog = true;
          }}
        >
          <svg
            fill="none"
            class="icon"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 22 22"
          >
            <path
              d="M18.857 0H3.143A3.143 3.143 0 000 3.143v15.714A3.143 3.143 0 003.143 22h15.714A3.143 3.143 0 0022 18.857V3.143A3.143 3.143 0 0018.857 0zm0 9.429h-6.286V3.143h6.286v6.286zM3.143 3.143h6.286v6.286H3.143V3.143zm0 15.714v-6.286h6.286v6.286H3.143zm9.428 0v-6.286h6.286v6.286h-6.286z"
              fill="#0C66B8"
            />
          </svg>
          Auto Balance
        </button>
      {/if}

      <button
        class="button no-border strong theme-info-color"
        on:click={() => {
          const team = createTeam();
          addPlayers(team, true);
          $data.teams = [team, ...$data.teams];
        }}
      >
        <svg
          width="26"
          height="26"
          viewBox="0 0 26 26"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          class="icon"
        >
          <circle
            cx="13"
            cy="13"
            r="12"
            stroke="currentColor"
            stroke-width="2"
          />
          <g clip-path="url(#clip0)">
            <path
              d="M17.9653 11.6049H15.1504C14.9504 11.6049 14.7585 11.5254 14.6171 11.384C14.4757 11.2426 14.3962 11.0507 14.3962 10.8507H14.3952V8.00958C14.3885 7.81386 14.3061 7.62837 14.1652 7.49226C14.0244 7.35615 13.8363 7.28005 13.6404 7.28003H12.3612C12.262 7.27989 12.1637 7.29931 12.072 7.33717C11.9803 7.37503 11.8969 7.43059 11.8267 7.50068C11.7564 7.57077 11.7007 7.65402 11.6626 7.74565C11.6246 7.83729 11.605 7.93553 11.6049 8.03476V10.8497C11.6049 11.2666 11.2666 11.6039 10.8507 11.6039H8.0227C7.82453 11.6076 7.63572 11.6889 7.49685 11.8303C7.35798 11.9717 7.28013 12.162 7.28003 12.3602V13.6394C7.28003 14.0516 7.61098 14.3878 8.0227 14.3936H10.8507V14.3946C11.2677 14.3946 11.6049 14.7329 11.6049 15.1488V17.9774C11.6083 18.1753 11.6894 18.364 11.8305 18.5028C11.9717 18.6416 12.1617 18.7194 12.3596 18.7195H13.6394C14.0521 18.7195 14.3873 18.3886 14.3936 17.9774V15.1488H14.3946C14.3946 14.7319 14.7329 14.3946 15.1488 14.3946V14.3936H17.9894C18.1852 14.3872 18.3708 14.3049 18.5071 14.1642C18.6433 14.0234 18.7195 13.8353 18.7195 13.6394V12.3602C18.7196 12.261 18.7002 12.1628 18.6624 12.0712C18.6246 11.9796 18.569 11.8963 18.499 11.8262C18.4289 11.756 18.3457 11.7004 18.2542 11.6624C18.1626 11.6245 18.0644 11.6049 17.9653 11.6049Z"
              fill="currentColor"
            />
          </g>
          <defs>
            <clipPath id="clip0">
              <rect
                width="11.44"
                height="11.44"
                fill="white"
                transform="translate(7.28003 7.28003)"
              />
            </clipPath>
          </defs>
        </svg>

        Add Team
      </button>
    </div>
    <div class="team-scroll">
      {#each teams as team (team.id)}
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
    {#if unassigned}
      <div class="note theme-alert-color">
        <div class="note-content">
          {unassigned} of {total} player{total === 1 ? "" : "s"} still unassigned.
        </div>
      </div>
    {:else}
      <div class="note theme-success-color">
        <div class="note-content">
          {total > 1 ? "All" : ""}
          {total} player{total === 1 ? "" : "s"} assigned to teams.
        </div>
      </div>
    {/if}
    <dl>
      {#each $data.sessions as session}
        <dt>{formatSession(session)}</dt>
        <dd>
          {#if groupedTeams.get(session)?.length}
            <a
              href={`#session-${session}`}
              on:click|preventDefault={() => {
                document
                  .getElementById(`session-${session}`)
                  .scrollIntoView({ behavior: "smooth" });
              }}
              >{groupedTeams.get(session).length} Team{groupedTeams.get(session)
                .length === 1
                ? ""
                : "s"}</a
            >
          {:else}
            No teams
          {/if}
        </dd>
      {/each}
    </dl>
    {#each [...groupedTeams] as [session, sessionTeams] (session)}
      {#if sessionTeams.length}
        <div transition:slide|local={{ duration: 200 }}>
          <h3 id={`session-${session}`}>
            <a
              href="."
              on:click|preventDefault={() => {
                currentSession = session;
              }}
              >{formatSession(session)}
            </a>
          </h3>
          {#each sessionTeams as team (team.id)}
            <div
              class="card player-card glow-shadow team-card"
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
</div>
