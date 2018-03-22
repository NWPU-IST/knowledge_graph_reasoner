# lpmln-learning

The LPMLN learning system is a tool for weight learning in LPMLN programs. It is a collection of Python scripts that execute gradient ascent based learning with a MC-SAT like sampling method called MC-ASP, based on Clingo and lpmln2asp.

The language LPMLN is an extension of Answer Set Programming (ASP) where each ASP rule can be associated with a weight, which roughly indicates how important the rule is. It extends ASP with a possible world semantics, and allows probabilistic informataion to be expressed in ASP. It was proposed in the paper Weighted Rules under the Stable Model Semantics.

The system relies on xorro, a uniform sampler for ASP programs, available here: https://github.com/flavioeverardo/xorro/
(Please copy the all xorro files to code/xorro under lpmln-learn folder)

For usage of the system, see https://lpmln-learn.weebly.com/uploads/7/9/0/9/7909467/usage.pdf
