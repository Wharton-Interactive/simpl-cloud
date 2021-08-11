import { writable } from "svelte/store";

export const data = writable({
  sessions: [],
  teams: [],
  players: null,
});

export const loaded = writable(false);

function notifier() {
  const subs = new Set();
  const subscribe = (cb) => {
    subs.add(cb);
    return () => {
      subs.delete(cb);
    };
  };
  const notify = (val) => {
    subs.forEach((cb) => cb(val));
  };
  return { subscribe, notify };
}

export const alterPlayer = notifier();
