#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 13:40:06 2022

@author: griffinj
"""

import pandas as pd
import numpy as np
import scipy as sp
import random


#import preference, description, and professor limit files
major_prefs = pd.read_csv('/Users/griffinj/Documents/ThesisAssignments/2024/major_profs.csv')
#shared_prefs = pd.read_csv('/Users/griffinj/Documents/ThesisAssignments/shared_profs.csv')
description = pd.read_csv('/Users/griffinj/Documents/ThesisAssignments/2024/thesis_descrip.csv')
limits = pd.read_csv('/Users/griffinj/Documents/ThesisAssignments/2024/limits.csv', encoding='ISO-8859-1')

# clean, transform limits
limits['Name'] = limits['Name'].str.replace('ChacÃ³n', 'Chacón')
limits['Name'] = limits['Name'].str.replace('SimÃµes', 'Simões')
limits['Name'] = limits['Name'].str.replace('GonzÃ¡lez', 'González')
limits = limits.set_index('Name').T.to_dict('list')

##########################
# ASSIGNMENT FUNCTION

def process_dataframe(prefs, limits, n):
    
    # randomize students
    prefs = prefs.sample(random_state = n, frac=1).reset_index(drop=True)
    
    #replace NaN values with sufficiently high penalty score
    #gonna pick 1000?
    prefs = prefs.replace(np.nan, 1000)
    prefs = prefs.replace(4, 100)
    prefs = prefs.replace(3, 10)
    
    #duplicate professors up to their limit
    #need to repeat professors in order for linear sum function to work
    #creating df for preferences with repeated profs
    #prefs_rep = prefs.drop(prefs.columns[0], axis=1)
    prefs_rep = pd.DataFrame()
    
    #for every professor in the preferences df, repeat their column based on limits dictionary
    for name in prefs.columns:
        #find column name in dictionary keys
        if name in limits.keys():
            #repeat that column number of dictionary value times 
            rep = limits[name][1]
            counter = 0
            #for x in range(0, i+1):
            while counter < rep:
                extract = prefs[[name]]
                prefs_rep = pd.concat([prefs_rep, extract], axis = 1)
                counter += 1
                
    #linear sum function only takes arrays of numbers
    #remove first column of psych names (remember index is 0 in Python)
    #noname = prefs_rep.drop(prefs_rep.columns[0], axis=1)
    
    #convert to array for linear sum function
    pref_array = prefs_rep.to_numpy()
    
    #linear sum assignment
    out = sp.optimize.linear_sum_assignment(pref_array)    
    
    #get prof names and index, match them
    prof_index = out[1]
    profs = prefs_rep.columns
    prof_match = [profs[index] for index in prof_index]
    
    # convert back to ranks
    prefs = prefs.replace(100, 4)
    prefs = prefs.replace(10, 3)    
    
    # add student info
    match = pd.DataFrame({'Student': prefs.loc[:, 'Name'], 'Matched Advisor': prof_match})
    
    # create data frame with all relevant columns
    for student in match['Student']:
        prof = match[match['Student'] == student]['Matched Advisor']
        choice = prefs[prefs['Name'] == student][prof].values[0]
        match.loc[match['Student'] == student, 'Rank'] = choice[0]
        major = prefs[prefs['Name'] == student]['Major']
        match.loc[match['Student'] == student, 'Major'] = major
        student_id = prefs[prefs['Name'] == student]['ID']
        match.loc[match['Student'] == student, 'ID'] = student_id
        row = prefs[prefs['Name'] == student]
        first = row.columns[(row == 1).iloc[0]].max()
        second = row.columns[(row == 2).iloc[0]].max()
        third = row.columns[(row == 3).iloc[0]].max()
        match.loc[match['Student'] == student, 'First Choice'] = first
        match.loc[match['Student'] == student, 'Second Choice'] = second
        match.loc[match['Student'] == student, 'Third Choice'] = third
    
    # clean up
    match = match.fillna("-")
    
    return match

##############################
#run function

old_sum = float('inf')
#processed_shared = process_dataframe(shared_prefs, limits)
# do it 50 times and take lowest
for i in range(1,51):
    n = random.randint(0, 10000)
    processed_major = process_dataframe(major_prefs, limits, n)
    new_sum = sum(processed_major['Rank'])
    if new_sum < old_sum:
        full_match = processed_major
        old_sum = new_sum


# concat and sort
#full_match = pd.concat([processed_shared, processed_major], axis = 0)
full_match = full_match[['Major', 'ID', 'Student', 'Matched Advisor', 'Rank', 'First Choice', 'Second Choice', 'Third Choice']]
full_match = full_match.sort_values(by=['Major', 'Matched Advisor'], na_position='last')

##############################
# create thesis description sheet 

# match advisor to description
for student in description['Name']:
    advisor_1 = full_match[full_match['Student'] == student]['First Choice'].values[0]
    advisor_2 = full_match[full_match['Student'] == student]['Second Choice'].values[0]
    advisor_3 = full_match[full_match['Student'] == student]['Third Choice'].values[0]
    description.loc[description['Name'] == student, 'A1'] = advisor_1
    description.loc[description['Name'] == student, 'A2'] = advisor_2
    description.loc[description['Name'] == student, 'A3'] = advisor_3
    
    
# make new data frame that has student_advisor as each row
melted_desc = pd.melt(description, id_vars=['Name', 'Major'], value_vars=['1','2','3'], var_name='Rank', value_name='Description')
melted_adv = pd.melt(description, id_vars=['Name'], value_vars=['A1','A2','A3'], var_name='A', value_name='Advisor')
merged = melted_desc.merge(melted_adv, left_index=True, right_index=True)
melted_co = pd.melt(description, id_vars=['Name'], value_vars=['Co_1','Co_2','Co_3'], var_name='Coadvisor_Rank', value_name='Coadvisor')
thesis_desc = merged.merge(melted_co, how = 'left', left_index=True, right_index=True)

thesis_desc = thesis_desc.drop(columns = ['Name', 'Name_y', 'A', 'Coadvisor_Rank'])
thesis_desc = thesis_desc[['Major', 'Name_x', 'Rank', 'Advisor', 'Coadvisor', 'Description']]
thesis_desc = thesis_desc.sort_values(by=['Major', 'Name_x'])
thesis_desc = thesis_desc.rename(columns = {'Name_x':'Student',
                                            'Advisor': 'Desired Advisor'})


# write files
full_match.to_csv('/Users/griffinj/Documents/ThesisAssignments/2024/matched.csv', index=False)
thesis_desc.to_csv('/Users/griffinj/Documents/ThesisAssignments/2024/thesis_desc.csv', index=False)



