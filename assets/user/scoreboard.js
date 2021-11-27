function htmlEntities(string) {
  return $("<div/>")
    .text(string)
    .html();
}

// https://gist.github.com/0x263b/2bdd90886c2036a1ad5bcf06d6e6fb37
function colorHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
    hash = hash & hash;
  }
  // Range calculation
  // diff = max - min;
  // x = ((hash % diff) + diff) % diff;
  // return x + min;
  // Calculate HSL values
  // Range from 0 to 360
  let h = ((hash % 360) + 360) % 360;
  // Range from 75 to 100
  let s = (((hash % 25) + 25) % 25) + 75;
  // Range from 40 to 60
  let l = (((hash % 20) + 20) % 20) + 40;
  return `hsl(${h}, ${s}%, ${l}%)`;
}

const graph = $("#score-graph");
const table = $("#scoreboard tbody");
const id = parseInt(window.location.href.split('/').slice(-1));

const updateScores = () => {
  new KoH_API().get_scoreboard_list({ challengeId: id }).then(response => {
    const teams = response.data;
    table.empty();

    for (let i = 0; i < teams.length; i++) {
      const row = [
        "<tr>",
        '<th scope="row" class="text-center">',
        i + 1,
        "</th>",
        '<td><a href="' + teams[i].account_url + '">',
        htmlEntities(teams[i].name),
        "</a></td>",
        "<td>",
        teams[i].score,
        "</td>",
        "</tr>"
      ].join("");
      table.append(row);
    }
  });
};

const buildGraphData = () => {
  return new KoH_API().get_scoreboard_detail({ challengeId: id, count: 10 }).then(response => {
    const places = response.data;

    const teams = Object.keys(places);
    if (teams.length === 0) {
      return false;
    }

    const option = {
      title: {
        left: "center",
        text: "Top 10"
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "cross"
        }
      },
      legend: {
        type: "scroll",
        orient: "horizontal",
        align: "left",
        bottom: 35,
        data: []
      },
      toolbox: {
        feature: {
          dataZoom: {
            yAxisIndex: "none"
          },
          saveAsImage: {}
        }
      },
      grid: {
        containLabel: true
      },
      xAxis: [
        {
          type: "time",
          boundaryGap: false,
          data: []
        }
      ],
      yAxis: [
        {
          type: "value"
        }
      ],
      dataZoom: [
        {
          id: "dataZoomX",
          type: "slider",
          xAxisIndex: [0],
          filterMode: "filter",
          height: 20,
          top: 35,
          fillerColor: "rgba(233, 236, 241, 0.4)"
        }
      ],
      series: []
    };

    for (let i = 0; i < teams.length; i++) {
      const team_score = [];
      const times = [];
      let max_score = 0;
      for (let j = 0; j < places[teams[i]]["solves"].length; j++) {
        if (id == places[teams[i]]["solves"][j].challenge_id && max_score < places[teams[i]]["solves"][j].value) {
          team_score.push(places[teams[i]]["solves"][j].value);
          const date = dayjs(places[teams[i]]["solves"][j].date);
          times.push(date.toDate());
          max_score = places[teams[i]]["solves"][j].value;
        }
      }

      var scores = times.map(function(e, i) {
        return [e, team_score[i]];
      });

      option.legend.data.push(places[teams[i]]["name"]);

      const data = {
        name: places[teams[i]]["name"],
        type: "line",
        label: {
          normal: {
            position: "top"
          }
        },
        itemStyle: {
          normal: {
            color: colorHash(places[teams[i]]["name"] + places[teams[i]]["id"])
          }
        },
        data: scores
      };
      option.series.push(data);
    }

    return option;
  });
};

const createGraph = () => {
  buildGraphData().then(option => {
    if (option === false) {
      // Replace spinner
      graph.html(
        '<h3 class="opacity-50 text-center w-100 justify-content-center align-self-center">No solves yet</h3>'
      );
      return;
    }

    graph.empty(); // Remove spinners
    let chart = echarts.init(document.querySelector("#score-graph"));
    chart.setOption(option);

    $(window).on("resize", function() {
      if (chart != null && chart != undefined) {
        chart.resize();
      }
    });
  });
};

const updateGraph = () => {
  buildGraphData().then(option => {
    let chart = echarts.init(document.querySelector("#score-graph"));
    chart.setOption(option);
  });
};

function update() {
  updateScores();
  updateGraph();
}

$(() => {
  setInterval(update, 300000); // Update scores every 5 minutes
  createGraph();
});

window.updateScoreboard = update;
