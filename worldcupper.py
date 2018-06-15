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
import math
from collections import OrderedDict
import time


AVERAGE_GOALS_PER_GAME = 2.6
AVERAGE_SHOTS_PER_GAME = 20  # Per team, shots on target about 50%. Attack and midfield + some random boost



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

        total_total_goals = 0
        games = 0
        groups = OrderedDict(sorted(groups.items()))
        for group_name, group_teams in groups.items():
            for i, team_1 in enumerate(group_teams):
                for team_2 in group_teams[i+1:]:
                    team1_score = 0
                    team2_score = 0

                    # print(team_1['name'].capitalize(), ' vs ', team_2['name'].capitalize())

                    #  Lower is better
                    team1_overall_rating = float(team_1['fifa_rating']) + float(team_1['elo_rating']) + \
                        float(team_1['goalimpact_rating']) + (5 - float(team_1['ea_fifa_18_rating']))
                    team2_overall_rating = float(team_2['fifa_rating']) + float(team_2['elo_rating']) + \
                        float(team_2['goalimpact_rating']) + (5 - float(team_2['ea_fifa_18_rating']))

                    # print('overall', team1_overall_rating, team2_overall_rating)

                    team1_relative_rating = team1_overall_rating / max(team1_overall_rating, team2_overall_rating)
                    team2_relative_rating = team2_overall_rating / max(team1_overall_rating, team2_overall_rating)
                    # print('relative!!', team1_relative_rating, team2_relative_rating)

                    # TODO: Do we need this
                    # team1_random_factor = float(team_1['overall']) / 100.0 * random.random() + \
                    #                       (float(team_1['boost']) / 100.0)
                    #
                    # team2_random_factor = float(team_2['overall']) / 100.0 * random.random() + \
                    #                       (float(team_2['boost']) / 100.0)
                    #
                    # print('rand factor', team1_random_factor, team2_random_factor)

                    # midfield  = how many shots you get (attacks)
                    team1_attack = float(team_1['att']) / 100.0
                    team2_attack = float(team_2['att']) / 100.0
                    team1_midfield = float(team_1['mid']) / 100.0
                    team2_midfield = float(team_2['mid']) / 100.0
                    team1_defense = float(team_1['def']) / 100.0
                    team2_defense = float(team_2['def']) / 100.0

                    # How much better is team 1 vs team 2?
                    attack_diff_factor = math.fabs(team2_attack - team1_attack) * 2
                    team1_attack_boost_min = 0.5
                    team1_attack_boost_max = 1.0
                    team2_attack_boost_min = 0.5
                    team2_attack_boost_max = 1.0
                    if team1_attack > team2_attack:
                        team1_attack_boost_max = team1_attack_boost_max + attack_diff_factor
                        team1_attack_boost_min = team1_attack_boost_min - attack_diff_factor
                    elif team1_attack == team2_attack:
                        pass
                    else:
                        team2_attack_boost_max = team2_attack_boost_max + attack_diff_factor
                        team2_attack_boost_min = team2_attack_boost_min - attack_diff_factor

                    team_1_number_of_attacks = random.uniform((team1_attack + team1_midfield)/2.0, 1.0) * AVERAGE_SHOTS_PER_GAME * random.uniform(team1_attack_boost_min, team1_attack_boost_max)
                    team_2_number_of_attacks = random.uniform((team2_attack + team2_midfield)/2.0, 1.0) * AVERAGE_SHOTS_PER_GAME * random.uniform(team2_attack_boost_min, team2_attack_boost_max)
                    # team_2_number_of_attacks = float(team_1['att']) / 100.0 * float(team_2['mid']) / 100.0 * \
                    #                            random.uniform(0.25, 1.0) * AVERAGE_SHOTS_PER_GAME
                    team_1_number_of_attacks = int(round(team_1_number_of_attacks, 0))
                    team_2_number_of_attacks = int(round(team_2_number_of_attacks, 0))

                    # print('no of shots, attacks', round(team_1_number_of_attacks, 1), team_2_number_of_attacks)

                    for _ in range(team_1_number_of_attacks):
                        # attack = how many are on target, chance of scoring
                        team_1_chance_of_scoring = random.random() * team1_attack
                        team2_chance_of_defense = random.random() * team2_defense
                        if team_1_chance_of_scoring > team2_chance_of_defense:
                            team1_score += 1

                    for _ in range(team_2_number_of_attacks):
                        # attack = how many are on target, chance of scoring
                        team_2_chance_of_scoring = random.random() * team2_attack
                        team2_chance_of_defense = random.random() * team1_defense
                        if team_2_chance_of_scoring > team2_chance_of_defense:
                            team2_score += 1

                    # Additional goals, based on relative rating
                    team1_relative_rating = 1.0 - team1_relative_rating
                    team2_relative_rating = 1.0 - team2_relative_rating
                    if team1_relative_rating > team2_relative_rating:
                        # Team 1 better
                        team1_score = team1_score + (team1_relative_rating * random.random() * 100)
                        # print(team_1['name'], (team1_relative_rating * random.random() * 100))
                    elif team1_relative_rating < team2_relative_rating:
                        # Team 1 worse
                        team2_score = team2_score + (team2_relative_rating * random.random() * 100)
                        # print(team_2['name'], (team2_relative_rating * random.random() * 100))

                    total_goals = max(AVERAGE_GOALS_PER_GAME * random.uniform(0, 3) + ((team1_attack + team2_attack - team2_defense - team1_defense) * 10) - 2, 0)
                    total_goals = int(round(total_goals, 0))
                    if team1_score:
                        team1_score = int(team1_score / (team1_score + team2_score) * total_goals)
                    if team2_score:
                        team2_score = int(team2_score / (team1_score + team2_score) * total_goals)
                    team1_score = team1_score
                    # print('score', team1_score, team2_score, 'total goals', total_goals)

                    print(team_1['name'].capitalize(), ' ', team1_score, ' vs ', team_2['name'].capitalize(), ' ', team2_score)

                    # team_1_random_boost = random.random()  # 0 to 1
                    total_total_goals += total_goals
                    games += 1
        # print(groups)

        print(total_total_goals)
        print(games)
        print(total_total_goals/games)
        # Sort groups by points, then do 0th group A to play group B 1th,
        #   const leftSideWinner = runPlayoffs(mappedTeams.A[0], mappedTeams.B[1], mappedTeams.C[0], mappedTeams.D[1], mappedTeams.E[0], mappedTeams.F[1], mappedTeams.G[0], mappedTeams.H[1]);
        # const rightSideWinner = runPlayoffs(mappedTeams.B[0], mappedTeams.A[1], mappedTeams.D[0], mappedTeams.C[1], mappedTeams.F[0], mappedTeams.E[1], mappedTeams.H[0], mappedTeams.G[1]);


if __name__ == "__main__":
    wc = WorldCupper()
