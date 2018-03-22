#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Models. This Class is responsible to print the answer sets and the solving stats """

import json
import random
class Models:

    #########################################################################################################
    """ Print Results """
    def print_results(self, control, solve_result, args, models):
        #Check if n is bigger than the remaining models
        if args.models > 0 and args.models < len(models):
            selected_models = random.sample(models, args.models)
        else:
            selected_models = models

        ## Print models
        for i in range(len(selected_models)):
            print "Answer: %s"%(i+1)
            m = ' '.join(map(str, selected_models[i])) 
            print m
        
        stats = json.dumps(control.statistics, sort_keys=True, indent=4, separators=(',', ': '))
        jsonToPython = json.loads(stats)

        if solve_result.satisfiable:
            print "SATISFIABLE"
        else:
            print "UNSATISFIABLE"
        print ""
        
        if args.models > 0 and args.models < len(models):
            print "Models       : %s"%int(args.models)
        else:
            print "Models       : %s"%int(jsonToPython['summary']['models']['enumerated'])
        print "Total Models : %s"%int(jsonToPython['summary']['models']['enumerated'])
        print "Calls        : %s"%int(jsonToPython['summary']['call'])
        #Time         : 0.001s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
        time   = "%.3f"%jsonToPython['summary']['times']['total']
        solve  = "%.2f"%jsonToPython['summary']['times']['solve']
        fmodel = "%.2f"%jsonToPython['summary']['times']['sat']
        unsat  = "%.2f"%jsonToPython['summary']['times']['unsat']
        
        print "Time         : %ss (Solving: %ss 1st Model: %ss Unsat: %ss)"%(time,solve,fmodel,unsat)
        print "CPU Time     : %.3fs"%jsonToPython['summary']['times']['cpu']


    #########################################################################################################
    """ Print Stats """
    def print_stats(self, control):
        stats = json.dumps(control.statistics, sort_keys=True, indent=4, separators=(',', ': '))
        jsonToPython = json.loads(stats)
        
        print ""
        #print stats
        space = 9

        ##Choices      : 54815
        choices   =  "%s"%int(jsonToPython['solving']['solvers']['choices'])
        print "Choices      : %s"%choices
        
        ##Conflicts    : 44052    (Analyzed: 44051)
        conflicts            =  "%s"%int(jsonToPython['solving']['solvers']['conflicts'])
        conflicts_analized   =  "%s"%int(jsonToPython['solving']['solvers']['conflicts_analyzed'])
        len_conflicts = len(str(conflicts))
        print "Conflicts    : "+conflicts +"".ljust(space-len_conflicts)+ "(Analyzed: "+conflicts_analized+")"
        
        ##Restarts     : 144      (Average: 305.91 Last: 110)
        restarts        =  "%s"%int(jsonToPython['solving']['solvers']['restarts'])
        restarts_last   =  "%s"%int(jsonToPython['solving']['solvers']['restarts_last'])
        ##restarts_average = ?
        len_restarts = len(str(restarts))
        print "Restarts     : "+restarts+"".ljust(space-len_restarts)+ "(Last: "+restarts_last+")"

        ##Model-Level  : 10.5
        model_level  = "%.1f"%jsonToPython['solving']['solvers']['extra']['models_level']
        print "Model-Level  : %s"%model_level

        ##Problems     : 1        (Average Length: 0.00 Splits: 0)
        problems = 1
        print "Problems     : %s"%problems
        
        ##Lemmas       : 44051    (Deleted: 37901)
          ##Binary     : 63       (Ratio:   0.14%)
          ##Ternary    : 179      (Ratio:   0.41%)
          ##Conflict   : 44051    (Average Length:    9.3 Ratio: 100.00%) 
          ##Loop       : 0        (Average Length:    0.0 Ratio:   0.00%) 
          ##Other      : 0        (Average Length:    0.0 Ratio:   0.00%)
        lemmas           = "%s"%int(jsonToPython['solving']['solvers']['extra']['lemmas'])
        lemmas_deleted   = "%s"%int(jsonToPython['solving']['solvers']['extra']['lemmas_deleted'])
        lemmas_binary    = "%s"%int(jsonToPython['solving']['solvers']['extra']['lemmas_binary'])
        lemmas_ternary   = "%s"%int(jsonToPython['solving']['solvers']['extra']['lemmas_ternary'])
        lemmas_conflict  = "%s"%int(jsonToPython['solving']['solvers']['extra']['lemmas_conflict'])
        lemmas_loop      = "%s"%int(jsonToPython['solving']['solvers']['extra']['lemmas_loop'])
        lemmas_other     = "%s"%int(jsonToPython['solving']['solvers']['extra']['lemmas_other'])
        len_lemmas = len(str(lemmas))
        print "Lemmas       : "+lemmas+"".ljust(space-len_lemmas)+ "(Deleted: "+lemmas_deleted+")"
        print "  Binary     : "+lemmas_binary+""
        print "  Ternary    : "+lemmas_ternary+""
        print "  Conflict   : "+lemmas_conflict+""
        print "  Loop       : "+lemmas_loop+""
        print "  Other      : "+lemmas_other+""
        
        ##Backjumps    : 44051    (Average:  1.22 Max:  11 Sum:  53918)
          ##Executed   : 44051    (Average:  1.22 Max:  11 Sum:  53918 Ratio: 100.00%)
          ##Bounded    : 0        (Average:  0.00 Max:   0 Sum:      0 Ratio:   0.00%)
        backjumps          = "%s"%int(jsonToPython['solving']['solvers']['extra']['jumps']['jumps'])
        backjumps_executed = backjumps
        backjumps_bounded  = "%s"%int(jsonToPython['solving']['solvers']['extra']['jumps']['jumps_bounded'])
        print "Backjumps    : "+backjumps+""
        print "  Executed   : "+backjumps_executed+""
        print "  Bounded    : "+backjumps_bounded+""

        ##Rules        : 580      (Original: 420)
          ##Choice     : 20      
          ##Minimize   : 1
        rules          = "%s"%int(jsonToPython['problem']['lp']['rules'])
        rules_original = "%s"%int(jsonToPython['problem']['lp']['rules_normal'])
        choice_rules   = "%s"%int(jsonToPython['problem']['lp']['rules_choice'])
        minimize_rules = "%s"%int(jsonToPython['problem']['lp']['rules_minimize'])
        len_rules = len(str(rules))
        print "Rules        : "+rules+"".ljust(space-len_rules)+ "(Original: "+rules_original+")"
        print "  Choice     : "+choice_rules+""
        print "  Minimize   : "+minimize_rules+""
        
        ##Atoms        : 370
        atoms = "%s"%int(jsonToPython['problem']['lp']['atoms'])
        print "Atoms        : "+atoms+""
        
        ##Bodies       : 221      (Original: 160)
          ##Count      : 20       (Original: 40)
        bodies                = "%s"%int(jsonToPython['problem']['lp']['bodies_tr'])
        bodies_count          = "%s"%int(jsonToPython['problem']['lp']['count_bodies_tr'])
        bodies_original       = "%s"%int(jsonToPython['problem']['lp']['bodies'])
        bodies_count_original = "%s"%int(jsonToPython['problem']['lp']['count_bodies'])
        len_bodies = len(str(bodies))
        len_bodies_count = len(str(bodies_count))
        print "Bodies       : "+bodies+"".ljust(space-len_bodies)+ "(Original: "+bodies_original+")"
        print "  Count      : "+bodies_count+"".ljust(space-len_bodies_count)+ "(Original: "+bodies_count_original+")"

        ##Equivalences : 150      (Atom=Atom: 20 Body=Body: 0 Other: 130)
        equivalences       = "%s"%int(jsonToPython['problem']['lp']['eqs'])
        equivalences_atom  = "%s"%int(jsonToPython['problem']['lp']['eqs_atom'])
        equivalences_body  = "%s"%int(jsonToPython['problem']['lp']['eqs_body'])
        equivalences_other = "%s"%int(jsonToPython['problem']['lp']['eqs_other'])
        len_equivalences = len(str(equivalences))
        print "Equivalences : "+equivalences+"".ljust(space-len_equivalences)+ "(Atom=Atom: "+equivalences_atom+" Body=Body: "+equivalences_body+" Other: "+equivalences_other+")" 
        
        ##Tight        : No       (SCCs: 1 Non-Hcfs: 0 Nodes: 109 Gammas: 0)
        tight = ""
        sccs     = "%s"%int(jsonToPython['problem']['lp']['sccs'])
        if int(sccs) == 0:
            tight    = "Yes"
        else:
            tight    = "No"
        non_hcf  = "%s"%int(jsonToPython['problem']['lp']['sccs_non_hcf'])
        nodes    = "%s"%int(jsonToPython['problem']['lp']['ufs_nodes'])
        gammas   = "%s"%int(jsonToPython['problem']['lp']['gammas'])
        len_tight = len(str(tight))
        print "Tight        : "+tight+"".ljust(space-len_tight)+ "(SCCs: "+sccs+" Non-Hcfs: "+non_hcf+" Nodes: "+nodes+" Gammas: "+gammas+")"
        
        ##Variables    : 210      (Eliminated:    0 Frozen:  190)
        variables            = "%s"%int(jsonToPython['problem']['generator']['vars'])
        variables_eliminated = "%s"%int(jsonToPython['problem']['generator']['vars_eliminated'])
        variables_frozen     = "%s"%int(jsonToPython['problem']['generator']['vars_frozen'])
        len_variables = len(str(variables))
        print "Variables    : "+variables+"".ljust(space-len_variables)+ "(Eliminated: "+variables_eliminated+" Frozen: "+variables_frozen+")"
        
        ##Constraints  : 230      (Binary:  78.3% Ternary:   0.0% Other:  21.7%)
        constraints            = "%s"%int(jsonToPython['problem']['generator']['constraints'])
        #constraints_binary
        #constraints_ternary
        #constraints_other
        print "Constraints  : "+constraints+""

        
    #########################################################################################################
    """ Print State with clasp literals """
    def print_state(self, state):
        print "************** xor with clasp solving literals ***********"
        for line in state:
            for constraint_id, constraint in line.items():
                print constraint[0][0], constraint[0][1]


    #########################################################################################################
    """ Print XOR constraints as count aggregates and theory atoms """
    def print_aggregates(self, state, symbols):
        constr = []
        parity = []
        for line in state:
            for constraint_id, constraint in line.items():
                parity.append(constraint[0][1])
                lits = []
                for literal in constraint[0][0]:
                    lits.append(symbols[literal])
                constr.append(lits)           
       
        for i in range(len(constr)):
            for j in range(len(constr[i])):
                terms = "%s:%s"%(constr[i][j],constr[i][j])
                constr[i][j] = terms

        theory_atoms  = ""
        integr_constr = ""
        for i in range(len(constr)):
            terms = " ; ".join(str(x) for x in constr[i])
            text_parity = ""
            if parity[i] == 1:
                text_parity = "odd"
            else:
                text_parity = "even"
            theory_atoms  += "&%s{ %s }. \n"%(text_parity, terms)
            integr_constr += ":- N = #count{ %s }, N\\2!=%s. \n"%(terms, parity[i])
        print "************** theory atoms xor constraints **************"
        print theory_atoms[:-2]
        print "************** integrity count constraints  **************"
        print integr_constr[:-2]
                    
