import Balancing from "./Balancing.svelte";
import Loader from "./Loader.svelte";
import NavManageTeams from "./NavManageTeams.svelte";
import NavStartGame from "./NavStartGame.svelte";
import { data } from "./stores";

export function init(target) {
  if (!target) {
    target = document.getElementById("app");
  }
  new Balancing({
    target,
    props: target.dataset,
  });

  const loader = document.getElementById("loader");
  if (loader) {
    new Loader({ target: loader, props: loader.dataset });
  }

  const unsubscribe = data.subscribe((value) => {
    if (!value.players) return;
    const navTeam = document.getElementById("simpl-team-nav");
    if (navTeam) {
      const anchor = navTeam.getElementsByTagName("A")[0] as HTMLAnchorElement;
      new NavManageTeams({
        target: navTeam,
        hydrate: true,
        props: {
          href: anchor.href,
          active: anchor.classList.contains("is-active"),
        },
      });
    }
    const navStartGame = document.getElementById("simpl-start-nav");
    if (navStartGame) {
      const href = (
        navStartGame.getElementsByTagName("A")[0] as HTMLAnchorElement
      ).href;
      new NavStartGame({
        target: navStartGame,
        hydrate: true,
        props: { href },
      });
    }
    unsubscribe();
  });
}
