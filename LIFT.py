# -*- coding: utf-8 -*-
"""
@author: M Nauta
"""
import pandas as pd
import numpy as np
import itertools
import json
import copy
from pprint import pprint

#values for the chi-square distribution, as can also be found in the Table from https://en.wikipedia.org/wiki/Chi-squared_distribution
thresholds=dict()
thresholds[0.90]=2.706
thresholds[0.95]=3.841
thresholds[0.99]=6.635
thresholds[0.999]=10.828

#add new column for AND-gate by temporarily extending the dataset with one extra column operating as the AND-gate
def mergeAND (df, tomerge):
    dfextended=df.copy()
    tomergeindices=[]
    for k in tomerge:
        index=df.columns.get_loc(k)
        tomergeindices.append(index)
    dataset = df.values
    newcolumn = np.zeros((len(dataset), 1))
    for i in range(len(dataset)):
        alltrue = True
        for k in range(len(tomerge)):
            if dataset[i, tomergeindices[k]] == False:
                alltrue=False
        if alltrue==True:
            newcolumn[i,0]=1
    dfextended['AND'] = newcolumn
    return dfextended

#add new column for OR-gate by temporarily extending the dataset with one extra column operating as the OR-gate
def mergeOR (df, tomerge):
    dfextended=df.copy()
    tomergeindices=[]
    for k in tomerge:
        index=df.columns.get_loc(k)
        tomergeindices.append(index)
    dataset = df.values
    newcolumn = np.zeros((len(dataset), 1))
    for i in range(len(dataset)):
        onetrue = False
        for k in range(len(tomerge)):
            if dataset[i, tomergeindices[k]] == True:
                onetrue=True
        if onetrue==True:
            newcolumn[i,0]=1
    dfextended['OR'] = newcolumn
    return dfextended

# generator of sets
def getavailablesets (df, splitter, seen):
    availablesets = []
    availables=[]
    for node in list(df):
        if node not in seen: # seen contains names, not indices.
            if node!=splitter:
                if node!='AND':
                    if node!='OR':
                        availables.append(node)
            
    for l in range(2, 6): #2 to 5 items as input in one gate
        for subset in itertools.combinations(availables, l):
            availablesets.append(subset)
    return availablesets

def getstratum(df, splitter, test_attribute, attribute_values, context=None):
    for key in attribute_values:
        df = df.loc[(df[key]==attribute_values[key])]

    c = np.ones((2,2))
    
    for testvalue in range(2):
        for splitvalue in range(2):
            df_temp = (df.loc[(df[test_attribute]==testvalue) & (df[splitter]==splitvalue)])
            count = df_temp.shape[0]
            c[(1-testvalue), (1-splitvalue)] = count
    return c

# calculates pamh score
def pamh(counts):
    #calculate numerator
    sumnumerator = 0.
    denominator = 0.
    
    for stratum in counts:

        if np.sum(stratum[:,0])==0 or np.sum(stratum[:,1])==0 or np.sum(stratum[0,:]) == 0 or np.sum(stratum[1,:])==0:
            continue
        else:
            above = stratum[0,0]*stratum[1,1] - stratum[1,0]*stratum[0,1]
            below = np.sum(stratum)
            stratumvalue = above / float(below)
            sumnumerator += stratumvalue
            
            #calculate denominator
            n1k = np.sum(stratum[0,:])
            n2k = np.sum(stratum[1,:])
            n1krow = np.sum(stratum[:,0])
            n2krow = np.sum(stratum[:,1])
            above = (n1k*n2k*n1krow*n2krow)
            total = np.sum(stratum)
            below = (total**2)*(total-1)
            value = above/float(below)
            denominator += value    
    sumnumerator = abs(sumnumerator)
    numerator = (sumnumerator - 0.5)**2
    if denominator == 0.:
        return 0
    else:
        return (numerator/float(denominator))

