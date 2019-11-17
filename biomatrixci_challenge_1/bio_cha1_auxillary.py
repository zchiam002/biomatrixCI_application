##This script contains helper functions which are needed to solve the optimization problem 

##This function converts the optimal stadium labels 
def convert_into_stadium_output (stadiums, results_final, games, num_schedules):
    
    ##stadiums          --- the number of stadiums to host the games 
    ##results_final     --- the optimal stadium schedule 
    ##games             --- the total number of games 
   ##num_schedules     --- the number of required schedules

    final_output = [0] * games 
    
    for i in range (0, num_schedules):
        start_index = i * games
        end_index = start_index + games 
        
        
        
        count = 0
        stadiums_left = stadiums
        for j in range (start_index, end_index):
            if int(results_final['Values'][j]) == 1:
                final_output[int(count)] = stadiums_left
                stadiums_left = stadiums_left - 1
            count = count + 1
        
    return final_output 

##This function extracts the results from the text file 
def extract_GLPK_results (num_schedules, games):

    ##num_schedules     --- the number of required schedules
    ##games             --- the total number of games 
     
    import os 
    current_directory = os.path.dirname(__file__) + '\\' 
    import pandas as pd 
    
    ##Result file location 
    result_file = current_directory + 'working_folder\\out.txt'
    
    ##Extracting the objective function 
    with open(result_file) as fo:
        for rec in fo:
            if 'Objective:  ' in rec:
                obj = rec.split(' ')
                break
    obj_value = float(obj[4])

    ##Establishing the list of results to extract 
    list_names = []
    for i in range (0, int(num_schedules)):
        for j in range (0, int(games)):
            list_names.append('T_g' + str(j) + '_z' + str(i))
            
    #Extracting the rest of the values 
        ##Parameters to search the file by 
        starting_line = 0
        variable_count = 0        
        last_line = 0    
 
        ##Initiating a dataframe to hold the return values 
        results_final = pd.DataFrame(columns = ['Names', 'Values'])
    
    with open(result_file) as fo:
        for rec in fo:
            if last_line == 1:
                break            
            else:
                check_split = rec.split()
                if check_split:
                    if starting_line < 2:
                        if len(check_split) != 0:
                            if str.isdigit(check_split[0]) == True:
                                if int(check_split[0]) == 1:
                                    starting_line = starting_line + 1            
            
                    ##This is where the records should start
                    if starting_line == 2:
                        if variable_count < len(list_names):
                            if (str.isdigit(check_split[1]) == False) and (len(check_split[1]) > 12): 
                                if check_split[1] in list_names:
                                    temp_name = check_split[1]
                                    check_split2 = next(fo).split()
                                    temp_data_to_save = [temp_name, int(check_split2[1])]
                                    temp_data_to_save_df = pd.DataFrame(data = [temp_data_to_save], columns = ['Names', 'Values'])
                                    results_final = results_final.append(temp_data_to_save_df, ignore_index = True)
                                
                            elif (str.isdigit(check_split[1]) == False):
                                if check_split[1] == 'feasibility':
                                    last_line = 1
                                    break
                                elif check_split[1] in list_names:
                                    temp_name = check_split[1]
                                    temp_data_to_save = [temp_name, int(check_split[3])]
                                    temp_data_to_save_df = pd.DataFrame(data = [temp_data_to_save], columns = ['Names', 'Values'])
                                    results_final = results_final.append(temp_data_to_save_df, ignore_index = True)
                                    variable_count = variable_count + 1    
            
    return obj_value, results_final

##This function calls GLPK to solve the problem 
def call_GLPK ():
    
    import subprocess
    import os 
    current_directory = os.path.dirname(__file__) + '\\' 
    
    ##Directories 
    main_call = current_directory + 'glpk-4.61\w64\glpsol --lp'
    file_location = current_directory + 'working_folder\script.lp'
    result_location = current_directory + 'working_folder\out.txt'
    
    command = main_call + ' ' + file_location + ' -o ' + result_location

    o = subprocess.check_call(command, shell= True)
    ## Checking for the output of the solver 
    if os.path.isfile(result_location) == False:
        convergence = 0
        return o, convergence
    
    else:
        if os.path.getsize(result_location) == 0:
            convergence = 0
            return o, convergence
    
    with open(result_location, 'r') as fo:
        solver_msg = fo.read()
    
    if 'OPTIMAL' in solver_msg:
        convergence = 1
    
    else:
        convergence = 0
    
    return o, convergence

