# xorro

[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/flavioeverardo/xorro_clingo5)

> A tool for generating (near-)uniform answers from Answer Set programs.

## Description
`xorro` is a tool that takes advantage of properties of random parity (XOR) constraints to cut through the search space towards near-uniformity solutions.
This consist of calculating a few answer sets representative for all the search space. This is particularly useful if the computation of all answers is practically infeasible.

A fully re-implemented and extended version of the original `xorro` prototype. This new version is built under clingo 5 infrastructure with Python support enhancing Answer Set Programming (ASP) with parity reasoning through a theory propagator.
This propagator is responsible to create "s" random XOR constraints to cluster the search space. 


## Table of Contents

- [Requirements](#requirements)
- [Install](#install)
- [Usage](#usage)
- [Contributors](#contributors)
- [License](#license)


## Requirements

This second series of `xorro` is tested under Unix systems (Ubuntu 16.04 LTS 64-bits, Debian GNU/Linux 8, 64-bits and MacOS 10.13.2 High Sierra 64-bits) with clingo 5.2.2 installed in the `PYTHONPATH` with Python support, tested with version 2.7.
* On Mac, you can download the corresponding [clingo release](https://github.com/potassco/clingo/releases/download/v5.2.2/clingo-5.2.2-macos-10.9.tar.gz), drag and drop the binaries including the clingo.so for Python under `usr/local/bin/`. To access clingo's API, drag and drop `clingo.so` file into `./Library/Python/2.7/site-packages/`.
* On Linux, you can download the [source code](https://github.com/potassco/clingo/archive/v5.2.2.tar.gz), build it following the instructions in `INSTALL.md`.


## Install

`xorro` sources can be downloaded as .zip file or cloned with `git clone https://github.com/flavioeverardo/xorro.git`.
Installation module still in progress.


## Usage
```bash
$ python xorro.py [files] [number] [options]
```

Default command-line
```bash
$ python xorro.py --models=1 --s=0 --verbose=1
```

`xorro` Options:

| command | description |
|---|---|
| `--s <n>` | Number of xor constraints to generate. Default=0, calculated automatically by **log(#atoms)**. |
| `--incremental` | Incremental solving adding new xor constraint in the next call. |
| `--iterative` | Runs until satisfiability. By default, the non-iterative approach can return UNSATISFIABLE. |
| `--verbose <n>` | Enable verbosity according to the given level. Default=1, values from 0-3. |
| `--version, -v` | Display version information. |
| `--help, -h` | Display help message. |


Current `clingo` Options:

| command | description |
|---|---|
| `--models, -n <n>` | Compute at most <n> models (0 for all). |
| `--stats` | Enable solving statistics. |

**Remarks** Currently not supported programs with optimizing statements. `--opt-mode=ignore` is executed by default.


## Examples

Having a simple encoding file consisting of a choice rule:
```
{a;b;c;d}.
```
This results in 16 different answers when enumerating all from clasp. To generate a sample of answers from the search space, we can give the following command:
```bash
python xorro.py encoding.lp --s=0 --models=4 --verbose=0
```
This command asks for 4 models, let xorro to estimate the number of xor constraints to use and enables verbosity level to all. An example of the output is the following:
```bash
Reading from encoding.lp    
Solving...
xor constraints: 2
************** xor with clasp solving literals ***********
[3L, 4L, 5L, 2L] 1
[5L, 3L] 0
************** theory atoms xor constraints **************
&odd{ b:b ; c:c ; d:d ; a:a }. 
&even{ d:d ; b:b }.
************** integrity count constraints  **************
:- N = #count{ b:b ; c:c ; d:d ; a:a }, N\2!=1. 
:- N = #count{ d:d ; b:b }, N\2!=0.

Answer: 1
c
Answer: 2
b c d
Answer: 3
a
Answer: 4
a b d
SATISFIABLE

Models       : 4
Total Models : 4
Calls        : 0
Time         : 0.004s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.000s
```

The output is the usual clingo's format, plus two additional attributes. The first one displays the number of XOR constraints used, being user-defined or internally estimated and is shown in the solving step. The second is called `Total Models` which displays the remaining models after solving with `--s` xor constraints.


The verbosity text shows three representation of the xor constraints used.
* The first one is the constraints built with clasp's literals as a list followed by a 0 or 1 depending on the parity.
* The second and third are output to work directly with ASP. The theory atoms are suited to work with theory propagators (coming soon...) and the integrity constraints with the count aggregate are ready to include them into the encoding to replicate the same results.

This output enumerates the 4 answers asked but also indicates that after applying the xor constraints, there are only 4 answers remaining shown by Total Models.

Similarly, if we decrease the number of answers or models to 3, we can see that after solving with the xor constraints, there are 4 answers remaining and ramdonly xorro give us 3.
```bash
Reading from encoding.lp    
Solving...
xor constraints: 2
************** xor with clasp solving literals ***********
[3L, 2L, 4L, 5L] 1
[4L] 1
************** theory atoms xor constraints **************
&odd{ b:b ; a:a ; c:c ; d:d }. 
&odd{ c:c }.
************** integrity count constraints  **************
:- N = #count{ b:b ; a:a ; c:c ; d:d }, N\2!=1. 
:- N = #count{ c:c }, N\2!=1.

Answer: 1
a b c
Answer: 2
b c d
Answer: 3
a c d
SATISFIABLE

Models       : 3
Total Models : 4
Calls        : 0
Time         : 0.003s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.004s
```

Another way to run xorro is by enabling the `--incremental` flag, allowing several calls to the solver by adding new xor constraints. An example of the output is:
```bash
python xorro.py encoding.lp --s=2 --models=1 --verbose=3 --incremental
Reading from encoding.lp    
Incremental Solving...
round 1:
************** theory atoms xor constraints **************
&odd{ b:b ; a:a ; c:c ; d:d }. 
&odd{ c:c ; b:b ; a:a ; d:d }.
************** integrity count constraints  **************
:- N = #count{ b:b ; a:a ; c:c ; d:d }, N\2!=1. 
:- N = #count{ c:c ; b:b ; a:a ; d:d }, N\2!=1.

round 2:
************** theory atoms xor constraints **************
&even{ d:d ; c:c ; b:b }.
************** integrity count constraints  **************
:- N = #count{ d:d ; c:c ; b:b }, N\2!=0.

round 3:
************** theory atoms xor constraints **************
&odd{ d:d ; b:b }.
************** integrity count constraints  **************
:- N = #count{ d:d ; b:b }, N\2!=1.

round 4:
************** theory atoms xor constraints **************
&odd{ d:d }.
************** integrity count constraints  **************
:- N = #count{ d:d }, N\2!=1.

----------------------------------------------------------
----------------------------------------------------------
total rounds: 4
total xor constraints used: 5
************** theory atoms xor constraints **************
&odd{ b:b ; a:a ; c:c ; d:d }. 
&odd{ c:c ; b:b ; a:a ; d:d }. 
&even{ d:d ; c:c ; b:b }. 
&odd{ d:d ; b:b }. 
&odd{ d:d }.
************** integrity count constraints  **************
:- N = #count{ b:b ; a:a ; c:c ; d:d }, N\2!=1. 
:- N = #count{ c:c ; b:b ; a:a ; d:d }, N\2!=1. 
:- N = #count{ d:d ; c:c ; b:b }, N\2!=0. 
:- N = #count{ d:d ; b:b }, N\2!=1. 
:- N = #count{ d:d }, N\2!=1.

Answer: 1
a c d
SATISFIABLE

Models       : 1
Total Models : 1
Calls        : 3
Time         : 0.000s (Solving: 0.00s 1st Model: 0.00s Unsat: 0.00s)
CPU Time     : 0.000s
```
Here, xorro started the solving with 2 xor constraints given in step 1, and every round a new xor constraint is added (step 2-4). Afterwards, the number of rounds and xor constraints needed are displayed followed by the output of the solver.

**Remarks** So far the stats displayed with the incremental mode are from the last solve call. 


Finally, is also possible to run several files (encoding and instance). To do so, an example command can be:
```bash
$ python xorro.py encoding.lp instance.lp --models=1 --s=6 --iterative
```
Here it is enabled the iterative mode where clasp will solve the programs with 3 xor constraints and trying to get 4 models. If the run is UNSATISFIABLE, xorro will keep launching (fresh start) clingo with new xor constraints until at least one answer is found. When the solving returns SATISFIABLE, xorro will return also the total number of rounds needed.


## Contributors

* Flavio Everardo - Get help/report bugs via flavio.everardo@cs.uni-potsdam.de
The original prototype of `xorro` was implemented by Marius Lindauer.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
