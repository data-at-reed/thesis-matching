#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 13 11:23:43 2023

@author: griffinj
"""

import pandas as pd
import re

############################
#### CLEAN

#import google form
prefs = pd.read_csv('/Users/griffinj/Documents/ThesisAssignments/2024/Final Fall 2024 Thesis Advisor Preferences (Bio_Chem_Psych) (Responses) - Form Responses 1.csv')


# rename
new_col_names = {'Email Address': 'Email',
                 'Student Name':'Name',
                 'Student ID':'ID', 
                 'What is your major?':'Major',
                 '(Optional) \nPlease check here if you do not have a preference for which faculty/project you wish to be assigned to.': 'Equal',
                 'Describe your thesis with your first choice adviser.': 'Bio_1',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your first choice project. ':'Bio_Co_1',
                 'Describe your thesis with your second choice adviser.':'Bio_2',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your second choice project. ':'Bio_Co_2',
                 'Describe your thesis with your third choice adviser. ':'Bio_3',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your third choice project. ':'Bio_Co_3', 
                 'Describe your thesis with your first choice advisor.': 'Chem_1',
                 'Describe your thesis with your second choice advisor.': 'Chem_2',
                 'Describe your thesis with your third choice advisor.': 'Chem_3',
                 '(Optional) \nPlease check here if you do not have a preference for which faculty/project you wish to be assigned to..1': 'Equal2',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your first choice project. .1':'Chem_Co_1',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your second choice project. .1':'Chem_Co_2',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your third choice project. .1':'Chem_Co_3',
                 '(Optional) \nPlease check here if you do not have a preference for which faculty/project you wish to be assigned to..2': 'Equal3',
                 'Describe your thesis idea for your first-choice professor.': 'Psych_1',
                 'Describe your thesis idea for your second-choice professor.': 'Psych_2',
                 'Describe your thesis idea for your third-choice professor.': 'Psych_3',
                 'Describe your thesis with your first choice adviser..1': 'Neuro_1',
                 'Describe your thesis with your second choice adviser..1': 'Neuro_2',
                 'Describe your thesis with your third choice adviser.': 'Neuro_3',
                 '(Optional) \nPlease check here if you do not have a preference for which faculty/project you wish to be assigned to..3': 'Equal4',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your first choice project. .2': 'Neuro_Co_1',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your second choice project. .2': 'Neuro_Co_2',
                 '(Optional) \nIf applicable, please list the co-advisor or off-campus advisor for your third choice project. .2': 'Neuro_Co_3',                 
                 'Describe your thesis with your first choice advisor..1': 'BMB_1',
                 'Describe your thesis with your second choice advisor..1': 'BMB_2',
                 'Describe your thesis with your third choice advisor..1': 'BMB_3',
                 '(Optional) \nPlease check here if you do not have a preference for which faculty/project you wish to be assigned to..4': 'Equal5',
                 '(Optional) \nIf applicable, please list the co-adviser or off-campus advisor for your first choice project. ':'BMB_Co_1',
                 '(Optional) \nIf applicable, please list the co-adviser or off-campus advisor for your second choice project. ':'BMB_Co_2',
                 '(Optional) \nIf applicable, please list the co-adviser or off-campus advisor for your third choice project. ':'BMB_Co_3'}
                 
prefs.rename(columns=new_col_names, inplace=True)


# replace long name with short so easier to match with description
replacements = {'Biology': 'Bio',
                'Chemistry': 'Chem',
                'Psychology': 'Psych',
                'Neuroscience': 'Neuro'}

for old_str, new_str in replacements.items():
    prefs.columns = prefs.columns.str.replace(old_str, new_str)

# get columns to include in all separated data frames
all_columns = ['Email', 'Name', 'ID', 'Major']

# clean column names
pattern = re.compile(r'Choose (.*?) Professors \[')
clean_columns = [pattern.sub(r'\1 ', col) for col in prefs.columns]
prefs.columns = clean_columns
clean_columns = [col.replace("]", "") for col in prefs.columns]
prefs.columns = clean_columns
clean_columns = [col.replace(" (Bio)", "").replace(" (Chem)", "").replace(" (Psych)", "") for col in prefs.columns]
prefs.columns = clean_columns

# change choice from character to numeric and long major to short
# (the multiple changes of Major to Maj are to match the Maj_1 things)
prefs = prefs.replace({'First Choice': '1',
                      'Second Choice': '2',
                      'Third Choice': '3',
                      'Fourth Choice': '4',
                      'Biology': 'Bio',
                      'Chemistry': 'Chem',
                      'Psychology': 'Psych',
                      'Neuroscience': 'Neuro',
                      'Please consider my 3 adviser/project suggestions equally.': 'Y'})

# change all equals to 3
for index, row in prefs.iterrows():
    if row['Equal'] == 'Y':
        prefs.iloc[index] = row.str.replace('2', '1').str.replace('3', '1')
    if row['Equal2'] == 'Y':
        prefs.iloc[index] = row.str.replace('2', '1').str.replace('3', '1')   
    if row['Equal3'] == 'Y':
        prefs.iloc[index] = row.str.replace('2', '1').str.replace('3', '1')
    if row['Equal4'] == 'Y':
        prefs.iloc[index] = row.str.replace('2', '1').str.replace('3', '1')
    if row['Equal5'] == 'Y':
        prefs.iloc[index] = row.str.replace('2', '1').str.replace('3', '1')

# get majors
majors = ['Bio', 'Chem', 'Psych', 'Neuro', 'BMB']
non_major_columns = ['Email', 'Name', 'ID', 'Major']

# put all the paragraph statements into separate data frame with just ID
temp_desc =  prefs[prefs.columns[prefs.columns.str.contains('_|Email|Name|ID|Major')]]
grouped = temp_desc.groupby('Major')

# collapse across majors, reduce to just first, second, third, fourth descriptions
description = pd.DataFrame()
for major in majors:
    temp = grouped.get_group(major)
    filtered_columns = temp.columns[temp.columns.isin(non_major_columns) | temp.columns.str.contains(major)]
    temp = temp[filtered_columns] 
    temp.columns = temp.columns.str.replace(f'{major}_', '')
    description = pd.concat([description, temp])

description.to_csv('/Users/griffinj/Documents/ThesisAssignments/2024/thesis_descrip.csv', index=False)
    
############################
#### separate professors into data frames for optimization 

# make separate dfs by major
major_dfs = {}
for major in majors:
    major_columns = [col for col in prefs.columns if major in col]
    selected_columns = major_columns + non_major_columns
    selected_columns = [col for col in selected_columns if "_" not in col]
    filtered_df = prefs[prefs['Major'] == major]
    major_dfs[major] = filtered_df[selected_columns]

# make columns just names 
replacements = {'Bio ': '',
                'Chem ': '',
                'Psych ': '',
                'Neuro ': '',
                'BMB ': ''}

# ****EDIT****: can actually do this earlier, didn't realize how easy concatenate is
for old_str, new_str in replacements.items():
    #inter.columns = inter.columns.str.replace(old_str, new_str)
    for major, df in major_dfs.items():
        major_dfs[major].columns = df.columns.str.replace(old_str, new_str)

# combine major profs (chem, bio, psych) together
major_profs = pd.concat(major_dfs.values(), ignore_index=True, sort=False)
major_profs = major_profs.dropna(axis = 1, how = 'all')

#for key, value in major_profs.items():
#    print(f"{key}: {value}")
   
############################
# write files
major_profs.to_csv('/Users/griffinj/Documents/ThesisAssignments/2024/major_profs.csv', index=False)

print(major_profs.columns)




# #########
# # if need to split by shared profs, this is old code:
    
# # find people who are interdisciplinary
# shared = []
# for major in ['Neuro', 'BMB']:
#     df = major_dfs.get(major)
#     shared.extend(df.columns[df.notna().any()])    
    
# shared = [item.replace('Neuro ', '').replace('BMB ', '') for item in shared]
# shared = [value for value in shared if " " in value]
# shared = list(set(shared))

# #### create two data frames: interdisciplinary and non
# # get shared profs from the non-interdiscplinaries, create interdiscip to add to neuro/chem
# inter = pd.DataFrame()
# for major in ['Bio', 'Chem', 'Psych']:
#     non_empty = []
#     df = major_dfs[major]
#     for col in df.columns:
#         if any(match in col for match in shared):
#             non_empty.extend(df.index[df[col].notna()])
#     remove = list(set(non_empty))
#     inter = pd.concat([inter, df.loc[remove]])
#     major_dfs[major] = df.drop(remove)

# # remove blanks from interdisciplinary
# inter = inter.dropna(axis = 1, how = 'all')

# # combined shared profs (inter, neuro, BMB)
# shared_profs = pd.concat([inter, major_dfs['Neuro'], major_dfs['BMB']], ignore_index=True, sort=False)
# shared_profs = shared_profs.dropna(axis = 1, how = 'all')

# shared_profs.to_csv('/Users/griffinj/Documents/ThesisAssignments/2024/shared_profs.csv', index=False)
