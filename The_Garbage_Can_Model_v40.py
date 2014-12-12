print '''
This is a ver 4.0 of the Garbage Can Model (Cohen, March, Olsen, 1972)
This model allows cycling over all scenarios
and 100 iterations and over parameter space.

This would be the final version of the GCM.

-----------------------------
Maciej Workiewicz 2014

'''
import random as rnd
import numpy as np
import xlwt

# ver 3.1 added a new specification of the summary stats
# ver 4.0 general cleaning of the code

#Original inputs
periods = 20  # time periods (20)
v = 10  # number of members: time series of available energy (10)
m = 10  # number of choices: entry time, list of participants (10)
# eligible to make the decision
w = 20  # number of problems: entry time, energy requirement,
# list of choices (20)
sol_coeff = .6  # solution coefficent (from 0 to 1) (0.6)
#energy available (5.5)
Net_energy_load = np.array([1.1, 2.2, 3.3])  # three scenarios for NEL
iterations = 100  # iterations, with 100 it takes about 5 min to complete
'''
mapping problems onto choices w by m array with 1 if
choice is accessible to the ith problem
'''
A0 = np.ones((w, m))
A1 = np.zeros((w, m))
A2 = np.zeros((w, m))
counter_1 = -1
for a1 in np.arange(w):
    if a1 % 2 == 0:  # if divisible by 2 i.e. a1 is even number
        counter_1 = counter_1 + 1
    A1[a1, counter_1:m] = 1
    A2[a1, counter_1] = 1
A_matrix = np.zeros((3, w, m))
A_matrix[0] = A0  # full access
A_matrix[1] = A1  # triangluar
A_matrix[2] = A2  # diagonal
'''
decision structure,  by m array with 1 for yes, 0 for no
mapping of chocies to decision makers -> the decision structure
'''
D0 = np.ones((v, m))  # decision structure
D1 = np.zeros((v, m))
D2 = np.zeros((v, m))
for a2 in np.arange(v):
    D1[a2, a2:m] = 1
    D2[a2, a2] = 1

D_matrix = np.zeros((3, v, m))
D_matrix[0] = D0  # full
D_matrix[1] = D1  # triangular
D_matrix[2] = D2  # diagonal

# Energy distribution among members,v vector
E0 = np.arange(0.1, 1.1, 0.1)*sol_coeff
E1 = np.ones(m)*.55*sol_coeff
E2 = np.arange(1, 0, -.1)*sol_coeff
Energy = np.zeros((3, v))
Energy[0] = E0  # increasing
Energy[1] = E1  # equal
Energy[2] = E2  # decreasing

'''
Key behavioral assumptions
1. energy additivity = sum of all energies devoted to problems
deflated by sol_coeff
2. Energy allocation assumption: each participant can participate in no
more than than one choice at the time with the lowest energy deficit
3. Problem allocation assumption: one problem attached to no more
than one choice at the time to closest to decision
'''


