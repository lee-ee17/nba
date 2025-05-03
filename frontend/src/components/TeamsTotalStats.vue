<template>
  <div class="teams-total-stats">
    <LoadingSpinner v-if="isLoading" />
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else>
      <h2 class="team-title">
        {{ getTeamFullName(team) }} {{ season }} 賽季統計
      </h2>
      <div
        class="charts-container"
        v-show="!isLoading"
        :class="{ expanded: isExpanded }"
      >
        <div :id="shotChartId" class="chart"></div>
        <div :id="makeChartId" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script>
  import LoadingSpinner from "./common/LoadingSpinner.vue";
  import Plotly from "plotly.js-dist";
  import nbaData from "@/assets/data/nba.json";

  export default {
    name: "TeamsTotalStats",
    components: {
      LoadingSpinner,
    },
    props: {
      team: {
        type: String,
        required: true,
      },
      season: {
        type: String,
        required: true,
      },
      isExpanded: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        isLoading: false,
        error: null,
        nbaData: nbaData,
        shotChartId: `shot-chart-${Date.now()}`,
        makeChartId: `make-chart-${Date.now()}`,
        teamNames: {
          "atlanta-hawks": "Atlanta Hawks",
          "boston-celtics": "Boston Celtics",
          "brooklyn-nets": "Brooklyn Nets",
          "charlotte-hornets": "Charlotte Hornets",
          "chicago-bulls": "Chicago Bulls",
          "cleveland-cavaliers": "Cleveland Cavaliers",
          "dallas-mavericks": "Dallas Mavericks",
          "denver-nuggets": "Denver Nuggets",
          "detroit-pistons": "Detroit Pistons",
          "golden-state-warriors": "Golden State Warriors",
          "houston-rockets": "Houston Rockets",
          "indiana-pacers": "Indiana Pacers",
          "la-clippers": "LA Clippers",
          "los-angeles-lakers": "Los Angeles Lakers",
          "memphis-grizzlies": "Memphis Grizzlies",
          "miami-heat": "Miami Heat",
          "milwaukee-bucks": "Milwaukee Bucks",
          "minnesota-timberwolves": "Minnesota Timberwolves",
          "new-orleans-pelicans": "New Orleans Pelicans",
          "new-york-knicks": "New York Knicks",
          "oklahoma-city-thunder": "Oklahoma City Thunder",
          "orlando-magic": "Orlando Magic",
          "philadelphia-76ers": "Philadelphia 76ers",
          "phoenix-suns": "Phoenix Suns",
          "portland-trail-blazers": "Portland Trail Blazers",
          "sacramento-kings": "Sacramento Kings",
          "san-antonio-spurs": "San Antonio Spurs",
          "toronto-raptors": "Toronto Raptors",
          "utah-jazz": "Utah Jazz",
          "washington-wizards": "Washington Wizards",
        },
        years: [
          "2018-19",
          "2019-20",
          "2020-21",
          "2021-22",
          "2022-23",
          "2023-24",
        ],
      };
    },
    watch: {
      team: {
        immediate: true,
        handler(newTeam) {
          if (newTeam) {
            // 找到對應的 team ID
            const teamId = Object.entries(this.teamNames).find(
              (name) => name === newTeam
            )?.[0];
            if (teamId) {
              this.selectedTeam = teamId;
            }
          }
        },
      },
      season: {
        immediate: true,
        handler(newSeason) {
          if (newSeason) {
            this.selectedYear = newSeason;
          }
        },
      },
      $route: {
        immediate: true,
        handler() {
          if (this.selectedTeam && this.selectedYear) {
            this.renderCharts();
          }
        },
      },
    },
    mounted() {
      this.$nextTick(() => {
        this.renderCharts();
      });
    },
    beforeUnmount() {
      const element = document.getElementById("member-chart");
      if (element) {
        element.innerHTML = "";
      }
    },
    methods: {
      renderCharts() {
        const convertSeason = (season) => {
          const [start, end] = season.split("-");
          return `${start}-${end.slice(2)}`;
        };

        const formattedSeason =
          this.season.length === 9 ? convertSeason(this.season) : this.season;

        const teamData = this.nbaData.find((item) => {
          return (
            item.YEAR === formattedSeason &&
            item.TEAM === this.getTeamFullName(this.team)
          );
        });

        if (!teamData) {
          this.error = `找不到 ${this.team} 在 ${this.season} 賽季的數據`;
          return;
        }

        // 計算各種投籃數據
        const FG2A = teamData.FGA - teamData.FG3A;
        const FG3A = teamData.FG3A;
        const FTA = teamData.FTA;

        const FG2M = (teamData.FGM - teamData.FG3M) * 2;
        const FG3M = (teamData.FG3M) * 3;
        const FTM = teamData.FTM;

        // 繪製出手結構圖
        const trace1 = {
          type: "pie",
          labels: ["兩分球", "三分球", "罰球"],
          values: [FG2A, FG3A, FTA],
          textinfo: "label+value+percent",
          marker: {
            colors: ["#FF6347", "#FFD700", "#40E0D0"],
            line: { color: "black", width: 3 },
          },
        };

        // 繪製命中結構圖
        const trace2 = {
          type: "pie",
          labels: ["兩分球", "三分球", "罰球"],
          values: [FG2M, FG3M, FTM],
          textinfo: "label+value+percent",
          marker: {
            colors: ["#FF6347", "#FFD700", "#40E0D0"],
            line: { color: "black", width: 3 },
          },
        };

        const layout1 = {
          title: "球隊出手結構",
          margin: { t: 30, l: 0 },
          font: { size: 15 },
          width: this.isExpanded ? 1000 : 350,
          height: this.isExpanded ? 800 : 500,
          autosize: true,
        };

        const layout2 = {
          title: "球隊得分結構",
          margin: { t: 30, l: 0 },
          font: { size: 15 },
          width: this.isExpanded ? 1000 : 350,
          height: this.isExpanded ? 800 : 500,
          autosize: true,
        };

        Plotly.newPlot(this.shotChartId, [trace1], layout1);
        Plotly.newPlot(this.makeChartId, [trace2], layout2);
      },
      getTeamFullName(team) {
        // 從 teamNames 中找到完整隊名
        const entry = Object.entries(this.teamNames).find(
          ([key, value]) => value === team || key === team
        );
        return entry ? entry[1] : team;
      },
    },
  };
</script>

<style scoped>
  .teams-total-stats {
    padding: 20px;
    width: 100%;
    height: 100%;
  }

  .team-title {
    text-align: center;
    margin-bottom: 20px;
    color: #1a1a1a;
    font-size: 24px;
    font-weight: bold;
  }

  .charts-container {
    display: flex;
    gap: 20px;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
  }

  .chart {
    width: 100%;
    height: 350px;
    border: 1px solid #eee;
    border-radius: 4px;
    justify-content: center;
    align-items: center;
  }

  .charts-container.expanded .chart {
    width: 50%;
  }

  .error-message {
    color: #ff4d4f;
    margin-bottom: 16px;
  }
</style>
