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
import copy
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
                row['name'] = row['name'].capitalize()
                self.groups.setdefault(row['group'], []).append(row)

        self.total_group_goals = 0
        self.games = 0
        self.total_knockout_goals = 0

    def run_group_stage(self):
        # Run group stage

        self.groups = OrderedDict(sorted(self.groups.items()))
        for group_name, group_teams in self.groups.items():
            for i, team1 in enumerate(group_teams):
                for team2 in group_teams[i+1:]:
                    team1_score, team2_score, total_goals, _ = self.run_match(team1, team2)
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
                    
                    print(team1['name'], ' ', team1_score, ' vs ', team2['name'], ' ',
                          team2_score)

        # Summary of groups
        print('total goals in ', self.games, ' games ', self.total_group_goals)
        print('goals per game ', self.total_group_goals/self.games)

        for group_name, group_teams in self.groups.items():
            print('Group {}'.format(group_name))
            print('team, points, games won, games lost, games tied, goals for, goals against, goal diff')
            # group_teams = sorted(group_teams, key=lambda k: k['points'], reverse=True)
            # Sort groups by points,
            group_teams = sorted(group_teams, key=lambda k: (k['points'], k['goals_diff']), reverse=True)

            for i, team in enumerate(group_teams):
                print(team['name'], team['points'], team['games_won'], team['games_lost'], team['games_tied'],
                      team['goals_for'], team['goals_against'], team['goals_diff'])
            print('')

    def run_round(self, current_round_matches):
        current_round_matches = copy.deepcopy(current_round_matches)
        next_round_matches = []
        next_match = []
        round_total_goals = 0
        for i, match_teams in enumerate(current_round_matches):
            team1_score, team2_score, total_goals, winning_team = self.run_match(match_teams[0], match_teams[1],
                                                                                 do_penalties=True)
            # Save scores in original dict
            match_teams[0]['score'] = team1_score
            match_teams[1]['score'] = team2_score

            round_total_goals += total_goals
            # print(match_teams[0]['name'], match_teams[0]['score'], match_teams[1]['name'], match_teams[1]['score'])

            # winning_team['score'] = None
            next_match.append(winning_team)
            if i % 2:
                next_round_matches.append(next_match)
                next_match = []

        # Single winner edge case for round of 2 teams (final)
        final_winner = None
        if not next_round_matches:
            final_winner = next_match[0]

        return next_round_matches, current_round_matches, final_winner, round_total_goals

    def run_knockout_stage(self):
        groups = self.groups
        # Final 16 teams
        final_16_matches = [
            [groups['a'][0], groups['b'][1]], [groups['c'][0], groups['d'][1]],
            [groups['e'][0], groups['f'][1]], [groups['g'][0], groups['h'][1]],
            [groups['b'][0], groups['a'][1]], [groups['d'][0], groups['c'][1]],
            [groups['f'][0], groups['e'][1]], [groups['h'][0], groups['g'][1]]
        ]

        # Final 16
        # print('')
        # print("Final 16")
        quarter_final_matches, final_16_matches, _, total_goals = self.run_round(final_16_matches)
        self.total_knockout_goals += total_goals

        # Semi finals
        # print('')
        # print("Semi Finals")
        semi_final_matches, quarter_final_matches, _, total_goals = self.run_round(quarter_final_matches)
        self.total_knockout_goals += total_goals

        # Quarter finals
        # print('')
        # print("Quarter Finals")
        final_match, semi_final_matches, _, total_goals = self.run_round(semi_final_matches)
        self.total_knockout_goals += total_goals

        # Final
        # print('')
        # print("Final")
        _, final_match, winner, total_goals = self.run_round(final_match)
        self.total_knockout_goals += total_goals

        # Winner
        # print('')
        # print("WC Winner: {}".format(winner['name']))

        self.draw_knockout_table(final_16_matches, quarter_final_matches, semi_final_matches, final_match, winner)

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

        # TODO: Man not need random factor
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

        winning_team = None
        if team1_score > team2_score:
            winning_team = team1
        elif team2_score > team1_score:
            winning_team = team2

        # TODO: Return penalties scored if applicable
        return team1_score, team2_score, total_goals, winning_team

    def draw_knockout_table(self, final_16_matches, quarter_final_matches, semi_final_matches, final_match, winner):
        args = []
        for match in final_16_matches + quarter_final_matches + semi_final_matches + final_match:
            args.append(match[0]['name'] + ' ' + str(match[0]['score']))
            args.append(match[1]['name'] + ' ' + str(match[1]['score']))

        args.append(winner['name'])

        table = ("\n"
                 "Left:\n"
                 "{0}\n"
                 "{1}\n"
                 "      {16}\n"
                 "      {17}\n"
                 "{2}\n"
                 "          {24}\n"
                 "{3}\n"
                 "                  {28}\n"
                 "{4}\n"
                 "{5}\n"
                 "          {25}\n"
                 "      {18}\n"
                 "      {19}\n"
                 "{6}\n"
                 "{7}\n"
                 "                           {30}\n"
                 "Right:\n"
                 "{8}\n"
                 "{9}\n"
                 "      {20}\n"
                 "      {21}\n"
                 "{10}\n"
                 "          {26}\n"
                 "{11}\n"
                 "                  {29}\n"
                 "{12}\n"
                 "{13}\n"
                 "          {27}\n"
                 "      {22}\n"
                 "      {23}\n"
                 "{14}\n"
                 "{15}\n").format(*args)

        print(table)


if __name__ == "__main__":
    wc = WorldCupper()
    wc.run_group_stage()
    wc.run_knockout_stage()
