<script>
  import { createEventDispatcher } from "svelte";

  import example from "../img/player-management-examples.png";

  export let showAutoBalance;

  const dispatch = createEventDispatcher();
</script>

<div>

  {#if showAutoBalance}
  <h3 class="player-help-header">Option 1: Build teams automatically</h3>
  <p>Choose
    <button
      class="button no-border strong theme-info-color inline-help-button"
      on:click={() => dispatch("openAutoBalance")}
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
    to randomly distribute players into teams.</p>
  {/if}

  <h3 class="player-help-header">{#if showAutoBalance}Option 2: {/if}Build teams manually</h3>
  <img class="player-help-img" src={example} alt="Player Management Examples" />
  <ol>
    <li>Select one or more players from the ’Unassigned Players’ list by hovering over their name and clickinghe check box.</li>
    <li>Click
      <button
        class="button no-border strong theme-info-color inline-help-button"
        on:click={() => dispatch("clickCreateTeam")}
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
      to start a new team with the selected players, and repeat until all players are assigned.
    </li>
  </ol>

  <div class="note border-theme theme-caution-color">
    <svg class="icon" fill="none" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 27 27">
      <path d="M26.115 11.345 15.639.86a3.094 3.094 0 0 0-4.278 0L.885 11.345a3.029 3.029 0 0 0 0 4.28l10.476 10.487a3.02 3.02 0 0 0 4.278 0l10.476-10.489a3.029 3.029 0 0 0 0-4.28v.002ZM12.054 6.73A1.449 1.449 0 0 1 13.5 5.282a1.446 1.446 0 0 1 1.446 1.447v5.792A1.449 1.449 0 0 1 13.5 13.97a1.446 1.446 0 0 1-1.446-1.448V6.73ZM13.5 20.243a1.928 1.928 0 0 1-1.892-2.307 1.931 1.931 0 0 1 2.63-1.407 1.93 1.93 0 0 1 .626 3.149 1.928 1.928 0 0 1-1.364.565Z" fill="#FFBE15"/>
    </svg>
    <div class="note-content">
      <p>You may <strong>rearrange teams</strong> as much as you’d like before the game is in play.</p>
      <p>All players must be <em>assigned</em> or marked <em>inactive</em> before the game can start.</p>
    </div>
  </div>
</div>