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
        self.stdev = stdev
        self.regions = list(set(sagarins['Region']))
        self.n_sims = n_sims

    def matchup_odds(self, sag1, sag2, stdev):
        prob = norm.cdf(0, loc = sag2 - sag1, scale = stdev)
        return prob

    def sim_game(self, sag1, sag2):
        prob = self.matchup_odds(sag1, sag2, self.stdev)
        rand = random.random()
        return rand < prob

    def sim_64_round(self):
        sagarins = self.sagarins
        n_matchups = 64 // 8
        for region in self.regions:
            for i in range(n_matchups):
                seed1 = int(i + 1)
                seed2 = int(17 - seed1)

                condition1 = (sagarins['Region'] == region) & (sagarins['Seed'] == seed1)
                condition2 = (sagarins['Region'] == region) & (sagarins['Seed'] == seed2)

                indices1 = sagarins.index[condition1]
                indices2 = sagarins.index[condition2]

                sag1 = sagarins.loc[indices1, 'Sagarin rating'].iat[0]
                sag2 = sagarins.loc[indices2, 'Sagarin rating'].iat[0]

                outcome = self.sim_game(sag1, sag2)
                sagarins.loc[indices1, 'In'] = outcome
                sagarins.loc[indices2, 'In'] = not outcome
        
    def sim_midround(self):
        sagarins = self.sagarins
        ## Pick the correct matchup sets based on the round (how many teams remaining)
        set1 = [1,8,9,16]
        set2 = [2,7,10,15]
        set3 = [3,6,11,14]
        set4 = [4,5,12,13]

        if sum(sagarins['In']) == 32:
            sets = [set1, set2, set3, set4]
        elif sum(sagarins['In']) == 16:
            set1 = set1 + set4
            set2 = set2 + set3
            sets = [set1, set2]
        elif sum(sagarins['In']) == 8:
            sets = [set1 + set2 + set3 + set4]

        for region in self.regions:
            for seed_set in sets:
                condition = (sagarins['In']) & (sagarins['Region'] == region) & (sagarins['Seed'].isin(seed_set))
                indices = sagarins.index[condition]

                sag1 = sagarins.loc[indices, 'Sagarin rating'].iat[0]
                sag2 = sagarins.loc[indices, 'Sagarin rating'].iat[1]

                outcome = self.sim_game(sag1, sag2)
                sagarins.loc[indices[0], 'In'] = outcome
                sagarins.loc[indices[1], 'In'] = not outcome

    def sim_4_round(self):
        ## This one uses actual hard coded region names and matchups - not sure  if this is always consitant across years
        regions_match1 = ['East', 'South']
        regions_match2 = ['Midwest', 'West']
        regions_matchups = [regions_match1, regions_match2]

        for region_matchup in regions_matchups:
            condition = (sagarins['In']) & (sagarins['Region'].isin(region_matchup))
            indices = sagarins.index[condition]

            sag1 = sagarins.loc[indices, 'Sagarin rating'].iat[0]
            sag2 = sagarins.loc[indices, 'Sagarin rating'].iat[1]

            outcome = self.sim_game(sag1, sag2)
            sagarins.loc[indices[0], 'In'] = outcome
            sagarins.loc[indices[1], 'In'] = not outcome

    def sim_2_round(self):
        condition = (sagarins['In'])
        indices = sagarins.index[condition]

        sag1 = sagarins.loc[indices, 'Sagarin rating'].iat[0]
        sag2 = sagarins.loc[indices, 'Sagarin rating'].iat[1]

        outcome = self.sim_game(sag1, sag2)
        sagarins.loc[indices[0], 'In'] = outcome
        sagarins.loc[indices[1], 'In'] = not outcome
        
    def simulate_bracket(self):
        self.sagarins['In'] = True
        self.sim_64_round()
        self.sim_midround()
        self.sim_midround()
        self.sim_midround()
        self.sim_4_round()
        self.sim_2_round()

        ## Add simulation result to the results_df
        self.results_df.loc[self.sagarins['In'], 'Win%'] += 100/self.n_sims

    def run_simulations(self):
        for _ in range(self.n_sims):
            self.simulate_bracket()

        return self.results_df
    
if __name__ == '__main__':
    ## Set file directory as current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ## Load in sagarin ratings table
    sagarins = pd.read_csv('MM23_Sagarin.csv')
    n = 100
    stdev = 10
    sim = NCAA_simulation(sagarins, stdev = stdev, n_sims = n)

    cProfile.run('sim.run_simulations()', 'output.dat')

    with open("output_time.txt", 'w') as f:
        p = pstats.Stats("output.dat", stream = f)
        p.sort_stats("time").print_stats()