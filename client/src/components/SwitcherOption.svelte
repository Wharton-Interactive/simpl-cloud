<script>
  export let state;
  export let value = null;
  export let badge = null;

  const setValue = el => {
    if (!value) value = el.innerText;
  };
</script>
<li class="tab-item">
<button
  use:setValue
  class="tab-link"
  class:selected={state === value}
  on:click={() => (state = value)}
  data-notification-badge={badge}>
  <slot />
  </button>
</li>
