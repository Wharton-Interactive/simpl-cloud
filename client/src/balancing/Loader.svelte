<script>
  import { GraphQLClient } from "graphql-request";
  import { onDestroy, onMount } from "svelte";
  import Loader from "../components/Loader.svelte";
  import query from "../queries/balancing.graphql";
  import alterPlayerMutation from "../queries/mutations/alterPlayer.graphql";
  import mutation from "../queries/mutations/balancing.graphql";
  import { alterPlayer, data, loaded } from "./stores";

  export let endpoint = "/graphql/";
  export let run;
  let saving = false;

  const client = new GraphQLClient(endpoint, { credentials: "include" });
  var dataCopy = {};

  onMount(() => {
    $loaded = false;
    client.request(query, { run }).then((d) => {
      if (d?.balancing) {
        dataCopy = JSON.parse(JSON.stringify(d.balancing));
        $data = d.balancing;
      }
      $loaded = true;
    });
  });

  onDestroy(
    alterPlayer.subscribe(async (v) => {
      if (!v) return;
      let d = await client.request(alterPlayerMutation, v);
      if (d?.alterPlayer) {
        $data.players = $data.players.map((p) =>
          p.id == d.alterPlayer.id ? Object.assign(p, d.alterPlayer) : p
        );
      }
    })
  );

  function updateData() {
    if (!dataCopy.teams) return;
    const dataTeamIds = $data.teams.map((team) => team.id);
    const params = {
      run,
      deleteTeams: dataCopy.teams
        .filter((team) => !team.id.startsWith("tmp"))
        .map((team) => team.id)
        .filter((id) => !dataTeamIds.includes(id)),
      teams: $data.teams
        .filter((team) => {
          const copy = dataCopy.teams.find((copy) => copy.id === team.id);
          return (
            !copy ||
            copy.name !== team.name ||
            copy.players.length !== team.players.length ||
            !copy.players.every((id) => team.players.includes(id))
          );
        })
        .map((team) =>
          team.id.startsWith("tmp") ? { ...team, id: null } : team
        ),
    };
    if (params.deleteTeams.length || params.teams.length) {
      console.debug("updating data");
      saving = true;
      dataCopy = JSON.parse(JSON.stringify($data));
      client.request(mutation, params).then((d) => {
        if (d?.balanceTeams) {
          $data = d.balanceTeams;
        }
        saving = false;
      });
    }
  }

  $: if ($loaded && $data && !saving) {
    console.debug("checking for changes");
    updateData();
  }
</script>

<Loader loaded={$loaded} {saving} />