def garbage_can(A, D, E, nel, Entry_m, Entry_w):
    '''
    Setting the initial values
    '''
    Problems = np.zeros((w, periods+1))-2
    # mapping of problems onto choices
    Choices = np.zeros((m, periods+1))-2
    # mapping of choices onto members
    Members = np.zeros((v, periods+1))-1
    # mapping members onto choices
    #-2: not active, -1: active not attached

    '''
    Resolution: choices work on problems before the problem is solved
    Oversight: choices are made without problems attached to them
    Flight: problems switch to a more attractive choice making a decision
    possible
    '''
    Choices_energy_required = np.zeros((m, periods+1))
    Choices_energy_spent = np.zeros((m, periods+1))
    for t in np.arange(periods):  # t+1 is present
        # carrying data from previous
        Choices[:, t+1] = Choices[:, t].copy()
        Problems[:, t+1] = Problems[:, t].copy()
        Members[:, t+1] = Members[:, t].copy()
        # activating choices
        if t < 10:
            Choices[Entry_m[t], t+1] = -1  # active, not attached
        #activating problems
            Problems[Entry_w[2*t], t+1] = -1  # active, not attached
            Problems[Entry_w[(2*t)+1], t+1] = -1

        #What is the distribution of energy deficits

        Choices_energy_required_calc = np.zeros(m)
        # to capture energy required, zeroed each round

        # Find most attractive choice for problems
        Choices_energy_spent_calc = Choices_energy_spent[:, t].copy()
        # previous stock of energy

        for b1 in np.arange(w):  # cycle over problems
            if Problems[b1, t+1] > -2 and Problems[b1, t+1] < 90:
            # if active and not completed
                # which applicable
                Indexes = []
                Values = []
                for b2 in np.arange(m):  # search for applicable choices
                    if A[b1, b2] == 1 and Choices[b2, t+1] > -2:
                        Indexes.append(b2)
                        Values.append(Choices_energy_required[b2, t] -
                                      Choices_energy_spent[b2, t])
                        # here t not t+1 because it is the last round's deficyt
                if len(Values) > 0:
                    min_deficyt = np.argmin(Values)
                    best_choice_index = Indexes[min_deficyt]
                    Problems[b1, t+1] = best_choice_index
                    Choices_energy_required_calc[best_choice_index] = \
                        Choices_energy_required_calc[best_choice_index] + nel
                else:
                    Problems[b1, t+1] = -1  # active but not attached

        Choices_energy_required[:, t+1] = Choices_energy_required_calc

        #find most attractive choice for decision maker
        for c1 in np.arange(v):  # cycle over decision makers
            # which applicable
            Indexes = []
            Values = []
            for c2 in np.arange(m):  # search for applicable choices
                if D[c1, c2] == 1 and Choices[c2, t+1] > -2:
                    Indexes.append(c2)
                    Values.append(Choices_energy_required[c2, t] -
                                  Choices_energy_spent[c2, t])
            if len(Values) > 0:
                min_deficyt = np.argmin(Values)
                best_choice_index = Indexes[min_deficyt]
                Members[c1, t+1] = best_choice_index
                Choices_energy_spent_calc[best_choice_index] =\
                    Choices_energy_spent_calc[best_choice_index] + E[c1]
            else:
                Members[c1, t+1] = -1  # active but not attached
        Choices_energy_spent[:, t+1] = Choices_energy_spent_calc

        # establishing energy required for choices
        Choices_energy_net = Choices_energy_required_calc -\
            Choices_energy_spent_calc

        #make choices
        for d1 in np.arange(m):  # over choices
            if Choices_energy_net[d1] <= 0 and Choices[d1, t+1] != -2:
                Choices[d1, t+1] = -3
                # now close problems that were attached
                for d2 in np.arange(w):  # over problems
                    if Problems[d2, t+1] == d1:
                        Problems[d2, t+1] = Problems[d2, t+1] + 100
                        # Problem solved
    return(Choices, Problems, Members, Choices_energy_required,
           Choices_energy_spent)

Output = np.zeros((81, 4 + 14))  # to capture the results, 4 for markers
count_1 = 0

