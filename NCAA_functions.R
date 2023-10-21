## Functions needed for NCAA monte carlo simulation
sagarin_matchup_odds <- function(sag1, sag2, stdev) {
  prob <- pnorm(0, mean = sag2 - sag1, sd = stdev)
  return(prob)
}

sim_game <- function(sag1, sag2, stdev) {
  prob <- sagarin_matchup_odds(sag1, sag2, stdev)
  rand <- runif(1)  # Generate a random number between 0 and 1
  return(rand < prob)
}

sim_round <- function(matchups_df, stdev = 10) {
  winners <- data.frame()
  if ('Region' %in% colnames(matchups_df)) {
    for (i in 1:nrow(matchups_df)) {
      sag1 <- matchups_df$`Sagarin.rating1`[i]
      sag2 <- matchups_df$`Sagarin.rating2`[i]
      outcome <- sim_game(sag1, sag2, stdev)
      if (outcome) {
        team <- matchups_df$Team1[i]
        seed <- matchups_df$Seed1[i]
        sag <- sag1
      } else {
        team <- matchups_df$Team2[i]
        seed <- matchups_df$Seed2[i]
        sag <- sag2
      }
      region <- matchups_df$Region[i]
      winner_data <- data.frame(
        Region = region,
        Seed = seed,
        Team = team,
        `Sagarin.rating` = sag,
        stringsAsFactors = FALSE
      )
      winners <- rbind(winners, winner_data)
    }
  } else {
    for (i in 1:nrow(matchups_df)) {
      sag1 <- matchups_df$`Sagarin.rating1`[i]
      sag2 <- matchups_df$`Sagarin.rating2`[i]
      outcome <- sim_game(sag1, sag2, stdev)
      if (outcome) {
        team <- matchups_df$Team1[i]
        seed <- matchups_df$Seed1[i]
        sag <- sag1
      } else {
        team <- matchups_df$Team2[i]
        seed <- matchups_df$Seed2[i]
        sag <- sag2
      }
      winner_data <- data.frame(
        Seed = seed,
        Team = team,
        `Sagarin.rating` = sag,
        stringsAsFactors = FALSE
      )
      winners <- rbind(winners, winner_data)
    }
  }
  return(winners)
}

generate_round_64_matchups <- function(teams_df) {
  n_matchups <- nrow(teams_df) %/% 8
  matchups <- data.frame()
  regions <- unique(teams_df$Region)
  
  for (region in regions) {
    tdf <- teams_df[teams_df$Region == region, ]
    for (i in 1:n_matchups) {
      seed1 <- i
      seed2 <- 17 - seed1
      
      team1 <- tdf$Team[tdf$Seed == seed1]
      sag1 <- tdf$`Sagarin.rating`[tdf$Seed == seed1]
      team2 <- tdf$Team[tdf$Seed == seed2]
      sag2 <- tdf$`Sagarin.rating`[tdf$Seed == seed2]

      matchup_data <- data.frame(
        Region = region,
        Seed1 = seed1,
        Team1 = team1,
        `Sagarin.rating1` = sag1,
        Seed2 = seed2,
        Team2 = team2,
        `Sagarin.rating2` = sag2
      )
      # Append the matchup data frame to the main matchups DataFrame
      matchups <- rbind(matchups, matchup_data)
    }
  }
  
  return(matchups)
}

