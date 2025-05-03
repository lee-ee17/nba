// src/services/api.js
const API_BASE_URL =
  process.env.VUE_APP_API_BASE_URL || "http://localhost:5000";

const apiService = {
  cache: new Map(),

  async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  async post(endpoint, data) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  nba: {
    getStats: () => apiService.get("/api/nba-stats"),
    getMemberStats: () => apiService.get("/api/member-stats"),
  },

  teams: {
    getTeams: () => apiService.get("/api/teams"),
    getTeamMapping: async () => {
      if (apiService.cache.has('team-mapping')) {
        return apiService.cache.get('team-mapping');
      }

      const response = await apiService.get('/api/teams');
      if (response.status === 'success') {
        const mapping = response.data.reduce((acc, team) => {
          acc[team.full_name] = team.id;
          return acc;
        }, {});
        apiService.cache.set('team-mapping', mapping);
        return mapping;
      }
      return {};
    },
    getTeamStats: async (teamIds) => {
      const cacheKey = `team-stats-${teamIds}`;
      if (apiService.cache.has(cacheKey)) {
        return apiService.cache.get(cacheKey);
      }

      const response = await apiService.get(`/api/team-stats?team_ids=${teamIds}`);
      apiService.cache.set(cacheKey, response);
      return response;
    },
    getNbaTeams: () => apiService.get("/api/nba-teams"),
    analyzeStats: async (payload) => {
      const response = await apiService.post('/api/analyze-stats', payload);
      return response;
    },
  },
};

export default apiService;
