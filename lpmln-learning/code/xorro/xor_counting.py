#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This xor propagator actually does not interfere with clasp's propagation...
 In fact we just check (count) the number of truth's assignments given by clasp respecting the parity given for each random xor constraint generated
 In case of conflict, add the nogood and let clasp propagate again """

import math
import random

class Propagator:
    
    #########################################################################################################
    """INIT: Propagator registered"""
    def __init__(self, s):
        self.__states = []
        self.__default_s = s
        self.__approach  = "uniform"
        self.__round = 1

    #########################################################################################################
    """Starts solving with XOR constraints."""
    def init(self, init):
        Propagator.roundn = self.__round
        index = 1
        # Get solver literals
        literals = [init.solver_literal(atom.literal) for atom in init.symbolic_atoms if abs(init.solver_literal(atom.literal)) != 1]
        # Get symbols
        Propagator.symbols = {}
        for atom in init.symbolic_atoms: ## Get symbols for verbosity
            Propagator.symbols[init.solver_literal(atom.literal)] = atom.symbol
        
        if not literals:
            raise ValueError("""Encoding/Instance Error... not enough literals to create xor constraints""")
        else:
            if self.__round==1:
                ## If first round, calculate the number of constraints or use the given one
                if self.__default_s > 0:
                    estimated_s = self.__default_s
                else:
                    estimated_s = int(math.log(len(literals) + 1, 2))
            else:
                ## If round greater than one, add just a new xor constraint
                estimated_s = 1
            Propagator.number_constraints = estimated_s
            for i in range(len(self.__states), init.number_of_threads):
	        self.__states.append({})
            if self.__approach == "uniform":
                min_size = 1
                max_size = len(literals)
            ## offset value serves to add new xors with a new key on state
            offset = len(self.__states[0].keys())
            for i in range(estimated_s):
                size = random.randint(min_size, max_size)
                lits = random.sample(literals, size)
                parity = random.randint(0,1)
                for thread_id in range(init.number_of_threads):
                    self.__states[thread_id].setdefault(index + offset, []).append((lits, parity))
                index+=1
            
        Propagator.state = self.__states
        ## Update solving rounds
        self.__round +=1

    #########################################################################################################
    """Checks claps's assignments. If not satisfies xors, add nogoods"""
    def check(self, control):
        state = self.__states[control.thread_id]
        for id, xor in state.items():
            nogood     = []
            constraint = xor[0][0]
            parity     = xor[0][1]
            count      = 0

            for literal in constraint:
                if control.assignment.is_true(literal):
                    nogood.append(literal)
                    count+=1
                else:
                    nogood.append(-literal)
            if count % 2 != parity:
                if not control.add_nogood(nogood) or not control.propagate():
                    return
