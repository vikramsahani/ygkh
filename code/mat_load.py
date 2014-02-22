"""
Load the csv data file and preprocess them (e.g. calculate mean and std deviation and normalize)
"""

import csv
import numpy as np
import os
import linreg
import neuro
import pickle

# feature_count = 41

first_year = 1970
last_year = 2011

indicator_list = []
feature_count = 105

country_list = []
country_count = 0

recommended_features_index = [
    2,
    4,
    6,
    7,
    9,
    10,
    13,
    16,
    19,
    22,
    31,
    50,
    56,
    62,
    68,
    74,
    75,
    77,
    79,
    82,
    87,
    91,
    92,
    96,
    97,
    102,
    103,
    105,
    106,
]

# recommended_features_list = ['# Adjusted savings: Energy Depletion',  'Adjusted savings: Mineral Depletion',  'Adolescent fertility rate',  'Crude Birth Rate',  'Crop Production Index',  'Crude Death Rate',  'Total Fertility Rate', 'Food production index', 'Total Life Expectancy at Birth', 'Livestock Production Index', 'Mobile Cellular Subscription per 100 people', 'Total Population', 'Annual Population Growth %', 'Population Density', 'Population in Largest City', 'Primary Education Duration', 'Primary Schooling Starting Age', 'Rural Population % of total population', 'Secondary Education Duration', 'Secondary School Starting Age', 'Telephone lines (per 100 peoples)', 'Urban Population (% of Total)', 'Annual Urban Population growth %']
recommended_features_list = []

# recommended_features = [
#     0,  # Adjusted savings: Energy Depletion
#     1,  # Adjusted savings: Mineral Depletion
#     2,  # Adolescent fertility rate
#     6,  # Crude Birth Rate
#     7,  # Crop Production Index
#     8,  # Crude Death Rate
#     9,  # Total Fertility Rate
#     10, # Food production index
#     14, # Total Life Expectancy at Birth
#     15, # Livestock Production Index
#     17, # Mobile Cellular Subscription per 100 people
#     18, # Total Population
#     23, # Annual Population Growth %
#     22, # Population Density
#     24, # Population in Largest City
#     27, # Primary Education Duration
#     28, # Primary Schooling Starting Age
#     30, # Rural Population % of total population
#     31, # Secondary Education Duration
#     32, # Secondary School Starting Age
#     37, # Telephone lines (per 100 peoples)
#     39, # Urban Population (% of Total)
#     40, # Annual Urban Population growth %
#     ]

for i in os.listdir('Work/'):
    country_count += 1

#The feature matrix
F = np.zeros((feature_count, country_count* (last_year-first_year+1)))

country_index = 0

def loadmat(filename):
    global country_index
    global indicator_list
    append = False
    if not indicator_list:
        append = True
    actualfname = 'Work/'+filename
    countryname = filename[:-4]
    country_list.append(countryname)
    with open(actualfname,'rb') as infile:
        csvreader = csv.DictReader(infile)
        for i, rows in enumerate(csvreader):
            #take the columns from 1960-2010
            if append:
                    indicator_list.append(rows['Indicator Name'])
            for col in rows:
                if len(col) == 4:   #i.e. it is a year data
                    index = int(col)-first_year
                    if index >= last_year-first_year+1: continue
                    val = 0 if rows[col] == '' else np.float(rows[col])
                    #val = rows[col] == '' and 0 or np.float(rows[col])
                    F[i, index + country_index*country_count] = val
    country_index += 1


def extract_indicators(countryname, year):
    data = []
    with open('%s.csv'%countryname) as infile:
        csvreader = csv.DictReader(infile)
        for rows in csvreader:
            if rows['Indicator Name'] in indicator_list:
                # print rows['Indicator Name']
                # print rows[year]
                # print float(rows[year])
                data.append(float(rows[year]))
    d = np.matrix(data).T
    # d = (d - muF)/sigmaF
    d = d/sigmaF
    # d = np.row_stack((np.array([0]), d))

    return d

for files in os.listdir('Work/'):
    loadmat(files)

for i, val in enumerate(indicator_list):
    if i+2 in recommended_features_index:
        print i+2, val
        recommended_features_list.append(val)

G = np.diff(F)
sigmaF= np.matrix(np.std(F,axis=1)).T
muF = np.matrix(np.mean(F, axis=1)).T
F = F/sigmaF

#Filter the Gradients..
G = G[np.array(recommended_features_index)-2, :]
sigmaG = np.matrix(np.std(G,axis=1)).T
muG = np.matrix(np.mean(G, axis=1)).T
#scale G in 0...1
minG = np.matrix(np.min(G, axis = 1)).T
maxG = np.matrix(np.max(G, axis = 1)).T
G = (G - minG)/(maxG - minG)
G = G/sigmaG
# print np.max(G)
# print np.min(G)

F = F[:, :-1]
# print F.shape
# print G.shape

n, m = F.shape
nrf, m = G.shape

#print n, m, nrf

F = np.matrix(F)
G = np.matrix(G)
R = np.matrix(np.zeros((nrf, n+1)))


nepal_features = extract_indicators("Nepal", '2011')

recommendations = {}
for i in range(nrf):
    print "Training %d/%d"%(i+1, nrf)
    L = linreg.linreg()
    L.train(F.T, G[i,:].T,regularization_param=10, alpha = 0.05, normalize=False, epochs=1000)
    R[i, :]= L.theta.T
    recommendations[recommended_features_list[i]] = L


# predictions = R * nepal_features
# predictions =

# for i, indicator_name in enumerate(recommended_features_list):
    # print indicator_name, predictions[i, 0]
    # print
results = {}

for r in recommendations:
    results[r] = recommendations[r].predict(nepal_features.T)[0,0]

with open('results_linreg10.csv','wb') as outfile:
    row_dict = {}
    keywords = results.keys()
    csvwriter = csv.DictWriter(outfile, keywords)
    t = ','.join([i.replace(',','-') for i in keywords]) + '\n'
    outfile.write(t)
    for indicator_name in recommended_features_list:
        row_dict[indicator_name] = results[indicator_name]
    csvwriter.writerow(row_dict)
