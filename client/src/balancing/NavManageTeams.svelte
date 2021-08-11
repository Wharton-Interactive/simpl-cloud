<script>
  import { data } from "./stores";

  export let active = false;
  export let href;

  let assigned = [];
  let unassignedCount;
  $: {
    assigned = $data.teams.flatMap((t) => t.players);
    unassignedCount = $data.players?.filter(
      (p) => !assigned.includes(p.id) && !p.inactive
    ).length;
  }
</script>

<li class="todo-item">
  <a
    class="todo-link"
    class:is-active={active}
    class:is-alert={unassignedCount}
    class:is-complete={!unassignedCount && assigned.length}
    {href}
  >
    <span class="todo-link-title">Manage Teams</span>
    {#if unassignedCount}
      <span class="todo-help-text">
        {#if unassignedCount == 1}
          {unassignedCount} player needs balancing
        {:else}
          {unassignedCount} players need balancing
        {/if}
      </span>
    {/if}
  </a>
</li>
