<template>
  <div class="teams-total-score">
    <div v-if="error" class="error-message">{{ error }}</div>
    <LoadingSpinner v-else-if="isLoading" />
    <div v-else class="score-container" :class="{ expanded: isExpanded }">
      <div class="chart-section">
        <div id="score-chart" ref="scoreChart" class="chart-container"></div>
      </div>
      <div v-if="isExpanded && analysis" class="analysis-section">
        <div class="analysis-container">
          <h3>球隊分析報告</h3>
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
    name: "TeamsTotalScore",
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
        analysis: null,
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
              this.renderChart();
              if (!this.analysis) {
                this.analyzeTeamPerformance(this.chartData);
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
          const teamMapping = await apiService.teams.getTeamMapping();
          const teamIds = this.teams
            .map((teamName) => teamMapping[teamName])
            .filter((id) => id);

          if (teamIds.length === 0) {
            this.error = "無效的球隊名稱";
            return;
          }

          const response = await apiService.teams.getTeamStats(
            teamIds.join(",")
          );
          if (response.status === "success" && response.data.length > 0) {
            this.chartData = response.data;
            await this.analyzeTeamPerformance(response.data);
            this.$nextTick(() => {
              if (document.getElementById("score-chart")) {
                this.renderChart();
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

      renderChart() {
        const teamNames = [...new Set(this.chartData.map((d) => d.team))];
        const traces = teamNames.map((teamName) => {
          const teamYears = this.chartData.filter((d) => d.team === teamName);
          return {
            mode: "lines+markers",
            type: "scatter",
            x: teamYears.map((d) => d.season),
            y: teamYears.map((d) => d.avg_points),
            name: teamName,
            marker: { size: 8 },
          };
        });

        const maxY = Math.max(...this.chartData.map((d) => d.avg_points));
        const minY = Math.min(...this.chartData.map((d) => d.avg_points));

        const layout = {
          title: {
            text: "NBA 球隊場均得分比較 (2018-2024)",
            font: { size: 24 },
          },
          xaxis: {
            title: "賽季年份",
            gridcolor: "#eee",
          },
          yaxis: {
            title: "場平均得分",
            dtick: 5,
            range: [minY - 5, maxY + 5],
            gridcolor: "#eee",
          },
          paper_bgcolor: "white",
          plot_bgcolor: "white",
          showlegend: true,
          width: this.isExpanded ? 1000 : 600,
          height: this.isExpanded ? 600 : 450,
          autosize: true,
          margin: { t: 50, l: 50, r: 80, b: 50, pad: 4 },
        };

        Plotly.newPlot("score-chart", traces, layout, {
          responsive: true,
          displayModeBar: false,
          useResizeHandler: true,
        });
      },

      async analyzeTeamPerformance(data) {
        try {
          this.analysis = null;
          const response = await apiService.teams.analyzeStats({
            data: data,
          });
          this.analysis = response.data.analysis;
        } catch (error) {
          console.error("分析錯誤:", error);
        }
      },
      updateChartSize() {
        const chart = document.getElementById("score-chart");
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
  .teams-total-score {
    padding: 10px;
    width: 100%;
    height: 100%;
  }

  .chart-container {
    width: 100%;
    height: 450px;
    min-height: 450px;
    border: 1px solid #eee;
    border-radius: 4px;
    padding: 10px;
    transition: height 0.3s ease;
  }

  .error-message {
    color: #ff4d4f;
    margin-bottom: 16px;
    text-align: center;
  }

  .analysis-section {
    width: 300px;
    overflow-y: auto;
    padding-right: 10px;
    max-height: 80vh;
  }

  .content-wrapper {
    display: flex;
    gap: 20px;
    height: 100%;
  }

  .content-wrapper:not(.expanded) {
    display: block;
  }

  .chart-section {
    flex: 1;
    min-width: 0;
    height: 100%;
  }

  .analysis-section {
    width: 300px;
    overflow-y: auto;
    padding-right: 10px;
  }

  .analysis-container {
    background: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    height: 100%;
  }

  .analysis-content {
    white-space: pre-line;
    line-height: 1.6;
    font-size: 14px;
  }

  h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 16px;
    color: #333;
  }

  .score-container {
    display: flex;
    gap: 20px;
    height: 100%;
  }

  .score-container:not(.expanded) {
    display: block;
  }

  .score-container.expanded .chart-container {
    height: 80vh;
  }
</style>
