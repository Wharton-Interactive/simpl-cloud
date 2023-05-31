<script>
  let dropdown; //Dropdown Ref
  export let placeholderText = 'Select'
  export let expanded = false;

  const clickOutside = (element, callbackFunction) => {
    const onClick = (event) => {
      if (!element.contains(event.target)) {
        callbackFunction();
      }
    }

    window.addEventListener('click', onClick);

    return {
      update(newCallbackFunction) {
        callbackFunction = newCallbackFunction;
      },
      destroy() {
        window.removeEventListener('click', onClick);
      }
    }
  }

  const open = () => expanded = true
  const close = () => expanded = false

  const toggle = () => {
    expanded = !expanded
  }
</script>

<div class="has-dropdown narrow-dropdown"
     use:clickOutside={() => close()}
     class:is-expanded={expanded}
     bind:this={dropdown}>
  <a
    href="#"
    on:click|preventDefault|stopPropagation
    on:click={toggle}
    class="button dropdown-button hollow small"
  >
    {placeholderText}
  </a>
  <div class="dropdown">
    <slot></slot>
  </div>
</div>
