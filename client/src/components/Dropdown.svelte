<script>
  import {onMount, onDestroy} from "svelte";

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

  const open = () => {
    expanded = true;
    closeOtherDropdowns();
  };

  const close = () => {
    expanded = false;
  };

  const toggle = () => {
    if (expanded) {
      close();
    } else {
      open();
    }
  };

  const closeOtherDropdowns = () => {
    const allDropdowns = document.querySelectorAll('.has-dropdown');
    allDropdowns.forEach((d) => {
      if (d !== dropdown) {
        d.dispatchEvent(new CustomEvent('closeDropdown'));
      }
    });
  };

  onMount(() => {
    dropdown.addEventListener('closeDropdown', close);
  });

  onDestroy(() => {
    dropdown.removeEventListener('closeDropdown', close);
  });
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
