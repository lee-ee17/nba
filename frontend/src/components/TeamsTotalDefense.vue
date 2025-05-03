<template>
  <div class="teams-defense">
    <div v-if="error" class="error-message">{{ error }}</div>
    <LoadingSpinner v-else-if="isLoading" />
    <div v-else class="defense-container" :class="{ expanded: isExpanded }">
      <div class="chart-section">
        <div
          id="defense-chart"
          ref="defenseChart"
          class="chart-container"
        ></div>
      </div>
      <div v-if="isExpanded && analysis" class="analysis-section">
        <div class="analysis-container">
          <h3>防守分析報告</h3>
          <div class="analysis-content">{{ analysis }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import apiService from "@/services/api";
  import LoadingSpinner from "./common/LoadingSpinner.vue";

  export default {
    name: "TeamsTotalDefense",
    components: {
      LoadingSpinner,
    },
    props: {
      teams: {
        type: Array,
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
      };
    },
    async mounted() {
      await this.fetchTeams();
    },
    watch: {
      teams: {
        handler: "fetchTeams",
        immediate: true,
      },
      isExpanded: {
        immediate: true,
        handler(newVal) {
          if (newVal && this.chartData.length > 0) {
            this.$nextTick(() => {
              this.renderDefenseChart();
              if (!this.analysis) {
                this.analyzeDefenseStats(this.chartData);
              }
            });
          }
          if (this.chartData.length > 0) {
            this.$nextTick(() => {
              this.updateChartSize();
            });
          }
        },
      },
    },
    methods: {
      async fetchTeams() {
        if (!this.teams.length) {
          this.error = "未選擇球隊";
          return;
        }

        this.isLoading = true;
        this.error = null;

        try {
          // 先取得球隊映射
          const teamMapping = await apiService.teams.getTeamMapping();
          // 將球隊名稱轉換為ID
          const teamIds = this.teams
            .map((teamName) => teamMapping[teamName])
            .filter((id) => id); // 過濾掉無效的ID

          if (teamIds.length === 0) {
            this.error = "無效的球隊名稱";
            return;
          }

          const response = await apiService.teams.getTeamStats(
            teamIds.join(",")
          );
          if (response.status === "success" && response.data.length > 0) {
            this.chartData = response.data;
            await this.analyzeDefenseStats(response.data);
            this.$nextTick(() => {
              if (document.getElementById("defense-chart")) {
                this.renderDefenseChart();
              }
            });
          } else {
            this.error = "無法取得球隊數據";
          }
        } catch (error) {
          console.error("Error:", error);
          this.error = "載入數據時發生錯誤";
        } finally {
          this.isLoading = false;
        }
      },
      renderDefenseChart() {
        const teamNames = [...new Set(this.chartData.map((d) => d.team))];
        const traces = [
          {
            x: teamNames,
            y: teamNames.map((team) =>
              this.chartData
                .filter((d) => d.team === team)
                .reduce((sum, d) => sum + d.blocks, 0)
            ),
            type: "bar",
            name: "蓋帽次數",
            marker: { color: "lightblue" },
          },
          {
            x: teamNames,
            y: teamNames.map((team) =>
              this.chartData
                .filter((d) => d.team === team)
                .reduce((sum, d) => sum + d.steals, 0)
            ),
            type: "bar",
            name: "抄球次數",
            marker: { color: "green" },
          },
          {
            x: teamNames,
            y: teamNames.map((team) =>
              this.chartData
                .filter((d) => d.team === team)
                .reduce((sum, d) => sum + d.defensive_rebounds, 0)
            ),
            type: "bar",
            name: "籃板次數",
            marker: { color: "orange" },
          },
        ];

        const layout = {
          barmode: "stack",
          title: {
            text: "NBA 球隊防守統計數據比較",
            font: { size: 30 },
          },
          xaxis: {
            title: {
              text: "球隊名稱",
              font: { size: 20 },
            },
            tickangle: -45,
            automargin: true,
          },
          yaxis: {
            title: {
              text: "防守次數",
              font: { size: 20 },
            },
            dtick: 1000,
          },
          paper_bgcolor: "white",
          plot_bgcolor: "white",
          showlegend: true,
          width: this.isExpanded ? 1000 : 600,
          height: this.isExpanded ? 600 : 450,
          autosize: true,
          margin: { t: 50, l: 50, r: 80, b: 50, pad: 4 },
        };

        Plotly.newPlot("defense-chart", traces, layout, {
          responsive: true,
          displayModeBar: false,
          useResizeHandler: true,
        });
      },
      async analyzeDefenseStats(data) {
        try {
          const response = await apiService.teams.analyzeStats({
            data: data,
            type: "defense",
          });
          this.analysis = response.data.analysis;
        } catch (error) {
          console.error("分析錯誤:", error);
        }
      },
      updateChartSize() {
        const chart = document.getElementById("defense-chart");
        if (chart) {
          const newLayout = {
            width: this.isExpanded ? 1000 : 600,
            height: this.isExpanded ? 600 : 450,
            autosize: true,
          };
          Plotly.relayout(chart, newLayout);
        }
      },
    },
  };
</script>

<style scoped>
  .teams-defense {
    padding: 10px;
    width: 100%;
    height: 100%;
  }

  .chart-container {
    width: 100%;
    height: 100%;
    min-height: 450px;
    border: 1px solid #eee;
    border-radius: 4px;
    padding: 10px;
  }

  .defense-container {
    display: flex;
    gap: 20px;
    transition: all 0.3s ease;
  }

  .defense-container:not(.expanded) {
    display: block;
  }

  .chart-section {
    width: 600px;
    transition: all 0.3s ease;
  }

  .expanded .chart-section {
    width: 1000px;
  }

  .analysis-container {
    background: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    height: 100%;
  }

  .analysis-section {
    width: 300px;
    overflow-y: auto;
    padding-right: 10px;
    max-height: 80vh;
  }

  .analysis-content {
    white-space: pre-line;
    line-height: 1.2;
    font-size: 14px;
  }

  h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 16px;
    color: #333;
  }

  .error-message {
    color: #ff4d4f;
    margin-bottom: 16px;
  }
</style>
