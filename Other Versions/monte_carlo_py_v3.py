## Monte Carlo Simulations for Analytics (per PK request)

import numpy as np
import pandas as pd
import random
import os
from scipy.stats import norm
import cProfile
import pstats

class NCAA_simulation:

    def __init__(self, sagarins, stdev = 10, n_sims = 100) -> None:
        self.results_df = sagarins.copy()
        self.results_df['Win%'] = 0
        self.sagarins = sagarins
        self.current_bracket = sagarins.copy()
        self.stdev = stdev
        self.regions = list(set(sagarins['Region']))
        self.n_sims = n_sims
        self.add_matchup_groups()

    def matchup_odds(self, sag1, sag2, stdev):
        prob = norm.cdf(0, loc = sag2 - sag1, scale = stdev)
        return prob

    def sim_game(self, sag1, sag2):
        prob = self.matchup_odds(sag1, sag2, self.stdev)
        rand = random.random()
        return rand < prob
    
    def add_matchup_groups(self):
        sagarins = self.sagarins
        sagarins['r64_group'] = 0
        sagarins['r32_group'] = 0       
        sagarins['r16_group'] = 0
        sagarins['r8_group'] = 0
        sagarins['r4_group'] = 0
        sagarins['r2_group'] = 0

        ## Add round of 64 groups
        n_matchups = 8
        matchup_sets = []

        for i in range(n_matchups):
            seed1 = int(i + 1)
            seed2 = int(17 - seed1)
            matchup_sets.append([seed1, seed2])

        for i, region in enumerate(self.regions):
            for j, matchup_set in enumerate(matchup_sets):
                group_num = i * n_matchups + j + 1
                sagarins.loc[(sagarins['Region'] == region) & (sagarins['Seed'].isin(matchup_set)), 'r64_group'] = group_num

        ## Add round of 32 groups
        n_matchups = 4
        set1 = [1,8,9,16]
        set2 = [2,7,10,15]
        set3 = [3,6,11,14]
        set4 = [4,5,12,13]
        matchup_sets = [set1, set2, set3, set4]

        for i, region in enumerate(self.regions):
            for j, matchup_set in enumerate(matchup_sets):
                group_num = i * n_matchups + j + 1
                sagarins.loc[(sagarins['Region'] == region) & (sagarins['Seed'].isin(matchup_set)), 'r32_group'] = group_num

        ## Add round of 16 groups
        n_matchups = 2
        set1 = set1 + set4
        set2 = set2 + set3
        matchup_sets = [set1, set2]

        for i, region in enumerate(self.regions):
            for j, matchup_set in enumerate(matchup_sets):
                group_num = i * n_matchups + j + 1
                sagarins.loc[(sagarins['Region'] == region) & (sagarins['Seed'].isin(matchup_set)), 'r16_group'] = group_num

        ## Add round of 8 groups
        n_matchups = 1
        matchup_sets = [set1 + set2 + set3 + set4]

        for i, region in enumerate(self.regions):
            for j, matchup_set in enumerate(matchup_sets):
                group_num = i * n_matchups + j + 1
                sagarins.loc[(sagarins['Region'] == region) & (sagarins['Seed'].isin(matchup_set)), 'r8_group'] = group_num

        ## Add round of 4 groups
        sagarins.loc[sagarins['Region'] == 'South', 'r4_group'] = 1
        sagarins.loc[sagarins['Region'] == 'East', 'r4_group'] = 1
        sagarins.loc[sagarins['Region'] == 'West', 'r4_group'] = 2
        sagarins.loc[sagarins['Region'] == 'Midwest', 'r4_group'] = 2

    def sim_logic(self, group):
        if len(group) == 2:
            sag1, sag2 = group['Sagarin rating'].iloc[:2].values
            outcome = self.sim_game(sag1, sag2)
            group['In'] = [outcome, not outcome]
        return group

    def sim_round(self):
        sagarins = self.current_bracket

        rem_teams = sum(sagarins['In'])
        col_name = f'r{rem_teams}_group'

        sagarins = sagarins.groupby(col_name).apply(self.sim_logic)
        self.current_bracket = sagarins[sagarins['In']]
        
    def simulate_bracket(self):
        self.sagarins['In'] = True
        self.current_bracket = self.sagarins.copy()
        for _ in range(6):
            self.sim_round()

        ## Add simulation result to the results_df
        winner = self.current_bracket.loc[self.current_bracket['In'], 'Team'].iat[0]
        self.results_df.loc[self.results_df['Team'] == winner, 'Win%'] += 100/self.n_sims

    def run_simulations(self):
        self.add_matchup_groups()
        for _ in range(self.n_sims):
            self.simulate_bracket()

        return self.results_df
    
if __name__ == '__main__':
    ## Set file directory as current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ## Load in sagarin ratings table
    sagarins = pd.read_csv('MM23_Sagarin.csv')
    n = 1000
    stdev = 10
    sim = NCAA_simulation(sagarins, stdev = stdev, n_sims = n)
    simulation_results = sim.run_simulations()
    simulation_results.to_csv(f'NCAA_2023_n{n}_stdev{stdev}_results.csv', index =  False)
    
    '''
    cProfile.run('sim.run_simulations()', 'output.dat')

    with open("output_time.txt", 'w') as f:
        p = pstats.Stats("output.dat", stream = f)
        p.sort_stats("time").print_stats()
    '''