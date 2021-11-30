<script>
  export let state;
  export let value = null;
  export let badge = null;
  export let outline = false;

  const setValue = (el) => {
    if (!value) value = el.innerText;
  };
</script>

<li class="tab-item">
  <button
    use:setValue
    class="tab-link"
    class:outline={outline || badge}
    aria-selected={state === value}
    on:click={() => (state = value)}
    data-notification-badge={badge}
  >
    <slot />
  </button>
</li>

<style>
  .tab-link.outline {
    border-width: 1px;
    border-style: solid;
    border-bottom: 0 none;
  }
</style>
