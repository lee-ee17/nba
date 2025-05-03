<template>
  <div :class="{ 'expanded-layout': isExpanded }">
    <LoadingSpinner v-if="isLoading" />
    <div v-if="error" class="error-message">{{ error }}</div>
    <div :class="['chart-container', { 'expand-chart': isExpanded }]">
      <div :id="chartId"></div>
    </div>
    <div v-if="analysis && isExpanded" class="analysis-section">
      <h3>球隊表現分析</h3>
      <ul>
        <li>
          最高得分賽季：{{ analysis.bestSeason }} ({{ analysis.maxPoints }} 分)
        </li>
        <li>平均得分：{{ analysis.avgPoints }} 分</li>
        <li>三分球比例：{{ analysis.threePointPercentage }}%</li>
      </ul>
    </div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import apiService from "@/services/api.js";
  import LoadingSpinner from "./common/LoadingSpinner.vue";

  export default {
    name: "NbaStatsGraph",
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
        exchangeData: [],
        isLoading: false,
        error: null,
        chartId: `stats-graph-${Date.now()}`,
        analysis: null,
      };
    },
    mounted() {
      this.fetchData();
    },
    beforeUnmount() {
      const element = document.getElementById("stats-graph");
      if (element) {
        element.innerHTML = "";
      }
    },
    watch: {
      exchangeData: {
        handler() {
          this.analyzeData();
        },
        immediate: true,
      },
      isExpanded: {
        handler(newVal) {
          if (newVal) {
            this.$nextTick(() => {
              this.createCharts();
            });
          }
        },
      },
    },
    methods: {
      async fetchData() {
        this.isLoading = true;
        this.error = null;
        try {
          const response = await apiService.nba.getStats();
          if (response.status === "success") {
            this.exchangeData = response.data.filter(
              (d) => d.team === this.team
            );
            this.createCharts();
          }
        } catch (error) {
          console.error("Error fetching NBA stats:", error);
          this.error = "數據載入失敗";
        } finally {
          this.isLoading = false;
        }
      },
      createCharts() {
        // 清除現有圖表
        const container = document.getElementById(this.chartId);
        if (!container) {
          console.error("Container element not found");
          return;
        }
        container.innerHTML = "";

        if (this.exchangeData.length === 0) {
          this.error = "找不到該球隊數據";
          return;
        }

        // Find the global maximum Y value
        const globalMaxY =
          Math.ceil(
            Math.max(
              ...this.exchangeData.map((d) =>
                Math.max(d.total_points, d.three_points)
              )
            ) / 1000
          ) * 1000;

        let trace1 = {
          type: "scatter",
          mode: "lines+markers",
          name: "Total Points",
          x: this.exchangeData.map((d) => d.season),
          y: this.exchangeData.map((d) => d.total_points),
        };

        let trace2 = {
          type: "bar",
          name: "Three-Point Scores",
          x: this.exchangeData.map((d) => d.season),
          y: this.exchangeData.map((d) => d.three_points),
          marker: {
            color: "orange",
            line: {
              color: "black",
              width: 0,
            },
          },
        };

        let layout = {
          title: `${this.team} Performance by Season`,
          xaxis: {
            title: "Season",
            showline: true,
          },
          yaxis: {
            title: "Scores",
            showline: true,
            range: [0, globalMaxY],
            tickformat: ",",
            tickvals: Array.from(
              { length: globalMaxY / 1000 + 1 },
              (_, i) => i * 1000
            ),
          },
          barmode: "overlay",
          bargap: 0,
          width: 800,
          height: 500,
        };

        let teamDiv = document.createElement("div");
        teamDiv.style.width = "100%";
        teamDiv.style.height = "600px";
        teamDiv.id = `chart-${this.team.replace(/\s/g, "-")}`;
        container.appendChild(teamDiv);

        Plotly.newPlot(this.chartId, [trace1, trace2], layout);
      },

      analyzeData() {
        if (!this.exchangeData?.length) return;

        const maxPoints = Math.max(
          ...this.exchangeData.map((d) => d.total_points)
        );
        const bestSeason = this.exchangeData.find(
          (d) => d.total_points === maxPoints
        )?.season;
        const avgPoints =
          this.exchangeData.reduce((sum, d) => sum + d.total_points, 0) /
          this.exchangeData.length;
        const threePointPercentage = (
          (this.exchangeData.reduce((sum, d) => sum + d.three_points, 0) /
            this.exchangeData.reduce((sum, d) => sum + d.total_points, 0)) *
          100
        ).toFixed(1);

        this.analysis = {
          bestSeason,
          maxPoints,
          avgPoints: Math.round(avgPoints),
          threePointPercentage,
        };
      },
    },
  };
</script>

<style scoped>
  .chart-container {
    padding: 20px;
    min-height: 600px;
  }

  .chart-container:not(.expand-chart) {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .expand-chart {
    padding: 20px;
    min-height: 600px;
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
