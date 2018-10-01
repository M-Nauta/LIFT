# -*- coding: utf-8 -*-
"""
@author: M Nauta
"""

import copy

gatetypes = ['OR', 'AND']
eventtypes = ['OR', 'AND', 'BE']
children_list = [2,3,4,5] #input of gate is at least 2 and max 5 events

def checktree(treesize, tree):
    #checks if all leafs of tree are BEs
    if len(tree)==treesize:
        for key in tree:
            if tree[key][1]!='BE':
                if len(tree[key][0])==0:
                    return False
    else:
        return False
    return True
    
def createalltreesperlayer(treesize, tree, todo, last):
    trees = []
    for nrchildren in children_list:
        newtree=copy.deepcopy(tree)
        newtree[todo][0] = list(range(last+1, last+1+nrchildren))[:] #set numbers of children
        children = newtree[todo][0]
        for nrgates in range(nrchildren+1): #set # of gates and # of basic events
            fillednewtree = copy.deepcopy(newtree)
            gatechildren = children[:nrgates]
            bechildren = children[nrgates:]
            for bc in bechildren:        
                fillednewtree[bc] = [[], 'BE']
            if nrgates==0:
                trees.append(fillednewtree)
                if len(fillednewtree) >= treesize: #tree is already too big, children don't have to become a gate
                    break
            else:
                for gatetype in gatetypes: #twice: one for each gate type
                    gatefillednewtree = copy.deepcopy(fillednewtree)
                    for gc in gatechildren:
                        gatefillednewtree[gc]=[[], gatetype]
                        trees.append(gatefillednewtree)
    return trees

def createandcheck(treesize, tree, todonext, finaltrees):
    trees = []
    last = len(tree)-1
    if len(tree)==treesize:
        res = checktree(treesize, tree)
        if res:
            if tree not in finaltrees:
                finaltrees.append(tree)
    elif len(tree) < treesize:
        trees = createalltreesperlayer(treesize, tree, todonext, last)
            
    return trees, finaltrees

# ugly
def getalltreesofsize(treesize):

    starttree = dict()
    finaltrees = []
    for gt in gatetypes:
        starttree[0] = [[], gt]
        
        trees = createalltreesperlayer(treesize, starttree, 0, 0)    
        for tree in trees:
            todo = []
            if checktree(treesize, tree):
                if tree not in finaltrees:
                    finaltrees.append(tree)
            elif len(tree) < treesize:
                for key in tree:
                    eventtype = tree[key][1]
                    children = tree[key][0]
                    if eventtype in gatetypes:
                        if len(children) == 0:
                            #this gate should be filled via createalltreesperlayer
                            todo.append(key)
                if todo:
                    trees1, finaltrees = createandcheck(treesize, tree, todo[0], finaltrees)
                    for tree1 in trees1:
                        if len(tree1) <= treesize:
                            if len(todo)>1:
                                trees2, finaltrees = createandcheck(treesize, tree1, todo[1], finaltrees)
                                for tree2 in trees2:
                                    if len(tree2) <= treesize:
                                        if len(todo) > 2:
                                            trees3, finaltrees = createandcheck(treesize, tree2, todo[2], finaltrees)
                                            for tree3 in trees3: 
                                                if len(tree3) <= treesize:
                                                    if len(todo) > 3:
                                                        trees4, finaltrees = createandcheck(treesize, tree3, todo[3], finaltrees)
                                                        for tree4 in trees4:
                                                            if len(tree4) <= treesize:
                                                                if len(todo) > 4:
                                                                    trees5, finaltrees = createandcheck(treesize, tree4, todo[4], finaltrees)
                                                                else:
                                                                    if checktree(treesize, tree4):
                                                                        if tree4 not in finaltrees:
                                                                            finaltrees.append(tree4)
                                                    else:
                                                        if checktree(treesize, tree3):
                                                            if tree3 not in finaltrees:
                                                                finaltrees.append(tree3)
                                        else:
                                            if checktree(treesize, tree2):
                                                if tree2 not in finaltrees:
                                                    finaltrees.append(tree2)
                            else:
                                if checktree(treesize, tree1):
                                    if tree1 not in finaltrees:
                                        finaltrees.append(tree1)

    # gates are switched between BEs and gates to create all possible trees
    newtrees = []
    for t in finaltrees:
        temptree = t.copy()
        if temptree[0][1] != 'BE':  # top event is gate
            topchildren = temptree[0][0]
            gates = []
            bes = []
            for child in topchildren:
                if temptree[child][1] != 'BE':
                    gates.append(child)
                else:
                    bes.append(child)
            if len(gates) > 0:
                for BE in bes:
                    for gate in gates:
                        t = temptree.copy()
                        t[BE] = temptree[gate]
                        t[gate] = temptree[BE]
                        newtrees.append(t)

    totaltrees = finaltrees + newtrees

    return totaltrees
