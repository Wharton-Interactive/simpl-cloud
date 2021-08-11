<script>
  import { data } from "./stores";

  export let href = null;

  let assigned = [];
  let unassignedCount;
  $: {
    assigned = $data.teams.flatMap((t) => t.players);
    unassignedCount = $data.players?.filter(
      (p) => !assigned.includes(p.id)
    ).length;
  }
</script>

<li class="todo-item">
  <a
    class="todo-link"
    class:is-ready={!unassignedCount && assigned.length}
    {href}
  >
    <span class="todo-link-title">Start Game</span>
  </a>
</li>
