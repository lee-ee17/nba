<template>
  <div class="detail-container">
    <button v-if="!focusedChart" class="back-btn" @click="goBack">
      <span>&larr;</span> 返回選擇
    </button>
    <div class="carousel-container">
      <button
        v-if="!focusedChart"
        class="nav-btn left-btn"
        @click="rotate('left')"
      >
        &lt;
      </button>
      <div class="carousel">
        <div
          v-for="(type, index) in ['stats', 'member', 'graph']"
          :key="index"
          class="chart-box"
          :class="{
            front: currentPosition[index] === 'front',
            left: currentPosition[index] === 'left',
            right: currentPosition[index] === 'right',
            expanded:
              focusedChart === type && currentPosition[index] === 'front',
            collapsing: isCollapsing && focusedChart === type,
          }"
          @click="handleCardClick($event, type)"
        >
          <div class="chart-content">
            <component
              :is="getComponent(type)"
              :team="team"
              :season="season"
              :isExpanded="
                focusedChart === type && currentPosition[index] === 'front'
              "
            />
          </div>
        </div>
        <!-- <div v-if="focusedChart" class="overlay" @click="resetFocus"></div> -->
      </div>
      <button
        v-if="!focusedChart"
        class="nav-btn right-btn"
        @click="rotate('right')"
      >
        &gt;
      </button>
    </div>
  </div>
</template>

<script>
  import TeamsTotalStats from "@/components/TeamsTotalStats.vue";
  import MemberStats from "@/components/MemberStats.vue";
  import NbaStatsGraph from "@/components/NbaStatsGraph.vue";

  export default {
    name: "TeamDetailView",
    components: {
      TeamsTotalStats,
      MemberStats,
      NbaStatsGraph,
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
    },
    data() {
      return {
        focusedChart: null,
        isCollapsing: false,
        currentPosition: ["front", "left", "right"],
        components: ["stats", "member", "graph"],
      };
    },
    mounted() {
      if (!this.team || !this.season) {
        this.$router.push({ name: "select-team" });
        return;
      }
      window.addEventListener("keydown", this.handleKeyPress);
    },
    beforeMount() {
      window.removeEventListener("keydown", this.handleKeyPress);
    },
    watch: {
      team: {
        immediate: true,
        handler(newTeam) {
          if (!newTeam) {
            this.$router.push({ name: "select-team" });
          }
        },
      },
    },
    methods: {
      getComponent(type) {
        const components = {
          stats: "TeamsTotalStats",
          member: "MemberStats",
          graph: "NbaStatsGraph",
        };
        return components[type];
      },
      async handleCardClick(event, chartName) {
        if (
          this.currentPosition[this.components.indexOf(chartName)] === "front"
        ) {
          if (this.focusedChart === chartName) {
            this.resetFocus();
          } else if (!this.focusedChart) {
            // 只有在沒有展開的卡片時才展開
            const card = event.currentTarget;
            const rect = card.getBoundingClientRect();

            // 設置原始位置
            this.$nextTick(() => {
              card.style.setProperty("--original-width", `${rect.width}px`);
              card.style.setProperty("--original-height", `${rect.height}px`);
              card.style.setProperty("--original-top", `${rect.top}px`);
              card.style.setProperty("--original-left", `${rect.left}px`);
              this.focusedChart = chartName;
            });
          }
        }
      },
      resetFocus() {
        if (this.focusedChart) {
          this.isCollapsing = true;
          this.$nextTick(() => {
            setTimeout(() => {
              this.isCollapsing = false;
              this.focusedChart = null;
            }, 300);
          });
        }
      },
      rotate(direction) {
        if (this.focusedChart) return;

        if (direction === "right") {
          this.currentPosition = [
            this.currentPosition[2],
            this.currentPosition[0],
            this.currentPosition[1],
          ];
        } else {
          this.currentPosition = [
            this.currentPosition[1],
            this.currentPosition[2],
            this.currentPosition[0],
          ];
        }
      },
      goBack() {
        this.$router.push({ name: "select-team" });
      },
      handleKeyPress(event) {
        if (event.key === "ArrowRight" && !this.focusedChart) {
          this.rotate("right");
        } else if (event.key === "ArrowLeft" && !this.focusedChart) {
          this.rotate("left");
        } else if (event.key === "ArrowUp" && !this.focusedChart) {
          const frontIndex = this.currentPosition.indexOf("front");
          const frontType = this.components[frontIndex];
          const card = document.querySelector(".chart-box.front");
          if (card) {
            this.handleCardClick({ currentTarget: card }, frontType);
          }
        } else if (event.key === "ArrowDown" && this.focusedChart) {
          this.resetFocus();
        }
      },
    },
  };
