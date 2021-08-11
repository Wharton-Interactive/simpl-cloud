import { crossfade } from "svelte/transition";

export const [send, receive] = crossfade({
  duration: (d) => Math.sqrt(d * 200),

  fallback(node) {
    const style = getComputedStyle(node);
    const transform = style.transform === "none" ? "" : style.transform;

    return {
      duration: 600,
      css: (t) => `
        transform: ${transform} scale(${t});
        opacity: ${t}
      `,
    };
  },
});
