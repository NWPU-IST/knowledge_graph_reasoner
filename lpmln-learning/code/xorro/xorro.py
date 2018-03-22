#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Xorro with clingo 5 python API. """

import sys
import clingo
import argparse
import random
import textwrap
from xor_counting import Propagator
from models import Models

models = []
number_constraints = 0

#########################################################################################################
""" Parse Arguments """
def parse_params():
    parser = argparse.ArgumentParser(prog='xorro.py',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     description=textwrap.dedent('''\
A tool for generating (near-)uniform answer sets of a logic program.
Default command-line: python xorro.py encoding.lp --models=1 --s=0 --verbose=1
                                     '''),

                                     usage='python %(prog)s [files] [number] [options]',
                                     epilog=textwrap.dedent('''\
xorro is part of Potassco Labs: https://potassco.org/labs/
Get help/report bugs via : flavio.everardo@cs.uni-potsdam.de
                                     '''),)


    # Basic Xorro Options
    basic_args = parser.add_argument_group("Basic Xorro Options")
    basic_args.add_argument('--version', '-v', action='version', version='%(prog)s 2.0.0')
    basic_args.add_argument("--s", type=int, default=0,
                        help="Number of xor constraints to generate. Default=0, log(#atoms)")
    basic_args.add_argument('input', nargs='*', help=argparse.SUPPRESS)
    basic_args.add_argument("--iterative", action='store_true',
                        help="Runs until satisfiability.")
    basic_args.add_argument("--incremental", action='store_true',
                        help="Incremental solve of xor constraints towards given number of models")
    basic_args.add_argument("--verbose", type=int, default=1, choices=[0,1,2,3],
                        help='''\
Set verbosity level:
0: Print all status messages
1: Default basic information printing
2: Clasp's literals and parity used in xor constraints
3: Xor constraints as count aggregates and theory atoms
                                     ''')

    # Clingo Options
    clingo_args = parser.add_argument_group("Clingo Options")
    clingo_args.add_argument('--models', '-n', type=int, default=1, nargs='?',
                        help="Compute at most <n> models (0 for all)")
    clingo_args.add_argument("--stats", action='store_true',
                        help="Enable solving statistics")
    
    
    return parser.parse_args()

#########################################################################################################
"""Checks consistency wrt. related command line args."""
def check_input(arguments):
    models_requested = [int(n) for n in arguments.input if n.isdigit()]
    if models_requested:
        arguments.models = models_requested[0]
    else:
        models_requested = [1]
    
    ## Check errors
    if len(models_requested) > 1:
        raise ValueError("""Multiple occurrences of models""")
    if len(arguments.input) == 0:
        raise ValueError("""No encoding or number of models found""")
    if arguments.models < 0 or not models_requested:
        raise ValueError("""Number of answers requested cannot be negative""")
    if arguments.s < 0:
        raise ValueError("""Number of xor constraints requested cannot be negative""")
    
#########################################################################################################
""" Main """
def main():
    ## Global variables
    global models
    global number_constraints
    xor_constraints = 0
    total_rounds = 0
    current_state_key = 0
    
    ## Parse input data
    args = parse_params()

    ## Check for input errors
    check_input(args)
    programs = []
    for in_file in args.input:
        try:
            int(in_file)
        except ValueError:
            programs.append(in_file)

    #print args
    #print programs
    
    ## Create clingo object
    round_num = 1
    while True:
        control = clingo.Control()
        control.cleanup()
        control.configuration.solve.models = 0
        control.configuration.solve.opt_mode = "ignore"
        if args.stats:
            control.configuration.stats=1
        for program in programs:
            control.load(program)
        control.ground([("base", [])])

        if round_num == 1:
            if len(programs) > 1:
                print "Reading from %s ..."%programs[0]
            else:
                print "Reading from %s    "%programs[0]
            if args.incremental:
                print "Incremental Solving..."
            else:
                print "Solving..."
        ## Initial solvinig... only solving call if not incremental or non iterative
        control.register_propagator(Propagator(args.s))
        solve_result = control.solve(None, lambda model: models.append(model.symbols(shown=True)))
        
            
        ## If incremental flag is on
        if args.incremental and solve_result:
            ## Get info from round 1 if verbosity 0, 2 or 3 
            if args.incremental:
                ## Get xor constraints and solving rounds
                xor_constraints = Propagator.number_constraints
                total_rounds = Propagator.roundn
                if args.verbose != 1:                
                    print "round %s:"%total_rounds
                if args.verbose == 0 or args.verbose == 2:
                    Models().print_state(Propagator.state)
                if args.verbose == 0 or args.verbose == 3:
                    Models().print_aggregates(Propagator.state, Propagator.symbols)
                ## Get the last key from state
                current_state_key = len(Propagator.state[0].keys())
            
            ## For round 2 or more
            while True: ## While True until the search space is cut enough
                if len(models) >= int(args.models)*2:
                    del models[:]
                    ## Additional solve calls for incremental xor
                    solve_result = control.solve(None, lambda model: models.append(model.symbols(shown=True)))
                    ## Get xor constraints and solving rounds
                    xor_constraints += Propagator.number_constraints
                    total_rounds = Propagator.roundn
                    ## Update the last key from state
                    current_state_key += 1
                    if args.verbose != 1:
                        print ""
                        print "round %s:"%total_rounds
                    if args.verbose == 0 or args.verbose == 2:
                        last_state = {}
                        last_state[current_state_key] = Propagator.state[0][current_state_key]
                        Models().print_state([last_state])
                    if args.verbose == 0 or args.verbose == 3:
                        last_state = {}
                        last_state[current_state_key] = Propagator.state[0][current_state_key]
                        Models().print_aggregates([last_state], Propagator.symbols)
                else:
                    break
        
        if args.iterative == False:
            #print "do not check sat!!!!!!!!"
            break
        elif args.iterative == True:
            if solve_result.satisfiable:
                print "total rounds: %s"%round_num
                break
            else: round_num+=1

    if args.incremental and args.verbose != 1:
        print ""
        print "----------------------------------------------------------"
        print "----------------------------------------------------------"
    
    if args.incremental:
        print "total rounds: %s"%total_rounds
        print "total xor constraints used: %s"%xor_constraints
    else:
        print "xor constraints: %s"%Propagator.number_constraints
    state   = Propagator.state
    symbols = Propagator.symbols
    if args.verbose == 0:
        Models().print_state(state)
        Models().print_aggregates(state, symbols)
        print ""
        Models().print_results(control, solve_result, args, models)
        
    elif args.verbose == 1:
        Models().print_results(control, solve_result, args, models)
        
    elif args.verbose == 2:
        Models().print_state(state)
        print ""
        Models().print_results(control, solve_result, args, models)

    elif args.verbose == 3:
        Models().print_aggregates(state, symbols)
        print ""
        Models().print_results(control, solve_result, args, models)
        
        
    if args.stats:
        Models().print_stats(control)

    #if args.incremental:
    #    print "check average solving stats and not only the last one!!!!!!"
            

#########################################################################################################
if __name__ == '__main__':
    sys.exit(main())					      
