# -*- coding: utf-8 -*-
"""
@author: M Nauta
"""

import random
import json
import numpy as np
import pandas as pd
import math
import itertools

def createdataset(tree):
    #set BEs to True or False    
    values = dict()
    for key in tree:
        node = tree[key]
        probability = random.uniform(0.2, 0.5)
        if node[1]=='BE':
            values[key] = random.random() < probability 

    # read logic to set gates to True or False
    while len(values.keys())<len(tree.keys()):
        for key in tree:
            if key not in values.keys():
                node=tree[key]
                gatetype = node[1]
                if gatetype!='BE':
                    children=node[0]
                    allchildrenset = True
                    for c in children:
                        if c not in values.keys():
                            allchildrenset = False
                    #If all children of the node have a value, then set value of that parent node as well
                    if allchildrenset == True:
                        if gatetype=='AND':
                            alltrue = True
                            for c in children:
                                if values[c]==False:
                                    alltrue=False
                            if alltrue:
                                values[key]=True
                            else:
                                values[key]=False
                        elif gatetype=='OR':
                            notrue = True
                            for c in children:
                                if values[c]==True:
                                    notrue=False
                            if notrue==False:
                                values[key]=True
                            else:
                                values[key]=False
    return values

def createallcombinations(tree, dataset):
    for gatekey in tree:
        outputnode = tree[gatekey]
        if outputnode[1]!='BE':
            inputchildren = outputnode[0]
            combinations = list(itertools.product([0, 1], repeat=len(inputchildren)))
            for combi in combinations:
                values=dict()
                for i in range(len(combi)):
                    values[inputchildren[i]]=bool(combi[i])
                while len(values.keys())<len(tree.keys()):
                    for key in tree:
                        if key not in values.keys():
                            node=tree[key]
                            gatetype = node[1]
                            if gatetype=='BE':
                                #check value of parent
                                for parent in tree:
                                    parentchildren = tree[parent][0]
                                    if key in parentchildren:
                                        #parent found
                                        if parent in values.keys():
                                            v = values[parent]
                                            if v:
                                                values[key]=True
                                            else:
                                                 values[key]=False
                                        else: #parent not yet valued, set BE to false
                                            values[key]=False
                            else: 
                                children=node[0]
                                allchildrenset = True
                                for c in children:
                                    if c not in values.keys():
                                        allchildrenset = False
                                #If all children of the node have a value, then set value of that parent node as well
                                if allchildrenset == True:
                                    if gatetype=='AND':
                                        alltrue = True
                                        for c in children:
                                            if values[c]==False:
                                                alltrue=False
                                        if alltrue:
                                            values[key]=True
                                        else:
                                            values[key]=False
                                    elif gatetype=='OR':
                                        notrue = True
                                        for c in children:
                                            if values[c]==True:
                                                notrue=False
                                        if notrue==False:
                                            values[key]=True
                                        else:
                                            values[key]=False
                dataset.append(list(values.values()))
    return dataset


def createnoisedrow(tree):
    #set BEs to True or False    
    values = dict()
    events = tree.keys()
    for key in tree:
        node = tree[key]
        probability = random.uniform(0.2, 0.5)
        if node[1]=='BE':
            values[key] = random.random() < probability 
               
    # read logic to set gates to True or False
    while len(values.keys())<len(tree.keys()):
        for key in tree:
            if key not in values.keys():
                node=tree[key]
                gatetype = node[1]
                if gatetype!='BE':
                    children=node[0]
                    allchildrenset = True
                    for c in children:
                        if c not in values.keys():
                            allchildrenset = False
                    #If all children of the node have a value, then set value of that parent node as well
                    if allchildrenset == True:
                        if gatetype=='AND':
                            alltrue = True
                            for c in children:
                                if values[c]==False:
                                    alltrue=False
                            if alltrue:
                                values[key]=True
                            else:
                                values[key]=False
                            
                        elif gatetype=='OR':
                            notrue = True
                            for c in children:
                                if values[c]==True:
                                    notrue=False
                            if notrue==False:
                                values[key]=True
                            else:
                                values[key]=False
    

    eventstochange = random.sample(events, 2)
    for e in eventstochange:
        values[e]=not values[e]
    return values


def createrandomvariable(nrrows):
    columnvector = []
    for i in range(nrrows):
        columnvector.append(bool(random.getrandbits(1))) #choose random boolean
    return columnvector

