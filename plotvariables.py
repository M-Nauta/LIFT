# -*- coding: utf-8 -*-
"""
@author: M Nauta
"""

from generateFT import createnoisedrow
from generateFT import createdataset
from generateFT import createrandomvariable
from generateFT import createallcombinations
from generateFTsofsize import getalltreesofsize
from LIFT import learnFTandcheck
import pandas as pd
import numpy as np
import math
import json


treesize = 8
rows = 1000
variables = range(0, 5) #superfluous variables
combipercentages = [0.005, 0.02] #0.5% or 2% of all rows in dataset has all combinations
significances = [0.90,0.95,0.99,0.999] #signiciance percentages
sigpercentages = dict()

# plot with superfluous variables
def generatedatasetsfortrees(trees, rows, nrvariables, combipercentage):
    treeswithdataset = dict()
    for tree in trees:
        treestring = json.dumps(tree)
        dataset = []
        bes = []
        gates = []
        names = []
        for key in tree:
            node=tree[key][1]
            if node=='BE':
                name = str('BE'+str(len(bes)))
                bes.append(name)
            else:
                name = str('G'+str(len(gates)))
                gates.append(name)
            names.append(name)
        dataset.append(names)

        for k in range(int(combipercentage*rows)):
            dataset = createallcombinations(tree, dataset)
        while len(dataset)<rows:
            values = createdataset(tree)
            dataset.append(list(values.values()))

        headers = dataset.pop(0)
        df = pd.DataFrame(dataset, columns=headers, dtype=bool)

        nrrows = df.shape[0]
        for i in range(nrvariables):
            columnname = 'R'+str(i)
            df[columnname] = createrandomvariable(nrrows)

        treeswithdataset[treestring]=df
    return treeswithdataset

for significance in significances:
    trees = getalltreesofsize(treesize)
    total = len(trees)

    for cp in combipercentages:
        toplot = []
        for nv in variables:
            correct = 0
            wrong = 0
            treeswithdatasets = generatedatasetsfortrees(trees, rows, nv, cp)
            for i in range(len(trees)):
                tree = trees[i]
                treestring = json.dumps(tree)
                result = learnFTandcheck(treestring, treeswithdatasets[treestring], significance)
                #        print (result)
                if result:
                    correct += 1
                else:
                    wrong += 1
            percentage = float(correct / total)
            print("extra variables: ", nv, "\n", "significance: ", significance, "\n", "% correct FTs:", percentage)
            toplot.append(percentage)
        sigpercentages[(significance, cp)] = toplot

print("significance results: ", sigpercentages)

# plot for noise levels
def generatenoisydatasetsfortrees(trees, rows, noisepercentage, combipercentage):
    treeswithdataset = dict()
    for tree in trees:
        treestring = json.dumps(tree)
        dataset = []
        bes = []
        gates = []
        names = []
        for key in tree:
            node = tree[key][1]
            if node == 'BE':
                name = str('BE' + str(len(bes)))
                bes.append(name)
            else:
                name = str('G' + str(len(gates)))
                gates.append(name)
            names.append(name)
        dataset.append(names)

        for k in range(int(combipercentage * rows)):
            dataset = createallcombinations(tree, dataset)

        while len(dataset) < rows:
            values = createdataset(tree)
            dataset.append(list(values.values()))

        noisyrows = math.ceil(noisepercentage * (len(dataset) - 1))
        for i in range(noisyrows):
            values = createnoisedrow(tree)
            dataset.append(list(values.values()))

        headers = dataset.pop(0)
        df = pd.DataFrame(dataset, columns=headers, dtype=bool)

        treeswithdataset[treestring] = df
    return treeswithdataset


noisepercentages = dict()
percentages = np.arange(0.0, 2.01, 0.5)
for significance in significances:
    print ("significance: ", significance)

    trees = getalltreesofsize(treesize)
    total = len(trees)
    print ("number of trees: ", total)
    for cp in combipercentages:
        toplot=[]
        for noisep in percentages:
            print ("noise: ", noisep)
            noisep = noisep/100
            correct = 0
            wrong = 0
            treeswithdatasets = generatenoisydatasetsfortrees(trees, rows, noisep, cp)
            for i in range(len(trees)):
                tree = trees[i]
                treestring = json.dumps(tree)
                print("tree: ",treestring)
                result = learnFTandcheck(treestring, treeswithdatasets[treestring], significance)
                if result:
                    correct+=1
                else:
                    wrong+=1
            percentage = float(correct/total)
            print ("noise: ", noisep*100, "\n", "% correct FTs:", percentage)
            toplot.append(percentage)
            noisepercentages[(significance, cp)]=toplot

print("noise results: ", noisepercentages)
