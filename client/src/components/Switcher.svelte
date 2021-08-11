<div id="progress-state">
  <slot />
</div>

<style scoped>
  :global(#progress-state :first-child) {
    border-radius: 4px 0px 0px 4px;
  }
  :global(#progress-state :last-child) {
    border-radius: 0px 4px 4px 0px;
  }
  :global(#progress-state button) {
    background: #fff;
    color: #425667;
    font-weight: bold;
    font-size: 16px;
    min-width: 8em;
    padding: 0.5em 1em;
    border-radius: 0;
    border: 1px solid #4288c7;
    margin: 0 1px;
  }
  :global(#progress-state button.selected) {
    color: #fff;
    background: #0d243f;
    border: none;
  }
</style>
