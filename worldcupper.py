"""
https://www.fifaindex.com/teams/?type=1
https://www.fifaindex.com/teams/fifa07_3/?league=78&type=1
https://www.fifaindex.com/teams/fifa06_2/?league=78&type=1

Attacks per game - average unknown
Number of attacks,

Goals per game
http://www.slate.com/articles/sports/sports_nut/2013/08/the_numbers_game_why_soccer_teams_score_fewer_goals_than_they_did_100_years.html

"""
import csv
import random
import time

AVERAGE_GOALS_PER_GAME = 2.6
AVERAGE_SHOTS_PER_GAME = 20  # Per team, shots on target about 50%. Attack and midfield + some random boost



# attack = how many are on target
# defense = how many go in

class WorldCupper(object):

    def __init__(self, filename='worldcupper.csv'):
        groups = {}  # Team groups in WC

        with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                groups.setdefault(row['group'], []).append(row)
                # groups[row['group']] = row
                # print(row['team'], row['fifa_rating'])

        for group_name, group_teams in groups.items():
            for i, team_1 in enumerate(group_teams):
                for team_2 in group_teams[i+1:]:
                    print(team_1['name'].capitalize(), ' vs ', team_2['name'].capitalize())

                    #  Lower is better
                    team1_overall_rating = float(team_1['fifa_rating']) + float(team_1['elo_rating']) + \
                        float(team_1['goalimpact_rating']) + (5 - float(team_1['ea_fifa_18_rating']))
                    team2_overall_rating = float(team_2['fifa_rating']) + float(team_2['elo_rating']) + \
                        float(team_2['goalimpact_rating']) + (5 - float(team_2['ea_fifa_18_rating']))

                    print('overall', team1_overall_rating, team2_overall_rating)

                    team1_relative_rating = team1_overall_rating / max(team1_overall_rating, team2_overall_rating)
                    team2_relative_rating = team2_overall_rating / max(team1_overall_rating, team2_overall_rating)
                    print('relative', team1_relative_rating, team2_relative_rating)

                    team1_random_factor = float(team_1['overall']) / 100.0 * random.random() + \
                                          (float(team_1['boost']) / 100.0)

                    team2_random_factor = float(team_2['overall']) / 100.0 * random.random() + \
                                          (float(team_2['boost']) / 100.0)

                    print('rand factor', team1_random_factor, team2_random_factor)

                    # midfield  = how many shots you get (attacks)
                    team1_attack = float(team_1['att']) / 100.0
                    team2_attack = float(team_2['att']) / 100.0
                    team1_midfield = float(team_1['mid']) / 100.0
                    team2_midfield = float(team_2['mid']) / 100.0

                    # How much better is team 1 vs team 2?
                    team1_attack_factor = None
                    
                    team_1_number_of_attacks = random.uniform((team1_attack + team1_midfield)/2.0, 1.0) * AVERAGE_SHOTS_PER_GAME * random.uniform(0.8, 1.5)
                    team_2_number_of_attacks = random.uniform((team2_attack + team2_midfield)/2.0, 1.0) * AVERAGE_SHOTS_PER_GAME * random.uniform(0.75, 1.5)
                    # team_2_number_of_attacks = float(team_1['att']) / 100.0 * float(team_2['mid']) / 100.0 * \
                    #                            random.uniform(0.25, 1.0) * AVERAGE_SHOTS_PER_GAME

                    print('no attacks', team_1_number_of_attacks, team_2_number_of_attacks)
                    # team_1_chance_of_scoring =
                    # team_1_random_boost = random.random()  # 0 to 1

        # print(groups)

        # Sort groups by points, then do 0th group A to play group B 1th,
        #   const leftSideWinner = runPlayoffs(mappedTeams.A[0], mappedTeams.B[1], mappedTeams.C[0], mappedTeams.D[1], mappedTeams.E[0], mappedTeams.F[1], mappedTeams.G[0], mappedTeams.H[1]);
        # const rightSideWinner = runPlayoffs(mappedTeams.B[0], mappedTeams.A[1], mappedTeams.D[0], mappedTeams.C[1], mappedTeams.F[0], mappedTeams.E[1], mappedTeams.H[0], mappedTeams.G[1]);


if __name__ == "__main__":
    wc = WorldCupper()