</script>

<style scoped>
  .detail-container {
    min-height: 100vh;
    position: relative;
    overflow: hidden;
  }

  .back-btn {
    position: fixed;
    top: 20px;
    left: 20px;
    padding: 10px 20px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    z-index: 1000;
    transition: all 0.3s ease;
  }

  .back-btn:hover {
    background: rgba(0, 0, 0, 0.9);
    transform: translateY(-2px);
  }

  .back-btn span {
    font-size: 20px;
  }

  .carousel-container {
    position: relative;
    width: 100%;
    height: 100vh;
    perspective: 1000px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
  }

  .carousel {
    position: relative;
    width: 60%;
    height: 70%;
    transform-style: preserve-3d;
    transform: translateZ(-300px);
  }

  .chart-box {
    position: absolute;
    width: 100%;
    height: 100%;
    transition: all 0.8s ease-out;
    transform-origin: center;
    transform-style: preserve-3d;
    cursor: pointer;
  }

  .chart-box.front {
    transform: rotateY(0deg) translateZ(300px);
    z-index: 3;
    opacity: 1;
    transition-delay: 0s;
  }

  .chart-box.left {
    transform: rotateY(-120deg) translateZ(300px);
    z-index: 1;
    opacity: 0;
    pointer-events: none;
    transition-delay: 0s;
  }

  .chart-box.right {
    transform: rotateY(120deg) translateZ(300px);
    z-index: 1;
    opacity: 0;
    pointer-events: none;
    transition-delay: 0s;
  }

  .nav-btn {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    background: rgba(0, 0, 0, 0.5);
    color: white;
    border: none;
    padding: 15px;
    cursor: pointer;
    border-radius: 50%;
    z-index: 4;
    transition: all 0.3s ease;
  }

  nav-btn:hover {
    background: rgba(0, 0, 0, 0.8);
  }

  .left-btn {
    left: 20px;
  }

  .right-btn {
    right: 20px;
  }

  .chart-content {
    width: 100%;
    height: 100%;
    background: white;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    padding: 20px;
    backface-visibility: hidden;
    position: relative;
    z-index: 12;
  }

  .charts-wrapper {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    padding: 20px;
    max-width: 100%;
    margin: 0 auto;
    position: relative;
    z-index: 1;
    height: calc(100vh - 40px);
  }

  .chart-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 600px;
    position: relative;
  }

  .chart-box.expanded {
    transform: translate(-50%, -50%) !important; /* 修改這行，加上 !important */
    position: fixed;
    display: flex;
    justify-content: center;
    z-index: 12;
    animation: expandFromOrigin 0.3s ease-out forwards;
    background: white;
    pointer-events: auto;
    cursor: default;
  }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0; /* 加入右邊界 */
    bottom: 0; /* 加入下邊界 */
    width: 100%; /* 改為100% */
    height: 100%; /* 改為100% */
    background: rgba(0, 0, 0, 0.5);
    z-index: 11;
    cursor: pointer;
    pointer-events: auto;
    margin: 0; /* 確保沒有邊距 */
    padding: 0; /* 確保沒有內距 */
  }

  .chart-box.collapsing {
    animation: collapseToOrigin 0.3s ease-out forwards;
  }

  @keyframes expandFromOrigin {
    0% {
      transform: translate(0, 0) scale(1);
      width: var(--original-width);
      height: var(--original-height);
      top: var(--original-top);
      left: var(--original-left);
    }
    100% {
      transform: translate(-50%, -50%) scale(1);
      width: 100vw;
      height: 100vh;
      top: 50%;
      left: 50%;
    }
  }

  @keyframes collapseToOrigin {
    0% {
      transform: translate(-50%, -50%) scale(1);
      width: 100vw;
      height: 100vh;
      top: 50%;
      left: 50%;
    }
    100% {
      transform: translate(0, 0) scale(1);
      width: var(--original-width);
      height: var(--original-height);
      top: var(--original-top);
      left: var(--original-left);
    }
  }

  .chart-box:not(.expanded):not(.collapsed):hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  }

  .chart-box.expanded .chart-content {
    width: 100%;
    height: 100%;
    padding: 20px;
    pointer-events: all;
    z-index: 1001;
  }

  .chart-box.expanded :deep(.chart-container),
  .chart-box.expanded :deep(.charts-container) {
    width: 100%;
    height: 100%;
    pointer-events: all;
    z-index: 1000;
  }

  .chart-box.collapsed {
    transform: scale(0.95);
    opacity: 0.6;
    pointer-events: none;
  }

  @media (max-width: 1200px) {
    .charts-wrapper {
      grid-template-columns: 1fr;
    }
  }
</style>
