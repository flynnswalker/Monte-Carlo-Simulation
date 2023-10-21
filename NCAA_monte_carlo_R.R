## NCAA Monte Carlo Work in R

## access the NCAA_function.R file to get relevant function
source("NCAA_functions.R")

## Load in teams/sagarin ratings
sagarins <- read.csv("MM23_Sagarin.csv")
stdev = 10
n_simulations = 1000

## Run the simulations
sim_results = aggregate_simulations(sagarins, n_simulations, stdev)
View(sim_results)

## Save the results to a csv
write.csv(sim_results, 'simluation_results_R.csv', row.names = FALSE)
