from flask import Flask, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore
import pandas as pd # type: ignore
from nba_api.stats.static.teams import get_teams # type: ignore
from nba_api.stats.endpoints import teamyearbyyearstats # type: ignore
import json

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8080" ,"http://localhost:8081"],  # Vue.js 開發伺服器的位置
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/nba-teams', methods=['GET'])
def get_nba_teams_stats():
    try:
        with open('./data/nba_team.json') as f:
            nba_data = json.load(f)

        formatted_data = []
        
        valid_seasons = ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
        
        # 遍歷每個球隊的每個賽季
        for team, seasons in nba_data.items():
            for season, players in seasons.items():
                # 計算該賽季所有球員的總和
                if season not in valid_seasons:
                    continue
                
                total_defense = sum(
                    player['defensive_rebounds'] + 
                    player['steals'] + 
                    player['blocks']
                    for player in players
                )
                
                total_offense = sum(
                    player['points']
                    for player in players
                )
                
                formatted_data.append({
                    'team': team,
                    'season': season,
                    'total_defense': total_defense,
                    'total_offense': total_offense
                })
        
        return jsonify({
            "status": "success",
            "data": formatted_data
        })
        
    except Exception as e:
        print("Error:", str(e))
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/nba-stats', methods=['GET'])
def get_nba_stats():
    try:
        # Read the JSON data
        df = pd.read_json("./data/nba_data.json")

        # Filter relevant seasons
        all_seasons = ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
        team_data = df[df["season"].isin(all_seasons)].copy()

        # Calculate three-point scores
        team_data['three_points'] = team_data['three_point_field_goals_made'] * 3

        # Group data by team and season
        grouped = team_data.groupby(["team", "season"]).agg(
            total_points=('points', 'sum'),
            three_points=('three_points', 'sum')
        ).reset_index()

        # Convert to dictionary format
        result = grouped.to_dict(orient="records")
        
        return jsonify({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/member-stats', methods=['GET'])
def get_member_stats():
    try:
        df = pd.read_json("./data/nba_data.json")
        all_seasons = ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024"]
        team_data = df[df["season"].isin(all_seasons)]
        
        grouped = team_data.groupby(["team", "full_name"]).agg(
            points=('points', 'sum'),
            assists=('assists', 'sum'),
            rebounds=('rebounds', 'sum')
        ).reset_index()
        
        return jsonify({
            "status": "success",
            "data": grouped.to_dict('records')
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
        
@app.route('/api/teams', methods=['GET'])
def get_teams_list():
    try:
        teams = get_teams()
        return jsonify({
            "status": "success",
            "data": teams
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/team-stats', methods=['GET'])
def get_team_stats():
    try:
        # 從 query string 獲取 team_ids
        team_ids_str = request.args.get('team_ids', '')
        team_ids = team_ids_str.split(',') if team_ids_str else []
        
        if not team_ids:
            return jsonify({
                "status": "error",
                "message": "No teams selected"
            }), 400

        selected_data = []
        for team_id in team_ids:
            try:
                stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
                team_stats_df = stats.get_data_frames()[0]
                
                filtered_df = team_stats_df[
                    (team_stats_df['YEAR'] >= '2018-19') & 
                    (team_stats_df['YEAR'] <= '2023-24')
                ]

                for _, row in filtered_df.iterrows():
                    selected_data.append({
                        'team': row['TEAM_NAME'],
                        'season': row['YEAR'],
                        # 'total_points': row['PTS'],
                        'avg_points': row['PTS'] / row['GP'],
                        'three_points': row.get('FG3M', 0) * 3,
                        'blocks': row['BLK'],
                        'steals': row['STL'],
                        'defensive_rebounds': row['DREB']
                    })
            except Exception as e:
                print(f"Error fetching stats for team ID {team_id}: {e}")

        return jsonify({
            "status": "success",
            "data": selected_data
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/analyze-stats', methods=['POST'])
def analyze_stats():
    try:
        data = request.json
        
        if data.get('type') == 'defense':
            analysis_result = perform_defense_analysis(data['data'])
        else:
            analysis_result = perform_score_analysis(data['data'])
        
        return jsonify({
            "status": "success",
            "data": {
                "analysis": analysis_result
            }
        })
    except Exception as e:
        return jsonify({
            "status": "warning",
            "data": {
                "analysis": perform_score_analysis(data['data'])
            }
        })

def perform_score_analysis(data):
    try:
        teams_data = {}
        analysis_text = []
        
        for entry in data:
            team = entry['team']
            if team not in teams_data:
                teams_data[team] = []
            teams_data[team].append(entry)
            
        for team, stats in teams_data.items():
            total_points = sum(s['total_points'] for s in stats)
            avg_points = total_points / len(stats)
            max_points = max(stats, key=lambda x: x['total_points'])
            min_points = min(stats, key=lambda x: x['total_points'])
            
            analysis = f"""
                {team} 分析：
                - 平均得分：{avg_points:.1f}
                - 最佳表現：{max_points['season']} 賽季，得分 {max_points['total_points']}
                - 最差表現：{min_points['season']} 賽季，得分 {min_points['total_points']}
                """
            analysis_text.append(analysis)
            
        return "\n".join(analysis_text)
    except Exception as e:
        return f"本地分析發生錯誤: {str(e)}"
    
def perform_defense_analysis(data):
    try:
        teams_data = {}
        analysis_text = []
        
        # 整理數據
        for entry in data:
            team = entry['team']
            if team not in teams_data:
                teams_data[team] = []
            teams_data[team].append(entry)
        
        # 分析每隊防守數據
        for team, stats in teams_data.items():
            # 計算總防守數據
            total_blocks = sum(s['blocks'] for s in stats)
            total_steals = sum(s['steals'] for s in stats)
            total_def_rebounds = sum(s['defensive_rebounds'] for s in stats)
            
            # 計算平均值
            avg_blocks = total_blocks / len(stats)
            avg_steals = total_steals / len(stats)
            avg_def_rebounds = total_def_rebounds / len(stats)
            
            # 找出最佳防守表現賽季
            best_defense = max(stats, key=lambda x: x['blocks'] + x['steals'] + x['defensive_rebounds'])
            
            analysis = f"""
                {team} 防守分析：
                - 平均數據：
                  • 籃板：{avg_def_rebounds:.1f}
                  • 抄截：{avg_steals:.1f}
                  • 蓋帽：{avg_blocks:.1f}
                - 最佳防守賽季：{best_defense['season']}
                  • 籃板：{best_defense['defensive_rebounds']}
                  • 抄截：{best_defense['steals']}
                  • 蓋帽：{best_defense['blocks']}
                """
            analysis_text.append(analysis)
            
        return "\n".join(analysis_text)
    except Exception as e:
        return f"防守分析發生錯誤: {str(e)}"
        
if __name__ == '__main__':
    app.run(debug=True)