##This function writes the optimization script in LP format, for the sake of readability 
def write_script_lp_format (teams, stadiums, profit, match_up, num_schedules, team_count):
    
    ##teams             --- the number of teams to be played
    ##stadiums          --- the number of stadiums to host the games 
    ##profit            --- the associated profit if when each team plays 
    ##match up          --- the the associated teams to play the match 
    ##num_schedules     --- the number of required schedules 
    ##team_count        --- the number of times each team appears in the list of match ups
    
    import os 
    current_directory = os.path.dirname(__file__) + '//' 
    import numpy as np
    
    script_loc = current_directory + 'working_folder//script.lp'
    
    f_data_set = open(script_loc, 'w')
    
    ##Writing the objective function 
    f_data_set.write('\\\\ Objective function \n \n')
    f_data_set.write('Maximize \n')
    f_data_set.write('\n')       

    obj_func_input = ''
    
    for i in range (0, int(num_schedules)):
        if i < int(num_schedules) - 1:
            obj_func_input = obj_func_input + 'sch_' + str(i) + ' + '
        else:
             obj_func_input = obj_func_input + 'sch_' + str(i)           
        
    f_data_set.write('obj: ' + obj_func_input) 
    f_data_set.write('\n \n')    

    ##Writing the constraints  
    f_data_set.write('Subject To \n \n')

    current_index = 0
    
    for i in range (0, int(num_schedules)):
        cons_temp = 'c' + str(current_index) + ': '
        curr_team_count = np.zeros((1, int(teams)))
        for j in range (0, match_up.shape[0]):
            
            team1 = int(match_up[j, 0] - 1)
            team2 = int(match_up[j, 1] - 1)
            
            team_1_profit = profit[team1]
            team_2_profit = profit[team2]
            
            if j < int(match_up.shape[0]) - 1:
                cons_temp = cons_temp + str(team_1_profit) + ' T_z' + str(i) + '_' + str(team1) + '_' + str(int(curr_team_count[0, team1])) + ' + '
                cons_temp = cons_temp + str(team_2_profit) + ' T_z' + str(i) + '_' + str(team2) + '_' + str(int(curr_team_count[0, team2])) + ' + '
                
            else:
                cons_temp = cons_temp + str(team_1_profit) + ' T_z' + str(i) + '_' + str(team1) + '_' + str(int(curr_team_count[0, team1])) + ' + '
                cons_temp = cons_temp + str(team_2_profit) + ' T_z' + str(i) + '_' + str(team2) + '_' + str(int(curr_team_count[0, team2])) + '- sch_' + str(i) + ' >= 0'
            
            ##Updating the team count 
            curr_team_count[0, team1] = curr_team_count[0, team1] + 1
            curr_team_count[0, team2] = curr_team_count[0, team2] + 1
            
        f_data_set.write(cons_temp + '\n')          
        current_index = current_index + 1
        
        ##Making sure that each team only plays once in each schedule 
        for j in range (0, int(teams)):
            cons_temp = 'c' + str(current_index) + ': '
            curr_team = int(j)
            for k in range (0, int(team_count[0, curr_team])):
                if k < int(team_count[0, curr_team] - 1):
                    cons_temp = cons_temp + 'T_z' + str(i) + '_' + str(curr_team) + '_' + str(k) + ' + '
                else:
                    cons_temp = cons_temp + 'T_z' + str(i) + '_' + str(curr_team) + '_' + str(k) + ' <= 1'
            f_data_set.write(cons_temp + '\n')          
            current_index = current_index + 1

        ##Making sure that teams stick to the predefined match ups 
        curr_team_count = np.zeros((1, int(teams)))
        for j in range (0, match_up.shape[0]):            
            cons_temp = 'c' + str(current_index) + ': '
            team1 = int(match_up[j, 0] - 1)
            team2 = int(match_up[j, 1] - 1)
            cons_temp = cons_temp + 'T_z' + str(i) + '_' + str(team1) + '_' + str(int(curr_team_count[0, team1])) + ' + T_z' + str(i) + '_' + str(team2) + '_' + str(int(curr_team_count[0, team2])) + ' - 2 T_g' + str(j) + '_z' + str(i) + ' = 0'   
            ##Updating the team count 
            curr_team_count[0, team1] = curr_team_count[0, team1] + 1
            curr_team_count[0, team2] = curr_team_count[0, team2] + 1                                 
            f_data_set.write(cons_temp + '\n')          
            current_index = current_index + 1            
            
        ##Making sure that in each schedule, the number of games do not exceed the number of stadiums 
        cons_temp = 'c' + str(current_index) + ': '
        for j in range (0, match_up.shape[0]):
            if j < int(match_up.shape[0]) - 1:
                cons_temp = cons_temp + 'T_g' + str(j) + '_z' + str(i) + ' + '
            else:
                cons_temp = cons_temp + 'T_g' + str(j) + '_z' + str(i) + ' <= ' + str(int(stadiums))                
                                                
        f_data_set.write(cons_temp + '\n')          
        current_index = current_index + 1                      
    ##Making sure that each group only features once in each schedule 
    for i in range (0, match_up.shape[0]):
        cons_temp = 'c' + str(current_index) + ': '
        for j in range (0, int(num_schedules)):
            if j < int(num_schedules) - 1:
                cons_temp = cons_temp + 'T_g' + str(i) + '_z' + str(j) + ' + '
            else:
                cons_temp = cons_temp + 'T_g' + str(i) + '_z' + str(j) + ' <= 1'
            
        f_data_set.write(cons_temp + '\n')          
        current_index = current_index + 1     

    f_data_set.write('\n')        
    ##Writing the binary constraints  
    f_data_set.write('Binary \n \n')      
    
    for i in range (0, int(num_schedules)):
        for j in range (0, teams):
            for k in range (0, int(team_count[0, j])):
                temp_term = 'T_z' + str(i) + '_' + str(j) + '_' + str(k)
                f_data_set.write(temp_term + '\n')                 
    
        for j in range (0, match_up.shape[0]):
            temp_term = 'T_g' + str(j) + '_z' + str(i) 
            f_data_set.write(temp_term + '\n')          
        
    ##Wrapping up 
    f_data_set.write('End \n')    
    f_data_set.close    
    return 

##This function tags the teams to track how many times they appear in the list of match ups
def tag_teams (teams, match_up):
    
    ##teams             --- the number of teams to be played    
    ##match up          --- the the associated teams to play the match 
    
    import numpy as np 
    
    team_count = np.zeros((1, int(teams)))
    
    for i in range (0, match_up.shape[0]):
        team_count[0, int(match_up[i, 0] - 1)] = team_count[0, int(match_up[i, 0] - 1)] + 1
        team_count[0, int(match_up[i, 1] - 1)] = team_count[0, int(match_up[i, 1] - 1)] + 1  
    
    return team_count