generate_midround_matchups <- function(teams_df) {
  regions <- unique(teams_df$Region)
  matchups <- data.frame()
  
  # Define the matchup sets based on the round (how many teams remaining)
  set1 <- c(1, 8, 9, 16)
  set2 <- c(2, 7, 10, 15)
  set3 <- c(3, 6, 11, 14)
  set4 <- c(4, 5, 12, 13)
  
  if (nrow(teams_df) == 32) {
    sets <- list(set1, set2, set3, set4)
  } else if (nrow(teams_df) == 16) {
    set1 <- c(set1, set4)
    set2 <- c(set2, set3)
    sets <- list(set1, set2)
  } else if (nrow(teams_df) == 8) {
    sets <- list(c(set1, set2, set3, set4))
  }
  
  for (seed_set in sets) {
    tdf <- teams_df[teams_df$Seed %in% seed_set, ]
    for (region in regions) {
      tdf1 <- tdf[tdf$Region == region, ]
      
      team1 <- tdf1$Team[1]
      sag1 <- tdf1$`Sagarin.rating`[1]
      seed1 <- tdf1$Seed[1]
      team2 <- tdf1$Team[2]
      sag2 <- tdf1$`Sagarin.rating`[2]
      seed2 <- tdf1$Seed[2]
      
      matchup_data <- data.frame(
        Region = region,
        Seed1 = seed1,
        Team1 = team1,
        `Sagarin.rating1` = sag1,
        Seed2 = seed2,
        Team2 = team2,
        `Sagarin.rating2` = sag2
      )
      matchups <- rbind(matchups, matchup_data)
    }
  }
  
  return(matchups)
}

generate_round_4_matchups <- function(teams_df) {
  # Define the hard-coded region names and matchups
  regions_match1 <- c('East', 'South')
  regions_match2 <- c('Midwest', 'West')
  regions_matchups <- list(regions_match1, regions_match2)
  matchups <- data.frame()
  
  for (region_set in regions_matchups) {
    tdf1 <- teams_df[teams_df$Region %in% region_set, ]
    
    team1 <- tdf1$Team[1]
    sag1 <- tdf1$`Sagarin.rating`[1]
    seed1 <- tdf1$Seed[1]
    team2 <- tdf1$Team[2]
    sag2 <- tdf1$`Sagarin.rating`[2]
    seed2 <- tdf1$Seed[2]
    
    matchup_data <- data.frame(
      Seed1 = seed1,
      Team1 = team1,
      `Sagarin.rating1` = sag1,
      Seed2 = seed2,
      Team2 = team2,
      `Sagarin.rating2` = sag2
    )
    matchups <- rbind(matchups, matchup_data)
  }
  
  return(matchups)
}

  generate_round_2_matchup <- function(teams_df) {
    team1 <- teams_df$Team[1]
    sag1 <- teams_df$`Sagarin.rating`[1]
    seed1 <- teams_df$Seed[1]
    team2 <- teams_df$Team[2]
    sag2 <- teams_df$`Sagarin.rating`[2]
    seed2 <- teams_df$Seed[2]
    
    matchup_data <- data.frame(
      Seed1 = seed1,
      Team1 = team1,
      `Sagarin.rating1` = sag1,
      Seed2 = seed2,
      Team2 = team2,
      `Sagarin.rating2` = sag2,
      stringsAsFactors = FALSE
    )
    
    return(matchup_data)
  }
  
  simulate_bracket <- function(matchups_df, stdev = 10) {
    round_32_teams <- sim_round(matchups_df, stdev)
    matchups_df <- generate_midround_matchups(round_32_teams)
    round_16_teams <- sim_round(matchups_df, stdev)
    matchups_df <- generate_midround_matchups(round_16_teams)
    round_8_teams <- sim_round(matchups_df, stdev)
    matchups_df <- generate_midround_matchups(round_8_teams)
    round_4_teams <- sim_round(matchups_df, stdev)
    matchups_df <- generate_round_4_matchups(round_4_teams)
    round_2_teams <- sim_round(matchups_df, stdev)
    matchups_df <- generate_round_2_matchup(round_2_teams)
    winner <- sim_round(matchups_df, stdev)
    
    return(winner)
  }
  
  aggregate_simulations <- function(sagarins, n = 1000, stdev = 10) {
    winners <- character(0)
    round_64_matchups <- generate_round_64_matchups(sagarins)
    
    for (i in 1:n) {
      outcome <- simulate_bracket(round_64_matchups, stdev)
      winners <- c(winners, outcome$Team[1])
    }
    
    sagarins$`Win%` <- 0
    for (winner in winners) {
      sagarins[sagarins$Team == winner, 'Win%'] <- sagarins[sagarins$Team == winner, 'Win%'] + (100 / n)
    }
    
    return(sagarins)
  }