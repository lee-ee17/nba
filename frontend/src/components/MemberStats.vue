<template>
  <div :class="{ 'expanded-layout': isExpanded }">
    <LoadingSpinner v-if="isLoading" />
    <div v-if="error" class="error-message">{{ error }}</div>
    <div :class="['charts-container', { 'expand-chart': isExpanded }]">
      <div :id="chartId"></div>
    </div>
    <div v-if="analysis && isExpanded" class="analysis-section">
      <h3>球員表現分析</h3>
      <ul>
        <li>
          得分王：{{ analysis.topScorer.full_name }} ({{
            analysis.topScorer.points
          }}
          分)
        </li>
        <li>
          助攻王：{{ analysis.topAssist.full_name }} ({{
            analysis.topAssist.assists
          }}
          次)
        </li>
        <li>
          籃板王：{{ analysis.topRebounder.full_name }} ({{
            analysis.topRebounder.rebounds
          }}
          個)
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import apiService from "@/services/api";
  import LoadingSpinner from "./common/LoadingSpinner.vue";

  export default {
    name: "MemberStats",
    components: {
      LoadingSpinner,
    },
    props: {
      team: {
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
        chartData: [],
        isLoading: false,
        error: null,
        chartId: `member-chart-${Date.now()}`,
        analysis: null,
      };
    },
    async mounted() {
      this.fetchData();
    },
    beforeUnmount() {
      const element = document.getElementById("member-chart");
      if (element) {
        element.innerHTML = "";
      }
    },
    watch: {
      team: {
        immediate: true,
        handler() {
          this.fetchData();
        },
      },
      chartData: {
        handler() {
          this.analyzeData();
        },
        immediate: true,
      },
    },
    methods: {
      async fetchData() {
        this.isLoading = true;
        this.error = null;
        try {
          const response = await apiService.nba.getMemberStats();
          if (response.status === "success") {
            this.chartData = response.data.filter((d) => d.team === this.team);
            if (this.chartData.length === 0) {
              this.error = "找不到該球隊數據";
              return;
            }
            this.$nextTick(() => {
              this.renderCharts();
            });
          }
        } catch (error) {
          console.error("Error fetching member stats:", error);
          this.error = "數據載入失敗";
        } finally {
          this.isLoading = false;
        }
      },

      renderCharts() {
        if (!this.chartData || this.chartData.length === 0) {
          console.error("No data available for rendering");
          return;
        }

        const container = document.getElementById(this.chartId);
        if (!container) {
          console.error("Container element not found");
          return;
        }

        container.innerHTML = "";

        const playerNames = this.chartData.map((d) => d.full_name);
        const points = this.chartData.map((d) => d.points);
        const rebounds = this.chartData.map((d) => d.rebounds);
        const assists = this.chartData.map((d) => d.assists);

        const maxRange = Math.max(...[...points, ...rebounds, ...assists]) + 10;

        const data = [
          {
            type: "scatterpolar",
            r: points,
            theta: playerNames,
            fill: "toself",
            name: "得分",
            marker: { color: "rgba(255, 99, 71, 0.8)" },
          },
          {
            type: "scatterpolar",
            r: rebounds,
            theta: playerNames,
            fill: "toself",
            name: "籃板",
            marker: { color: "rgba(54, 162, 235, 0.8)" },
          },
          {
            type: "scatterpolar",
            r: assists,
            theta: playerNames,
            fill: "toself",
            name: "助攻",
            marker: { color: "rgba(75, 192, 192, 0.8)" },
          },
        ];

        const layout = {
          title: {
            text: `${this.team} 球員數據雷達圖`,
            font: { size: 24 },
          },
          polar: {
            radialaxis: {
              visible: true,
              range: [0, maxRange],
              tickfont: { size: 14 },
            },
            angularaxis: {
              tickfont: { size: 14 },
            },
          },
          margin: { l: 100, r: 100, t: 50, b: 50 },
          showlegend: true,
          legend: { font: { size: 16 } },
          width: 600,
          height: 500,
          autosize: true,
        };

        const teamDiv = document.createElement("div");
        teamDiv.style.width = "400px";
        teamDiv.style.height = "600px";
        teamDiv.id = `chart-${this.team.replace(/\s/g, "-")}`;
        container.appendChild(teamDiv);

        Plotly.newPlot(this.chartId, data, layout);
      },

      analyzeData() {
        if (!this.chartData?.length) return;

        this.analysis = {
          topScorer: this.chartData.reduce(
            (max, player) => (player.points > max.points ? player : max),
            { points: 0 }
          ),

          topAssist: this.chartData.reduce(
            (max, player) => (player.assists > max.assists ? player : max),
            { assists: 0 }
          ),

          topRebounder: this.chartData.reduce(
            (max, player) => (player.rebounds > max.rebounds ? player : max),
            { rebounds: 0 }
          ),
        };
      },
    },
  };
</script>

<style scoped>
  .member-stats {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
  }

  .charts-container {
    padding: 20px;
    min-height: 600px;
  }

  .charts-container:not(.expand-chart) {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .expanded-layout {
    display: flex;
    flex-direction: row;
    width: 100%;
    height: 100%;
  }

  .error-message {
    color: #ff4d4f;
    text-align: center;
    margin: 20px 0;
  }

  .analysis-section {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    width: 100%;
    margin-top: 20px;
    padding: 15px;
    background: #f5f5f5;
    border-radius: 8px;
  }

  .analysis-section {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
  }

  .analysis-section h3 {
    margin-bottom: 10px;
    color: #333;
    font-size: 1.8em;
  }

  .analysis-section ul {
    list-style: none;
    padding: 0;
    width: 100%;
  }

  .analysis-section li {
    margin-bottom: 8px;
    color: #666;
    font-size: 1.5em;
    padding: 10px;
    border-bottom: 1px solid #eee;
  }
</style>