# SIMULATION
for x1 in np.arange(3):  # Net energy dist: 1.1, 2.2, 3.3
    for x2 in np.arange(3):  # Energy dist: increasing, equall, decreasing
        for x3 in np.arange(3):  # problem access A: all, triangular, diagonal
            for x4 in np.arange(3):  # D: choices to dec. mkrs: all, tri, diag
                Resolutions = np.zeros(iterations)  # to capture the data
                Oversights = np.zeros(iterations)
                Flights = np.zeros(iterations)
                Quickies = np.zeros(iterations)
                Prob_unsolved = np.zeros(iterations)
                Prob_shifts = np.zeros(iterations)
                Prob_active = np.zeros(iterations)
                Prob_latency = np.zeros(iterations)
                Dm_active = np.zeros(iterations)
                Dm_shifts = np.zeros(iterations)
                Energy_spent = np.zeros(iterations)
                Energy_excess = np.zeros(iterations)
                Choices_unsolved = np.zeros(iterations)
                Choices_active = np.zeros(iterations)

                nel = Net_energy_load[x1]
                E = Energy[x2]
                A = A_matrix[x3]
                D = D_matrix[x4]

                for i101 in np.arange(iterations):
                    '''
                    I also included the original random numbers from the
                    Cohen et al. 1972 paper
                    '''
                    # one choice per period for first 10 periods
                    # Entry_m1 = np.array([10, 7, 9, 5, 2, 3, 4, 1, 6, 8])
                    # original choice
                    # Entry_m2 = np.array([6, 5, 2, 10, 8, 9, 7, 4, 1, 3])
                    # original choice

                    Entry_m1 = np.arange(10)
                    rnd.shuffle(Entry_m1)
                    '''
                    # two problems per period for first 10 periods
                    Entry_w1 = np.array([8, 20, 14, 16, 6, 7, 15, 17, 2, 13,
                                         11, 19, 4, 9, 3, 12, 1, 10, 5, 18])
                    Entry_w2 = np.array([4, 14, 11, 20, 3, 5, 2, 12, 1, 6, 8,
                                        19, 7, 15, 16, 17, 10, 18, 9, 13])
                    '''
                    Entry_w1 = np.arange(20)
                    rnd.shuffle(Entry_w1)

                    Choices, Problems, Members, Choices_energy_required,\
                        Choices_energy_spent =\
                        garbage_can(A, D, E, nel, Entry_m1, Entry_w1)

                    # Summary statistics: Decision Style
                    # 1. Resolution: choices work on problems before the
                    #   problem is solved

                    resolutions = 0

                    for e1 in np.arange(m):  # over choices
                        for e2 in np.arange(2, periods+1, 1):
                            if Choices[e1, e2] == -3 and Choices[e1, e2-1] ==\
                                    -1 and Choices[e1, e2-2] == -1:
                                resolutions = resolutions + 1

                    #2. Oversight: choices are made without problems
                    #   attached to them
                    oversights = 0
                    Prob_choice = np.arange(w)  # which choic. solved the prob
                    for e3 in np.arange(w):  # over problems
                        Prob_choice[e3] = Problems[e3, periods] - 100

                    for e4 in np.arange(m):  # over choices
                        e5 = e4 in Prob_choice
                        # has the chocie solved even one problem?
                        if Choices[e4, periods] == -3 and e5 is False:
                                oversights = oversights + 1

                    #3. Flight: problems switch to a more attractive choice
                    #   making a decision possible
                    flights = 0
                    for e11 in np.arange(m):  # over choices
                        for e12 in np.arange(1, periods + 1, 1):
                            if Choices[e11, e12] == -3 and\
                                    Choices[e11, e12 - 1] == -1:
                                if Choices_energy_required[e11, e12] <\
                                         Choices_energy_required[e11, e12 - 1]:
                                    flights = flights + 1

                    #4. Quickie: done immediatelly (I added that one)
                    quickies = 0
                    for e13 in np.arange(m):  # over choices
                        for e14 in np.arange(1, periods+1, 1):
                            if Choices[e13, e14] == -3 and\
                                    Choices[e13, e14-1] == -2:
                                quickies = quickies + 1

                    #Problem activity
                    #1. Number fo problems unsolved at the end
                    prob_unsolved = 0
                    for f11 in np.arange(w):  # over problems
                        if Problems[f11, periods] < 90:
                            prob_unsolved = prob_unsolved + 1
                    #2. Number of shifts from one choice to another
                    #3. Number of periods that a problem is active and
                    #   attached over all problems
                    #4. Problem latency: problem active but not attached
                    prob_shifts = 0
                    prob_active = 0
                    prob_latency = 0
                    for f1 in np.arange(w):  # over problems
                        for f2 in np.arange(1, periods+1, 1):
                            if Problems[f1, f2] > -1 and Problems[f1, f2-1]\
                                    > -1 and Problems[f1, f2] < 90 and\
                                    Problems[f1, f2-1] != Problems[f1, f2]:
                                prob_shifts = prob_shifts + 1
                            if Problems[f1, f2] > -1 and\
                                    Problems[f1, f2] < 90:
                                prob_active = prob_active + 1
                            elif Problems[f1, f2] == -1:
                                prob_latency = prob_latency + 1

                    #4. Problem latency: problem active but not attached

                    #Summary statistics: Decision Maker activity
                    #1. Number of periods DM active and attached
                    #2. Number of decision makers shifting to other decisions
                    dm_active = 0
                    dm_shifts = 0
                    for g1 in np.arange(v):  # over decision makers
                        for g2 in np.arange(1, periods + 1, 1):
                            if Members[g1, g2] > -1:
                                dm_active = dm_active + 1
                            if Members[g1, g2] > -1 and Members[g1, g2 - 1] >\
                                    -1 and Members[g1, g2-1] !=\
                                    Members[g1, g2]:
                                dm_shifts = dm_shifts + 1

                    #3. Energy spent
                    energy_spent = 0
                    for h1 in np.arange(m):  # over choices
                        for h2 in np.arange(periods):
                            energy_spent = energy_spent +\
                                Choices_energy_spent[h1, h2+1] -\
                                Choices_energy_spent[h1, h2]
                    #4 Energy in excess
                    energy_excess = 0
                    for h3 in np.arange(m):  # over choices
                        for h4 in np.arange(periods):
                            if Choices[h3, h4] != -3 and\
                                    Choices[h3, h4 + 1] == -3:
                                energy_excess = energy_excess +\
                                    Choices_energy_spent[h3, h4 + 1] -\
                                    Choices_energy_required[h3, h4 + 1]

                    #Summary statistics: decision difficulty
                    choices_unsolved = 0
                    choices_active = 0
                    for i1 in np.arange(m):  # over choices
                        if Choices[i1, periods] != -3:
                            choices_unsolved = choices_unsolved + 1
                        for i2 in np.arange(periods+1):
                            if Choices[i1, i2] == -1:
                                choices_active = choices_active + 1

                    Resolutions[i101] = float(resolutions)
                    Oversights[i101] = float(oversights)
                    Flights[i101] = float(flights)
                    Quickies[i101] = float(quickies)
                    Prob_unsolved[i101] = float(prob_unsolved)
                    Prob_shifts[i101] = float(prob_shifts)
                    Prob_active[i101] = float(prob_active)
                    Prob_latency[i101] = float(prob_latency)
                    Dm_active[i101] = float(dm_active)
                    Dm_shifts[i101] = float(dm_shifts)
                    Energy_spent[i101] = float(energy_spent)
                    Energy_excess[i101] = float(energy_excess)
                    Choices_unsolved[i101] = float(choices_unsolved)
                    Choices_active[i101] = float(choices_active)

                resolutions_mean = np.mean(Resolutions)
                oversights_mean = np.mean(Oversights)
                flights_mean = np.mean(Flights)
                quickies_mean = np.mean(Quickies)
                prob_unsolved_mean = np.mean(Prob_unsolved)
                prob_shifts_mean = np.mean(Prob_shifts)
                prob_active_mean = np.mean(Prob_active)
                prob_latency_mean = np.mean(Prob_latency)
                dm_active_mean = np.mean(Dm_active)
                dm_shifts_mean = np.mean(Dm_shifts)
                energy_spent_mean = np.mean(Energy_spent)
                energy_excess_mean = np.mean(Energy_excess)
                choices_unsolved_mean = np.mean(Choices_unsolved)
                choices_active_mean = np.mean(Choices_active)

                print 'En_load ' + str(x1) + ' En_dist ' + str(x2) + \
                      ' P-C ' + str(x3) + ' C-DM ' + str(x4) + ' Completed'

                Output[count_1, 0] = x1  # Net energy load
                Output[count_1, 1] = x2  # Energy distribution
                Output[count_1, 2] = x3  # Problems to choices
                Output[count_1, 3] = x4  # Choices to decision makers

                Output[count_1, 4] = resolutions_mean
                Output[count_1, 5] = oversights_mean
                Output[count_1, 6] = flights_mean
                Output[count_1, 7] = quickies_mean
                Output[count_1, 8] = prob_unsolved_mean
                Output[count_1, 9] = prob_shifts_mean
                Output[count_1, 10] = prob_active_mean
                Output[count_1, 11] = prob_latency_mean
                Output[count_1, 12] = dm_active_mean
                Output[count_1, 13] = dm_shifts_mean
                Output[count_1, 14] = energy_spent_mean
                Output[count_1, 15] = energy_excess_mean
                Output[count_1, 16] = choices_unsolved_mean
                Output[count_1, 17] = choices_active_mean

                count_1 = count_1 + 1

file_name = file_name = 'D:\Output\garbage_can_v_40.xls'

wbk = xlwt.Workbook()
sheet1 = wbk.add_sheet('sheet1')
for row1 in np.arange(81):
    for col1 in np.arange(4+14):
        sheet1.write(row1, col1, Output[row1, col1])
wbk.save(str(file_name))

print "Done"
