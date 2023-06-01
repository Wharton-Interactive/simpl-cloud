<script>
  import {onMount, onDestroy} from "svelte";

  let dropdown;
  let dropdownContainer;

  export let placeholderText = 'Select'
  export let expanded = false;

  const clickOutside = () => {
    //Close when clicking outside
    const onClick = (e) => {
      if (!dropdown.contains(e.target)) {
        close()
      }
    }

   document.addEventListener('click', onClick);

    return {
      destroy() {
        document.removeEventListener('click', onClick);
      }
    }
  }

  const close = () => {
    expanded = false;
  };

  const toggle = () => {
    expanded = !expanded;
  }

  onMount(() => {
    document.addEventListener('click', clickOutside)
  });

  onDestroy(() => {
      document.removeEventListener('click', clickOutside)
  });
</script>

<div class="has-dropdown narrow-dropdown"
     class:is-expanded={expanded}
     bind:this={dropdown}>
  <a
    href="#"
    on:click|preventDefault
    on:click={toggle}
    class="button dropdown-button hollow small"
    aria-expanded={expanded}
  >
    {placeholderText}
  </a>
  <div class="dropdown" bind:this={dropdownContainer}>
    <slot></slot>
  </div>
</div>
