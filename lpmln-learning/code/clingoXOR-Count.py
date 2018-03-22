#script (python)
import clingo
import math
import random

class XOR:
    def __init__(self, literals, parity):
        assert(len(literals) > 0)
        self.__literals = literals
        self.__parity = parity

    def __getitem__(self, idx):
        return self.__literals[idx]

    def __propagate(self, assignment, p, begin=0, end=None):
        for literal in self.__literals[begin:end]:
            value = assignment.value(literal)
            if value is None:
                break
            elif value:
                p+= 1
            begin+= 1
        return (begin, p)

    def propagate(self, assignment, unassigned):
        i, p = self.__propagate(assignment, 0, begin=unassigned)
        if i == len(self.__literals):
            i, p = self.__propagate(assignment, p, end=unassigned)
        return i != unassigned or p % 2 == self.__parity, i

    def reason(self, assignment):
        clause = []
        for literal in self.__literals:
            if assignment.is_true(literal):
                clause.append(-literal)
            else:
                clause.append(literal)
        return clause

class Propagator:
    def __init__(self, s):
        self.__states = []
        self.__default_s = s.number

    def __add_watch(self, ctl, xor, unassigned, thread_ids):
        variable = abs(xor[unassigned])
        ctl.add_watch(variable)
        ctl.add_watch(-variable)
        for thread_id in thread_ids:
            self.__states[thread_id].setdefault(variable, []).append((xor, unassigned))

    def init(self, init):
        literals = [init.solver_literal(atom.literal) for atom in init.symbolic_atoms if abs(atom.literal) != 1]
        if len(literals) > 0:
            # Randomly create n XOR constraints
            if self.__default_s > 0:
                estimated_s = self.__default_s
            else:
                estimated_s = int(math.log(len(literals) + 1, 2))
            for i in range(len(self.__states), init.number_of_threads):
                self.__states.append({})
            for i in range(estimated_s):
                size = random.randint(1, (len(literals) + 1) / 2)
                lits = random.sample(literals, size)
                parity = random.randint(0,1)
                xor = XOR(lits, parity)
                self.__add_watch(init, xor, 0, range(init.number_of_threads))

    def propagate(self, control, changes):
        state = self.__states[control.thread_id]
        for literal in changes:
            variable = abs(literal)
            watches = state[variable]
            assert(len(watches) > 0)
            state[variable] = []
            ok = True
            for xor, unassigned in watches:
                if ok:
                    ok, unassigned = xor.propagate(control.assignment, unassigned)
                    self.__add_watch(control, xor, unassigned, (control.thread_id,))
                    if not ok:
                        control.add_clause(xor.reason(control.assignment))
                else:
                    state[variable].append((xor, unassigned))
            if len(state[variable]) == 0:
                control.remove_watch(variable)
                control.remove_watch(-variable)
            if not ok:
                return

def main(prg):
    s = prg.get_const("s")
    prg.ground([("base", [])])
    prg.register_propagator(Propagator(s))
    prg.solve()

#end.

%%
#const s=0.