#tests if AND gate is correct:
def testANDgate(significance, df, parent, tuplechildren):
    result = False
    dfextended = mergeAND(df, tuplechildren)
    stratum = getstratum(dfextended, parent, 'AND', [])
    righttop = np.sum(stratum[0,1])
    leftbottom = np.sum(stratum[1,0])
    total = np.sum(stratum)
    if righttop>((1.0-significance)*total):
        return False, 0.0
    if leftbottom>((1.0-significance)*total):
        return False, 0.0
    pamhscore = pamh([stratum])
    if pamhscore>=thresholds[significance]:
    #gate is significant
        result = True
    return result, pamhscore

def testORgate(significance, df, parent, tuplechildren):
    dfextended=mergeOR(df, tuplechildren)
    stratum = getstratum(dfextended, parent, 'OR', [])
    righttop = np.sum(stratum[0,1])
    leftbottom = np.sum(stratum[1,0])
    total = np.sum(stratum)
    
    if righttop>(1.0-significance)*total:
        return False, 0.0
    elif leftbottom>(1.0-significance)*total:
        return False, 0.0
    pamhscore = pamh([stratum])
    result = False
    if pamhscore>=thresholds[significance]:
        result = True
    return result, pamhscore

# LIFT
def createlayer(significance, df, generatedtree, seen, parentlist):
    for splitter in parentlist:
        lowestnrchildrenAND= float("inf")
        lowestnrchildrenOR= float("inf")
        highestpamhOR=0.
        highestpamhAND=0.
        availablesets = getavailablesets(df, splitter, seen)

        if availablesets:
            for a in availablesets:
                if (len(a)>lowestnrchildrenAND) or (len(a)>lowestnrchildrenOR):
                    break
                else:
                    testresult = testORgate(significance, df, splitter, a)
                    testbool = testresult[0]
                    pamhscore = testresult[1]
                    if testbool:
                        if pamhscore>highestpamhOR:
                            highestpamhOR=pamhscore
                            generatedtree[splitter]=[a, 'OR']
                            lowestnrchildrenOR=len(a)

                    testresult = testANDgate(significance, df, splitter, a)
                    testbool = testresult[0]
                    pamhscore = testresult[1]

                    if testbool:
                        if pamhscore>highestpamhAND:
                            highestpamhAND=pamhscore
                            generatedtree[splitter]=[a, 'AND']
                            lowestnrchildrenAND=len(a)

                
        if splitter in generatedtree:
            children=generatedtree[splitter][0]
            for c in children:
                if c not in seen:
                    seen.append(c)
    
    return generatedtree, seen

def learnFTandcheck(tree, dataset, significance):
    df=dataset*1
    #convert tree with indices to tree with nodenames
    tree = json.loads(tree)

    newtree = dict()
    for pos in range(len(tree)):
        values = tree[str(pos)][0]
        newvalues=()
        for v in values:
            newvalues+=(df.columns[v],)
        newtree[df.columns[pos]] = [newvalues,tree[str(pos)][1]]

    topevent = 'G0'
    generatedtree=dict()
    seen = [topevent]
    oldseen=[]
    generatedtree, seen = createlayer(significance, df, generatedtree, seen, [topevent]) #creates only first layer
    while seen!=oldseen:
        allchildren = generatedtree.values()
        allparents = generatedtree.keys()
        nr = 0
        parentlist=[]
        for clist in allchildren:
            ctuple=clist[0]
            for c in ctuple:
                nr+=1
                if c not in allparents:
                    parentlist.append(c)
        oldseen = copy.deepcopy(seen)
        generatedtree, seen = createlayer(significance, df, generatedtree, seen, parentlist)  #create next layer of FT
    for event in list(df):
        if event not in generatedtree:
            if event in seen:
                #event is BE and should be added
                generatedtree[event]=[(), 'BE']

    if newtree!=generatedtree:
        return False
    else:
        return True
