<template>
  <div class="plot-container">
    <div class="mode-controls">
      <button
        :class="['mode-btn', { active: mode === 'single' }]"
        @click="setMode('single')"
      >
        單隊模式
      </button>
      <button
        :class="['mode-btn', { active: mode === 'multiple' }]"
        @click="setMode('multiple')"
      >
        多隊模式
      </button>
    </div>

    <div v-if="mode === 'multiple'" class="selected-teams">
      <div class="selected-teams-list">
        <div v-for="team in selectedTeams" :key="team" class="team-tag">
          {{ team }}
          <span @click="removeTeam(team)" class="remove-btn">&times;</span>
        </div>
      </div>
      <button
        @click="compareTeams"
        :disabled="selectedTeams.length < 2"
        class="compare-btn"
      >
        比較球隊
      </button>
    </div>

    <LoadingSpinner v-if="isLoading" />
    <div
      id="plot"
      :class="{ loading: isLoading }"
      style="width: 100%; height: 100vh"
    ></div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import apiService from "@/services/api.js";
  import LoadingSpinner from "@/components/common/LoadingSpinner.vue";

  export default {
    name: "SelectTeam",
    components: {
      LoadingSpinner,
    },
    data() {
      return {
        teamLogos: {
          "Atlanta Hawks": require("../assets/photos/logos/hawks.svg"),
          "Boston Celtics": require("../assets/photos/logos/celtics.svg"),
          "Brooklyn Nets": require("../assets/photos/logos/nets.svg"),
          "Charlotte Hornets": require("../assets/photos/logos/hornets.svg"),
          "Chicago Bulls": require("../assets/photos/logos/bulls.svg"),
          "Cleveland Cavaliers": require("../assets/photos/logos/cavaliers.svg"),
          "Dallas Mavericks": require("../assets/photos/logos/mavericks.svg"),
          "Denver Nuggets": require("../assets/photos/logos/nuggets.svg"),
          "Detroit Pistons": require("../assets/photos/logos/pistons.svg"),
          "Golden State Warriors": require("../assets/photos/logos/warriors.svg"),
          "Houston Rockets": require("../assets/photos/logos/rockets.svg"),
          "Indiana Pacers": require("../assets/photos/logos/pacers.svg"),
          "LA Clippers": require("../assets/photos/logos/clippers.svg"),
          "Los Angeles Lakers": require("../assets/photos/logos/lakers.svg"),
          "Memphis Grizzlies": require("../assets/photos/logos/grizzlies.svg"),
          "Miami Heat": require("../assets/photos/logos/heat.svg"),
          "Milwaukee Bucks": require("../assets/photos/logos/bucks.svg"),
          "Minnesota Timberwolves": require("../assets/photos/logos/timberwolves.svg"),
          "New Orleans Pelicans": require("../assets/photos/logos/pelicans.svg"),
          "New York Knicks": require("../assets/photos/logos/knicks.svg"),
          "Oklahoma City Thunder": require("../assets/photos/logos/thunder.svg"),
          "Orlando Magic": require("../assets/photos/logos/magic.svg"),
          "Philadelphia 76ers": require("../assets/photos/logos/76ers.svg"),
          "Phoenix Suns": require("../assets/photos/logos/suns.svg"),
          "Portland Trail Blazers": require("../assets/photos/logos/blazers.svg"),
          "Sacramento Kings": require("../assets/photos/logos/kings.svg"),
          "San Antonio Spurs": require("../assets/photos/logos/spurs.svg"),
          "Toronto Raptors": require("../assets/photos/logos/raptors.svg"),
          "Utah Jazz": require("../assets/photos/logos/jazz.svg"),
          "Washington Wizards": require("../assets/photos/logos/wizards.svg"),
        },
        isLoading: false,
        mode: "single",
        selectedTeams: [],
        teamData: [],
      };
    },
    async mounted() {
      try {
        const response = await apiService.teams.getNbaTeams();
        if (response.status === "success" && Array.isArray(response.data)) {
          await this.initPlot(response.data);
          this.setupEventListeners();
        } else {
          console.error("Invalid data format:", response);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
      this.$nextTick(() => {
        window.addEventListener("resize", this.handleResize);
      });
    },
    beforeUnmounted() {
      window.removeEventListener("resize", this.handleResize);
    },
    methods: {
      handleResize() {
        const plot = document.getElementById("plot");
        if (plot && plot.layout) {
          Plotly.relayout(plot, {
            "xaxis.autorange": false,
            "yaxis.autorange": false,
          });
        }
      },
      async initPlot(data) {
        try {
          this.isLoading = true;
          if (!Array.isArray(data) || data.length === 0) {
            console.error("Invalid or empty data:", data);
            return;
          }

          const lookup = this.processData(data);
          const teams = Object.keys(lookup);
          this.teamData = teams.map((team) => ({ name: team }));
          const seasons = this.getUniqueSortedSeasons(data);
          const traces = this.createTraces(teams, lookup);
          const layout = this.createLayout(teams, traces, seasons);

          Plotly.newPlot("plot", traces, layout).then(() => {
            this.setupFrames(teams, seasons, lookup);
          });
        } catch (error) {
          console.error("Error initializing plot:", error);
        } finally {
          this.isLoading = false;
        }
      },
      processData(data) {
        if (!Array.isArray(data)) {
          console.error("Data is not an array:", data);
          return {};
        }

        const lookup = {};

        // 初始化時建立 Set
        data.forEach((d) => {
          if (d && d.team) {
            if (!lookup[d.team]) {
              lookup[d.team] = {
                x: [],
                y: [],
                text: [],
                seasons: [],
                validData: {},
              };
            }
          }
        });

        data.forEach((d) => {
          if (d && d.team && d.season) {
            const team = lookup[d.team];

            // 先檢查是否為有效數據
            const isValidData = d.total_defense > 0 && d.total_offense > 0;

            // 設置有效性標記
            team.validData[d.season] = isValidData;

            // 添加其他數據
            team.x.push(d.total_defense || 0);
            team.y.push(d.total_offense || 0);
            team.text.push(d.season);
            team.seasons.push(d.season);
          }
        });

        return lookup;
      },

      createTraces(teams, lookup) {
        return teams.map((team) => ({
          name: team,
          x: lookup[team].x,
          y: lookup[team].y,
          text: lookup[team].seasons.map((season) => `${team}<br>${season}`), // 修正 hover 文字
          mode: "markers",
          type: "scatter",
          marker: {
            size: 40,
            opacity: 0,
            color: "#4a90e2",
          },
          hoverinfo: "name+text",
          showlegend: false,
        }));
      },

      createLayout(teams, traces, seasons) {
        const logoSize = 1500; // 固定 logo 大小

        const allX = traces.flatMap((trace) => trace.x);
        const allY = traces.flatMap((trace) => trace.y);
        const xMin = Math.min(...allX);
        const xMax = Math.max(...allX);
        const yMin = Math.min(...allY);
        const yMax = Math.max(...allY);

        return {
          title: "NBA Teams Performance",
          xaxis: {
            title: "Defense",
            range: [xMin * 0.9, xMax * 1.1],
            fixedrange: true,
            zeroline: true,
            zerolinewidth: 2,
            zerolinecolor: "#969696",
            showline: true,
            showgrid: true,
            gridcolor: "#bdbdbd",
            gridwidth: 1,
            linecolor: "#636363",
            linewidth: 2,
            mirror: true,
          },
          yaxis: {
            title: "Offense",
            range: [yMin * 0.9, yMax * 1.1],
            fixedrange: true,
            zeroline: true,
            zerolinewidth: 2,
            zerolinecolor: "#969696",
            showline: true,
            showgrid: true,
            gridcolor: "#bdbdbd",
            gridwidth: 1,
            linecolor: "#636363",
            linewidth: 2,
            mirror: true,
          },
          hovermode: "closest",
          updatemenus: [
            {
              x: 0,
              y: 0,
              yanchor: "top",
              xanchor: "left",
              showactive: false,
              direction: "left",
              type: "buttons",
              pad: { t: 87, r: 10 },
              buttons: [
                {
                  method: "animate",
                  args: [
                    null,
                    {
                      mode: "immediate",
                      fromcurrent: true,
                      transition: { duration: 300 },
                      frame: { duration: 300, redraw: true },
                    },
                  ],
                  label: "Play",
                },
                {
                  method: "animate",
                  args: [
                    [null],
                    {
                      mode: "immediate",
                      transition: { duration: 0 },
                      frame: { duration: 0, redraw: true },
                    },
                  ],
                  label: "Pause",
                },
              ],
            },
          ],
          sliders: [
            {
              currentvalue: {
                visible: true,
                prefix: "Season:",
                xanchor: "right",
                font: { size: 20, color: "#666" },
              },
              pad: { l: 130, t: 30 },
              steps: seasons.map((season) => ({
                label: season,
                method: "animate",
                args: [
                  [season],
                  {
                    mode: "immediate",
                    transition: { duration: 300 },
                    frame: { duration: 300, redraw: true },
                  },
                ],
              })),
            },
          ],
          images: teams.map((team, i) => ({
            source: this.teamLogos[team],
            x: traces[i].x[0],
            y: traces[i].y[0],
            xref: "x",
            yref: "y",
            sizex: logoSize,
            sizey: logoSize,
            xanchor: "center",
            yanchor: "middle",
            sizing: "contain",
            layer: "above",
          })),
        };
      },

      setupFrames(teams, seasons, lookup) {
        const frames = seasons.map((season) => ({
          name: season,
          data: teams.map((team) => {
            const idx = lookup[team].seasons.indexOf(season);
            const hasValidData = lookup[team].validData[season];

            return {
              x: [lookup[team].x[idx]],
              y: [lookup[team].y[idx]],
              text: `${team}<br>${season}`,
              team: team,
              hasValidData: hasValidData,
            };
          }),
        }));

        const plot = document.getElementById("plot");

        // 移除舊的事件監聵器
        if (plot._events) {
          plot._events = {};
        }

        // 添加新的事件監聽器
        plot.on("plotly_animatingframe", (e) => {
          if (e && e.frame && e.frame.data) {
            this.updateImagePositions(e.frame.data, teams);
          }
        });

        plot.on("plotly_sliderchange", (e) => {
          if (e && typeof e.step !== "undefined") {
            const currentSeason = seasons[e.step];
            const frameData = frames.find((f) => f.name === currentSeason);
            if (frameData) {
              this.updateImagePositions(frameData.data, teams);
            }
          }
        });
        // 添加 frames
        Plotly.addFrames("plot", frames);
      },

      async updateImagePositions(frameData) {
        try {
          this.isLoading = true;
          const gd = document.getElementById("plot");
          if (!gd || !gd.layout) return;

          const logoSize = 1500; // 固定 logo 大小

          const images = frameData
            .map((d) => {
              if (
                !d ||
                !d.hasValidData ||
                !d.x ||
                !d.y ||
                d.x[0] === 0 ||
                d.y[0] === 0
              ) {
                return null;
              }

              return {
                source: this.teamLogos[d.team],
                x: d.x[0],
                y: d.y[0],
                xref: "x",
                yref: "y",
                sizex: logoSize,
                sizey: logoSize,
                xanchor: "center",
                yanchor: "middle",
                sizing: "contain",
                layer: "above",
                opacity: 1,
              };
            })
            .filter((img) => img !== null);

          if (images.length > 0) {
            Plotly.relayout(gd, { images: images });
          }
        } catch (error) {
          console.error("Error updating image positions:", error);
        } finally {
          this.isLoading = false;
        }
      },

      getUniqueSortedSeasons(data) {
        return Array.from(new Set(data.map((d) => d.season))).sort(
          (a, b) => parseInt(a.split("-")[0]) - parseInt(b.split("-")[0])
        );
      },

      setupEventListeners() {
        const plot = document.getElementById("plot");
        if (!plot) return;

        // 清除現有事件監聽器
        if (plot._events) {
          plot._events = {};
        }

        plot.on("plotly_click", async (data) => {
          if (!data || !data.points || !data.points[0]) return;

          const point = data.points[0];
          const teamName = point.data.name;
          let pointSeason = null;
          if (point.data.text) {
            pointSeason = point.data.text.split("<br>")[1];
          }

          if (this.mode === "single") {
            this.$router.push({
              name: "team-detail",
              params: { team: teamName, season: pointSeason },
            });
          } else {
            if (this.selectedTeams.includes(teamName)) {
              this.removeTeam(teamName);
            } else if (this.selectedTeams.length < 4) {
              this.selectedTeams.push(teamName);
            }
            this.updateTeamMarkersStyle();
          }
        });

        // 保持其他事件監聽器不變
        plot.on("plotly_animatingframe", (e) => {
          if (e && e.frame && e.frame.data) {
            this.updateImagePositions(e.frame.data);
          }
        });
      },

      async handleMultipleModeClick(teamName) {
        if (this.selectedTeams.includes(teamName)) {
          this.removeTeam(teamName);
        } else if (this.selectedTeams.length < 4) {
          this.selectedTeams.push(teamName);
        }

        // 立即更新樣式
        await this.$nextTick();
        this.updateTeamMarkersStyle();
      },

      removeTeam(team) {
        this.selectedTeams = this.selectedTeams.filter((t) => t !== team);
      },

      compareTeams() {
        if (this.selectedTeams.length >= 2) {
          this.$router.push({
            name: "teams-analysis",
            query: { teams: this.selectedTeams.join(",") },
          });
        }
      },

      async setMode(newMode) {
        this.mode = newMode;
        this.selectedTeams = [];

        // 確保 DOM 更新後再更新樣式
        await this.$nextTick();
        this.updateTeamMarkersStyle();
      },

      updateTeamMarkersStyle() {
        const plot = document.getElementById("plot");
        if (!plot) return;

        const update = {
          "marker.size": this.teamData.map((team) => {
            if (this.mode === "multiple") {
              return this.selectedTeams.includes(team.name) ? 60 : 40;
            }
            return 40;
          }),
          "marker.opacity": this.teamData.map(() => 0),
          "marker.color": this.teamData.map((team) => {
            if (this.mode === "multiple") {
              return this.selectedTeams.includes(team.name)
                ? "#ff6b6b"
                : "#4a90e2";
            }
            return "#4a90e2";
          }),
        };

        Plotly.restyle(plot, update);

        this.updateImagePositions(plot.data);
      },
    },
  };
</script>

<style scoped>
  .plot-container {
    position: relative;
  }

  #plot {
    background-color: white;
  }

  #plot.loading {
    opacity: 0.5;
  }

  .mode-controls {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    gap: 10px;
  }

  .mode-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background: #f0f0f0;
    cursor: pointer;
    transition: all 0.3s;
  }

  .mode-btn.active {
    background: #2196f3;
    color: white;
  }

  .selected-teams {
    position: fixed;
    top: 70px;
    right: 20px;
    z-index: 1000;
    background: white;
    padding: 10px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    max-width: 300px;
  }

  .selected-team {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px;
    margin: 5px 0;
    background: #f5f5f5;
    border-radius: 4px;
  }

  .confirm-btn {
    width: 100%;
    padding: 8px;
    margin-top: 10px;
    background: #4caf50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .confirm-btn:disabled {
    background: #cccccc;
    cursor: not-allowed;
  }
</style>
