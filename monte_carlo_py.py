## Monte Carlo Simulations for Analytics (per PK request)

import numpy as np
import pandas as pd
import random
import os
from scipy.stats import norm
import cProfile
import pstats
from multiprocessing import Process

class NCAA_simulation:

    def __init__(self, sagarins, stdev, n) -> None:
        self.sagarins = sagarins
        self.stdev = stdev
        self.num_sims = n
        self.winners = []
        self.round_64_matchups = None

    def matchup_odds(self, sag1, sag2):
        prob = norm.cdf(0, loc = sag2 - sag1, scale = self.stdev)
        return prob

    def sim_game(self, sag1, sag2):
        prob = self.matchup_odds(sag1, sag2)
        rand = random.random()
        return rand < prob

    def sim_round(self, matchups_df):
        winners = []
        for i, row in matchups_df.iterrows():
            sag1 = row['Sagarin rating1']
            sag2 = row['Sagarin rating2']
            outcome = self.sim_game(sag1, sag2)
            if outcome:
                team = row['Team1']
                seed = row['Seed1']
                sag = sag1
            else:
                team = row['Team2']
                seed = row['Seed2']
                sag = sag2

            if 'Region' in matchups_df.columns:
                region = row['Region']
                winner_dict = {'Region' : region, 'Seed' : seed, 'Team' : team, 'Sagarin rating' : sag}

            else:
                winner_dict = {'Seed' : seed, 'Team' : team, 'Sagarin rating' : sag}

            winners.append(winner_dict)

        winner_df = pd.DataFrame(winners)
        return winner_df

    def generate_round_64_matchups(self, teams_df):
        n_matchups = len(teams_df) // 8
        matchups = []
        regions = list(set(teams_df['Region']))
        for region in regions:
            tdf = teams_df[teams_df['Region'] == region]
            for i in range(n_matchups):
                seed1 = int(i + 1)
                seed2 = int(17 - seed1)

                team1 = tdf.loc[tdf['Seed'] == seed1, 'Team'].iat[0]
                sag1 = tdf.loc[tdf['Seed'] == seed1, 'Sagarin rating'].iat[0]
                team2 = tdf.loc[tdf['Seed'] == seed2, 'Team'].iat[0]
                sag2 = tdf.loc[tdf['Seed'] == seed2, 'Sagarin rating'].iat[0]
                matchup_dict = {'Region' : region, 'Seed1' : seed1, 'Team1' : team1, 'Sagarin rating1' : sag1, 'Seed2' : seed2, 'Team2' : team2, 'Sagarin rating2' : sag2}
                matchups.append(matchup_dict)

        matchup_df = pd.DataFrame(matchups)
        self.round_64_matchups = matchup_df

    def generate_midround_matchups(self, teams_df):
        regions = list(set(teams_df['Region']))
        matchups = []

        ## Pick the correct matchup sets based on the round (how many teams remaining)
        set1 = [1,8,9,16]
        set2 = [2,7,10,15]
        set3 = [3,6,11,14]
        set4 = [4,5,12,13]

        if len(teams_df) == 32:
            sets = [set1, set2, set3, set4]
        elif len(teams_df) == 16:
            set1 = set1 + set4
            set2 = set2 + set3
            sets = [set1, set2]
        elif len(teams_df) == 8:
            sets = [set1 + set2 + set3 + set4]

        for seed_set in sets:
            tdf = teams_df[teams_df['Seed'].isin(seed_set)]
            for region in regions:
                tdf1 = tdf.loc[tdf['Region'] == region]

                team1 = tdf1['Team'].iat[0]
                sag1 = tdf1['Sagarin rating'].iat[0]
                seed1 = tdf1['Seed'].iat[0]
                team2 = tdf1['Team'].iat[1]
                sag2 = tdf1['Sagarin rating'].iat[1]
                seed2 = tdf1['Seed'].iat[1]
                matchup_dict = {'Region' : region, 'Seed1' : seed1, 'Team1' : team1, 'Sagarin rating1' : sag1, 'Seed2' : seed2, 'Team2' : team2, 'Sagarin rating2' : sag2}
                matchups.append(matchup_dict)
                            
        matchup_df = pd.DataFrame(matchups)
        return matchup_df

    def generate_round_4_matchups(self, teams_df):
        ## This one uses actual hard coded region names and matchups - not sure  if this is always consitant across years
        regions_match1 = ['East', 'South']
        regions_match2 = ['Midwest', 'West']
        regions_matchups = [regions_match1, regions_match2]
        matchups = []

        for region_set in regions_matchups:
            tdf1 = teams_df[teams_df['Region'].isin(region_set)]

            team1 = tdf1['Team'].iat[0]
            sag1 = tdf1['Sagarin rating'].iat[0]
            seed1 = tdf1['Seed'].iat[0]
            team2 = tdf1['Team'].iat[1]
            sag2 = tdf1['Sagarin rating'].iat[1]
            seed2 = tdf1['Seed'].iat[1]
            matchup_dict = {'Seed1' : seed1, 'Team1' : team1, 'Sagarin rating1' : sag1, 'Seed2' : seed2, 'Team2' : team2, 'Sagarin rating2' : sag2}
            matchups.append(matchup_dict)

        matchup_df = pd.DataFrame(matchups)
        return matchup_df

    def generate_round_2_matchup(self, teams_df):
        team1 = teams_df['Team'].iat[0]
        sag1 = teams_df['Sagarin rating'].iat[0]
        seed1 = teams_df['Seed'].iat[0]
        team2 = teams_df['Team'].iat[1]
        sag2 = teams_df['Sagarin rating'].iat[1]
        seed2 = teams_df['Seed'].iat[1]
        matchup_dict = {'Seed1' : seed1, 'Team1' : team1, 'Sagarin rating1' : sag1, 'Seed2' : seed2, 'Team2' : team2, 'Sagarin rating2' : sag2}

        matchup_df = pd.DataFrame([matchup_dict])
        return matchup_df

    def simulate_bracket(self):
        round_32_teams = self.sim_round(self.round_64_matchups)
        matchups_df = self.generate_midround_matchups(round_32_teams)
        round_16_teams = self.sim_round(matchups_df)
        matchups_df = self.generate_midround_matchups(round_16_teams)
        round_8_teams = self.sim_round(matchups_df)
        matchups_df = self.generate_midround_matchups(round_8_teams)
        round_4_teams = self.sim_round(matchups_df)
        matchups_df = self.generate_round_4_matchups(round_4_teams)
        round_2_teams = self.sim_round(matchups_df)
        matchups_df = self.generate_round_2_matchup(round_2_teams)
        winner = self.sim_round(matchups_df)
        self.winners.append(winner['Team'][0])

    def aggregate_simulations(self):
        sagarins = self.sagarins
        self.generate_round_64_matchups(sagarins)

        for _ in range(self.num_sims):
            self.simulate_bracket()

        sagarins['Win%'] = 0
        for winner in self.winners:
            sagarins.loc[sagarins['Team'] == winner, 'Win%'] += 100/n

        return sagarins

if __name__ == '__main__':
    ## Set file directory as current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ## Load in sagarin ratings table
    sagarins = pd.read_csv('MM23_Sagarin.csv')
    n = 1000
    stdev = 10
    sim = NCAA_simulation(sagarins, stdev, n)
    simulation_results = sim.aggregate_simulations()
    simulation_results.to_csv(f'NCAA_2023_n{n}_stdev{stdev}_results_1.csv', index =  False)

    '''
    # Create a cProfile object and run the function
    profiler = cProfile.Profile()
    profiler.enable()
    simulation_results = aggregate_simulations(sagarins, n, stdev)
    profiler.disable()
    cProfile.run('aggregate_simulations(sagarins, n, stdev)')

    # Set profile results file name
    output_file = "profiling_results.txt"

    # Write the profiling results to a text file
    with open(output_file, 'w') as file:
        stats = pstats.Stats(profiler, stream=file)
        stats.sort_stats('cumulative')
        stats.print_stats()
    '''


