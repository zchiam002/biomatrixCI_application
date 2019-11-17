##This function tries to solve the scheduling problem presented in https://biomatrixci.com/challenge-1/

##This function solves the problem in the following manner:
    ##Input 
        ##m         --- the number of GAMES to be played 
        ##n         --- the number of TEAMS
        ##k         --- the number of STADIUMS 
        ##w         --- a [1 * n] array, with each corresponding index indicating the profit gained when each team plays 
        ##ai_bi     --- a [m * 2] matrix with each game to be played
    ##Output 
        ##ans       --- a [m * 1] array of each corresponding stadium to host each team in 

##Key questions:
        ##A. Why is there a need to schedule?
            ## 1.  If GAMES < TEAMS, got to allocate the post profitable pairing to play first 
            ## 2.  Since k (STADIUMS) is a parameter, it is best to assume that no DOUBLE scheduling occurs,
            ##     i.e, at a certain time-slot, team i is not expected to play at 2 stadiums at the same time.
            ## 3.  Without the above assumptions, there will be no scenario where any team is not expected to play, also
            ##     the solution is not applicable in reality.
        ##B. Why is the ai_bi matrix given as an input?
            ## 1. Likely to make the iterative search process easier in the following manner:
            ##    - ensuring that each pair of teams only plays 1 game.
            ##    - ensuring that NO team plays itself.
            ##    - limiting the search space only to the number of games to be played.

##Objective:
        ## To find the scheduling which maximized the total profit 
            ## To do that, the problem must first be formulated as a IP, and solved using GLPK, an open source solver. 
        
def determine_max_profit_schedule (teams, games, stadiums, profit, match_up):
    
    ##teams         --- the number of teams to be played
    ##games         --- the number of games to be played 
    ##stadiums      --- the number of stadiums to host the games 
    ##profit        --- the associated profit if when each team plays 
    ##match up      --- the the associated teams to play the match 
    
    ##Importing the necessary packages 
    import numpy as np 
    import math
    from bio_cha1_auxillary import tag_teams
    from bio_cha1_auxillary import write_script_lp_format
    from bio_cha1_auxillary import call_GLPK
    from bio_cha1_auxillary import extract_GLPK_results
    from bio_cha1_auxillary import convert_into_stadium_output
    
    match_up = np.array(match_up)
    
    ##First we determine the number of schedules required 
    num_schedules = math.ceil(games / stadiums)
    
    ##Next we tag the teams which appear repeatedly 
    team_count = tag_teams(teams, match_up)
    
    ##Now we write the integer programming problem in a LP format for readability 
    write_script_lp_format (teams, stadiums, profit, match_up, num_schedules, team_count)

    ##After the script is written, we solve it by calling GLPK
    o, convergence = call_GLPK ()
    
    ##Finally we extract the optimal values 
    obj_value, results_final = extract_GLPK_results (num_schedules, games)
    
    ##The last step is to convert the results into the intended form
    final_output = convert_into_stadium_output (stadiums, results_final, games, num_schedules)
        
    return final_output

###################################################################################################################################################################################
###################################################################################################################################################################################
##Running the script 
if __name__ == '__main__':
        
    n = 7
    m = 11
    k = 3
    
    w = [4, 7, 8, 10, 10, 9, 3]
    
    ai_bi = [[6, 2],
             [6, 1],
             [7, 6],
             [4, 3],
             [4, 6],
             [3, 1],
             [5, 3],
             [7, 5],
             [7, 3],
             [4, 2],
             [1, 4]]
    
    final_output = determine_max_profit_schedule(n, m, k, w, ai_bi)
    
    for i in range (0, len(final_output)):
        print(final_output[i])
    
    
    
    
            