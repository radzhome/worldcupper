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


AVERAGE_GOALS_PER_GAME = 2.6
AVERAGE_SHOTS_PER_GAME = 20  # Per team, shots on target about 50%. Attack and midfield + some random boost
EXTRA_ATTACK_RATIO = 15  # For better team


class WorldCupper(object):

    def __init__(self, filename='worldcupper.csv'):
        self.groups = {}  # Team groups in WC

        with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                row['goals_for'] = 0
                row['goals_against'] = 0
                row['goals_diff'] = 0
                row['games_won'] = 0
                row['games_lost'] = 0
                row['games_tied'] = 0
                row['points'] = 0
                self.groups.setdefault(row['group'], []).append(row)

        self.total_group_goals = 0
        self.games = 0
        self.total_knockout_goals = 0

    def run_group_stage(self):
        # Run group stage

        groups = OrderedDict(sorted(self.groups.items()))
        for group_name, group_teams in groups.items():
            for i, team1 in enumerate(group_teams):
                for team2 in group_teams[i+1:]:
                    team1_score, team2_score, total_goals = self.run_match(team1, team2)
                    self.games += 1
                    self.total_group_goals += total_goals
                    team1['goals_for'] += team1_score
                    team2['goals_for'] += team2_score
                    team1['goals_against'] += team2_score
                    team2['goals_against'] += team1_score
                    team1['goals_diff'] += team1_score - team2_score
                    team2['goals_diff'] += team2_score - team1_score
                    if team1_score > team2_score:
                        team1['games_won'] += 1
                        team1['points'] += 3
                        team2['games_lost'] += 1
                    elif team1_score == team2_score:
                        team1['games_tied'] += 1
                        team2['games_tied'] += 1
                        team1['points'] += 1
                        team2['points'] += 1
                    elif team1_score < team2_score:
                        team2['games_won'] += 1
                        team1['games_lost'] += 1
                        team2['points'] += 3
                    # print('score', team1_score, team2_score, 'total goals', total_goals)
                    print(team1['name'].capitalize(), ' ', team1_score, ' vs ', team2['name'].capitalize(), ' ',
                          team2_score)

        # Summary of groups
        print('total goals in ', self.games, ' games ', self.total_group_goals)
        print('goals per game ', self.total_group_goals/self.games)

        for group_name, group_teams in groups.items():
            print('team, points, games won, games lost, games tied, goals for, goals against, goal diff')
            # group_teams = sorted(group_teams, key=lambda k: k['points'], reverse=True)
            # Sort groups by points,
            group_teams = sorted(group_teams, key=lambda k: (k['points'], k['goals_diff']), reverse=True)

            for i, team in enumerate(group_teams):
                print(team['name'], team['points'], team['games_won'], team['games_lost'], team['games_tied'],
                      team['goals_for'], team['goals_against'], team['goals_diff'])
            print('')

        # TODO
        # print(groups['a'][0])
        # print(groups['b'][1])
        # print(self.run_match(groups['a'][0], groups['b'][1])) # team1_score, team2_score, total_goals
        # run_playoffs, right vs left side winnters
        # Team 1 vs team 2, team 3 vs team 4, team 5 vs team 6, team 7 vs team 8
        # winner team1,2, winner of team3,4, winner of team5,6, winner of team7,8
        # winner of team 1,2,34, winner of team 5,6,7,8
        # winner
        left_side_teams = groups['a'][0], groups['b'][1], groups['c'][0], groups['d'][1], groups['e'][0],\
                          groups['f'][1], groups['g'][0], groups['h'][1]
        right_side_teams = groups['b'][0], groups['a'][1], groups['d'][0], groups['c'][1], groups['f'][0],\
                          groups['e'][1], groups['h'][0], groups['g'][1]

    def attack(self, team_attack, team_overall, number_of_attacks, other_team_defense):
        """
        Get team score on attack
        :param team_attack:
        :param team_overall:
        :param number_of_attacks:
        :param other_team_defense:
        :return:
        """
        team_score = 0
        for _ in range(number_of_attacks):
            # attack = how many are on target, chance of scoring
            chance_of_scoring = random.random() * team_attack * team_overall
            # defense = how many go in
            chance_of_defense = random.random() * other_team_defense * team_overall
            # print(chance_of_scoring, chance_of_defense, 'attack ', team_attack, 'other team def', other_team_defense)

            if chance_of_scoring > chance_of_defense:
                team_score += 1
        return team_score

    def get_total_goals(self, team1_attack, team2_attack, team1_defense, team2_defense):
        total_goals = max(AVERAGE_GOALS_PER_GAME * random.uniform(0, 3) + (
                (team1_attack + team2_attack - team1_defense - team2_defense) * 10) - 2, 0)
        return total_goals

    def normalize_goals(self, team1_score, team2_score, team1_attack, team2_attack, team1_defense, team2_defense,
                        total_goals=None):
        """
        Normalize match goals
        :param team1_score:
        :param team2_score:
        :param team1_attack:
        :param team2_attack:
        :param team1_defense:
        :param team2_defense:
        :param total_goals:
        :return:
        """
        if not total_goals:
            # CForce total_goals to be > 0 if the diff b/w team1_score & team2_score is high
            total_goals = self.get_total_goals(team1_attack, team2_attack, team1_defense, team2_defense)
            if not total_goals and math.fabs(team1_score - team2_score) > 4:
                total_goals = self.get_total_goals(team1_attack, team2_attack, team1_defense, team2_defense)

        total_goals = int(round(total_goals, 0))
        team1_new_score = team2_new_score = 0
        if team1_score:
            team1_new_score = int(round(team1_score / (team1_score + team2_score) * total_goals, 0))
        if team2_score:
            team2_new_score = int(round(team2_score / (team1_score + team2_score) * total_goals, 0))
        return team1_new_score, team2_new_score, total_goals

    def run_match(self, team1, team2, do_penalties=False):
        """
        Run a match simulation
        :param team1:
        :param team2:
        :param do_penalties:
        :return:
        """
        # Lower is better. FIFA rating is not as significant.
        team1_overall_rating = float(float(team1['fifa_rating']) / 2.0) + float(team1['elo_rating']) + \
                               float(team1['goalimpact_rating']) + (5 - float(team1['ea_fifa_18_rating']))
        team2_overall_rating = float(float(team1['fifa_rating']) / 2.0) + float(team2['elo_rating']) + \
                               float(team2['goalimpact_rating']) + (5 - float(team2['ea_fifa_18_rating']))

        # print('overall', team1_overall_rating, team2_overall_rating)

        team1_relative_rating = team1_overall_rating / max(team1_overall_rating, team2_overall_rating)
        team2_relative_rating = team2_overall_rating / max(team1_overall_rating, team2_overall_rating)
        team1_relative_rating = 1.0 - team1_relative_rating
        team2_relative_rating = 1.0 - team2_relative_rating
        # print('relative!!', team1_relative_rating, team2_relative_rating)

        # TODO: Do we need this?
        # team1_random_factor = float(team1['overall']) / 100.0 * random.random() + \
        #                       (float(team1['boost']) / 100.0)
        # team2_random_factor = float(team2['overall']) / 100.0 * random.random() + \
        #                       (float(team2['boost']) / 100.0)
        # print('rand factor', team1_random_factor, team2_random_factor)

        # midfield  = how many shots you get (attacks)
        team1_attack = float(team1['att']) / 100.0
        team2_attack = float(team2['att']) / 100.0
        team1_midfield = float(team1['mid']) / 100.0
        team2_midfield = float(team2['mid']) / 100.0
        team1_defense = float(team1['def']) / 100.0
        team2_defense = float(team2['def']) / 100.0
        team1_overall = float(team1['overall']) / 100.0
        team2_overall = float(team2['overall']) / 100.0
        # print(team1['name'], team1_attack, team1_midfield, team1_defense, team1_overall, team2['name'], team2_attack, team2_midfield, team2_defense,
        #       team2_overall)

        # How much better is team 1 vs team 2?
        attack_diff_factor = math.fabs(team2_attack - team1_attack) * 2
        team1_attack_boost_min = 0.5
        team1_attack_boost_max = 1.0
        team2_attack_boost_min = 0.5
        team2_attack_boost_max = 1.0
        if team1_attack > team2_attack:
            team1_attack_boost_max = team1_attack_boost_max + attack_diff_factor
            team1_attack_boost_min = team1_attack_boost_min - attack_diff_factor
        elif team1_attack < team2_attack:
            team2_attack_boost_max = team2_attack_boost_max + attack_diff_factor
            team2_attack_boost_min = team2_attack_boost_min - attack_diff_factor

        team1_number_of_attacks = random.uniform((team1_attack + team1_midfield) / 2.0,
                                                 1.0) * AVERAGE_SHOTS_PER_GAME * random.uniform(
            team1_attack_boost_min, team1_attack_boost_max)
        team2_number_of_attacks = random.uniform((team2_attack + team2_midfield) / 2.0,
                                                 1.0) * AVERAGE_SHOTS_PER_GAME * random.uniform(
            team2_attack_boost_min, team2_attack_boost_max)
        # team2_number_of_attacks = float(team1['att']) / 100.0 * float(team2['mid']) / 100.0 * \
        #                            random.uniform(0.25, 1.0) * AVERAGE_SHOTS_PER_GAME
        team1_number_of_attacks = int(round(team1_number_of_attacks, 0))
        team2_number_of_attacks = int(round(team2_number_of_attacks, 0))

        # print('no of shots/attacks', round(team1_number_of_attacks, 1), team2_number_of_attacks)

        # print('attack for ', team1['name'])
        team1_score = self.attack(team1_attack, team1_overall, team1_number_of_attacks, team2_defense)
        # print('attack for ', team2['name'])
        team2_score = self.attack(team2_attack, team2_overall, team2_number_of_attacks, team1_defense)
        # print(team1_score, team2_score)

        # Additional goals, based on relative rating
        # print('relative is', team1['name'], team1_relative_rating, team2['name'], team2_relative_rating)
        if team1_relative_rating > team2_relative_rating:
            # Team 1 better, lower is better
            # team1_score = team1_score + (team1_relative_rating * random.random() * 100)
            team1_extra_attacks = int(round(team1_relative_rating * random.random() * EXTRA_ATTACK_RATIO, 0))
            # print('team1 better', team1['name'], team1_extra_attacks)
            team1_score += self.attack(team1_attack, team1_overall, team1_extra_attacks, team2_defense)
        elif team1_relative_rating < team2_relative_rating:
            # Team 2 better, lower is better
            # team2_score = team2_score + (team2_relative_rating * random.random() * 100)
            team2_extra_attacks = int(round(team2_relative_rating * random.random() * EXTRA_ATTACK_RATIO, 0))
            # print('team2 better', team2['name'], team2_extra_attacks)
            team2_score += self.attack(team2_attack, team2_overall, team2_extra_attacks, team1_defense)

        # print(team1['name'], team1_score, team2['name'], team2_score)
        # # Normalize goals
        # total_goals = max(AVERAGE_GOALS_PER_GAME * random.uniform(0, 3) + (
        #             (team1_attack + team2_attack - team2_defense - team1_defense) * 10) - 2, 0)
        # total_goals = int(round(total_goals, 0))
        # if team1_score:
        #     team1_score = int(team1_score / (team1_score + team2_score) * total_goals)
        # if team2_score:
        #     team2_score = int(team2_score / (team1_score + team2_score) * total_goals)
        # print('hello')
        # print(team1_score, team2_score, team1_attack, team2_attack, team1_defense, team2_defense)
        # print('done'); input()
        team1_score, team2_score, total_goals = self.normalize_goals(team1_score, team2_score, team1_attack,
                                                                     team2_attack, team1_defense, team2_defense)
        # Penalties if applicable
        if team1_score == team2_score and do_penalties:
            team1_penalties = 0
            team2_penalties = 0
            penalties_taken = 0
            while team1_penalties == team2_penalties or penalties_taken < 5:
                team1_penalties += self.attack(team1_attack, team1_overall, 1, team2_defense)
                team2_penalties += self.attack(team2_attack, team2_overall, 1, team1_defense)
                penalties_taken += 1
            if team1_penalties > team2_penalties:
                team1_score += 1
            else:
                team2_score += 1

        return team1_score, team2_score, total_goals


if __name__ == "__main__":
    wc = WorldCupper()
    wc.run_group_stage()
    # print(wc.normalize_goals(7, 8, 0.86, 0.84, 0.85, 0.81, 2))
