import random, csv, math
from copy import deepcopy

''' REMEMBER!!!
        Python tends to pass everything by reference.
        When translating this to Java, I need to remember to pass-by-reference
        all of my values.

'''

class Guest:

    def __init__(self, guest_number, first_name, last_name, same_table=[], not_same_table=[], table_number=0):

        # Guest's Name
        self.first_name = first_name

        # guest's last name
        self.last_name = last_name

        # guest's number
        self.guest_number = guest_number

        # list of guest numbers the guest should be seated near
        self.same_table = same_table

        # list of guest numbers the guest should NOT be seated near
        self.not_same_table = not_same_table

        # table number a guest is seated at
        self.table_number = table_number


    def assign_table(self, table_number):
        self.table_number = table_number

        
'''
    Class: Table - 
        Defines the table object

        Tables can add guests, or remove guests
'''
class Table:

    def __init__(self, table_number, capacity=8, empty_seats=0):
        self.table_number = table_number
        self.seated_guests = []
        self.capacity = capacity
        self.empty_seats = empty_seats

    def add_guest(self, guest):
        if len(self.seated_guests) < self.capacity - self.empty_seats:
            if guest not in self.seated_guests:
                guest.table_number = self.table_number
                self.seated_guests.append(guest)
                return True

        return False

    def remove_guest(self, guest):
        if guest in self.seated_guests:
            self.seated_guests.remove(guest)
            return True

        return False


'''
    Class: Layout
        defines the layout of multiple tables

        cannot create tables itself, but stores a list of tables/guests and can
        evaulate its own fitness

    NOT READY FOR PRIMETIME
'''
class Layout:

    # constructor
    def __init__(self, table_list):
        
        # properties
        self.table_list = table_list
        self.fitness_score = 0

    # function that gets all of the individual guests from the tables in the layout
    def get_guests(self):

        guest_list = []

        for table in self.table_list:
            for guest in table.seated_guests:
                guest_list.append(guest)

        return guest_list
   
    # Static function that returns a new layout from a guest list: this returns a new Layout object
    def create_random_table_layout(guest_list=[], capacity=8, empty_seats=0):

        # Check for invalid parameters
        if guest_list == None or len(guest_list) == 0:
            print("Invalid parameters")
            return None

        # make a copy of the guest list, to ensure that the original is not altered
        temp_guest_list = deepcopy(guest_list)

        # Add the first table to the layout
        num_current_tables = 1
        table_list = [Table(num_current_tables, capacity, empty_seats)]

        # randomly shuffle the guests around
        random.shuffle(temp_guest_list)

        # Create tables until all of the guests have been allocated
        for guest in temp_guest_list:

            # Try to add the guest to the last table...
            if not table_list[-1].add_guest(guest):

                # If the table is full, add a new table...
                num_current_tables += 1
                table_list.append(Table(num_current_tables, capacity, empty_seats))

                # ...and add the guest
                table_list[-1].add_guest(guest)
        
        # return a new layout with the set table_list
        return Layout(table_list)
    
    # Evaluate the fitness value of the layout; this returns the value and sets it as a instance property
    def evaluate_fitness(self):
        if len(self.table_list) == 0:
            return 0
        
        '''
        evaluating the fitness of a layout means that each guest is examined for its neighbors at the same table
        a guest has people they can and cannot sit next to; the more times the rules are followed, the better the score

        ***
        FOR NOW: this function relies on the notion that table numbers determine table proximity to each other
        example: table 1 - table 2: next to each other - good result
        example: table 4 - table 21 very far away - good result
        example: enemies(table 5 - table 3) 2 tables away, score is 2
        ***

        HIGHER FITNESS SCORES ARE ALWAYS BETTER
        '''
        # Starting fitness score
        fitness_score = 0                        

        # I don't like this loop. I'm sure there's a faster way to perform a "where" statement in
        # Python, but since I have to rewrite this in Java anyway, as long as it works: don't care.
        # What I want to do: good_neighbors = self.all_guests.Where(x => guest.same_table.Contains(x.guest_number))  
        for guest in self.get_guests():

            # allocate a list for guest objects related to the guest numbers in a guest's 'same table' attribute
            good_neighbors = []
            bad_neighbors = []

            for g in self.get_guests():
                if g.guest_number in guest.same_table:
                    good_neighbors.append(g)
                elif g.guest_number in guest.not_same_table:
                    bad_neighbors.append(g)                    

            # How fitness is determined:
                # determine the proximity of the guest from both its desired neighbors and undesidred
                # desired:
                    # score = num_tables - abs(guest_table - neighbor_table)
                    # score = 20 tables - abs(table 5 - table 6)
                    # score = 20 - abs(-1)
                    # score = 19 = 20 - 1
                # undesired
                    # score = abs(guest_table - neighbor_table)
                    # score = abs(table 19 - table 5)
                    # score = abs(14)
                    # score = 14
            for g in good_neighbors:
                fitness_score += (len(self.table_list) - abs(guest.table_number - g.table_number))

            for b in bad_neighbors:
                fitness_score += (abs(guest.table_number - b.table_number))

        self.fitness_score = fitness_score
        return fitness_score

    def print_layout(self):

        print("***Table Layout***")
        print("  Fitness Value: {0}".format(self.fitness_score))

        for table in self.table_list:
            print("    Table {0}:".format(table.table_number))
            for guest in table.seated_guests:
                print("      {0} {1}".format(guest.first_name, guest.last_name))


'''
    GA:
        Primary driver for the genetic algorithm
        Takes a guest list, table capacity, and the default number of empty seats
        and creates a evolved table listing based on GA

    returns: best table listing
'''
def GA(guests, capacity=8, empty_seats=2):

    # Parameter check
    if (guests == None):
        print("Unable to run algorithm, guest list is empty.")
        return None

    # DEFAULT GA PARAMETERS; set these values to change how the algorithm works
    POPULATION_SIZE = 100
    MUTATION_RATE = 0.05
    DEATH_RATE = 0.1
    FITNESS_THRESHOLD = 100000

    # Init
    population = []
    temp_list = guests

    while len(population) == 0 or (member.fitness_value < FITNESS_THRESHOLD for member in population) and False:

        # Create an initial population by randomly selecting guests
        # from the guest list. Relationships play no role in this.
        for genome in range(0, POPULATION_SIZE):

            # Create a randomized layout of guests at the table
            layout = Layout.create_random_table_layout(temp_list)

            # Evalute the fitness of the layout
            layout.evaluate_fitness()

            # Add the member to the population
            population.append(layout)

        # Randomly select (round-robin) members to breed and create children
        children = breed(population, DEATH_RATE)

        # Insert a mutation into the population
        mutate(children, MUTATION_RATE)

        # Kill off the lowest fitness of the population to make room for the children
        # Sort the population by fitness value from greatest to smallest
        population.sort(key=lambda layout: layout.fitness_score, reverse=True)

        # remove the last X members: where X is the amount of children
        del population[-len(children):]

        # append the children to the population
        population.extend(children)

        # print the details of the most fit member
        population[0].print_layout()

        # REPEAT THIS METHOD until the fitness is over a certain threshold.
        pass


'''
    breed:
    Breed for new members of the population. This function takes three parameters:
        The population to breed - List
        The fitness values for the population - List
        The death rate of the population for a generation

    Returns - list of children selected from parents in the population
'''
def breed(population, death_rate=0.1):
    
    # list to track selected parents
    _selected = []
    _children = []

    # Use round-robin selection to select members to breed
    members_to_select = math.ceil(len(population) * death_rate)
    if members_to_select % 2 != 0: members_to_select += 1

    for c in range(members_to_select):
        select = None

        while(select is None or select in _selected):
            select = roulette_selection(population)
        
        _selected.append(select)

    # grab pairs of members and breed them to create a child
    index = 0
    while index < len(_selected):
        _children.append(crossover(mother=_selected[index], father=_selected[index+1]))
        index += 2

    # DEBUG to make sure this is working right
    if (len(_children) != members_to_select / 2):
        raise ValueError

    return _children

'''
    roulette_selection:
        randomly selects a member of a population based on the fitness values of the population
        higher fitness value -> higher chance of being selected
        
    returns: selected member of the population
'''
def roulette_selection(population):

    fitness_values = [p.fitness_score for p in population]
    sum_of_fitnesses = sum(fitness_values)
    pick = random.uniform(0,sum_of_fitnesses)
    current = 0
    for p in population:
        current += p.fitness_score
        if current > pick:
            return p

    return population[-1]

'''
    crossover:  ***UNFINISHED***
    swaps portions of the mother and father's lists to create a child

    returns a new genome with the swapped characteristics
'''
def crossover(mother, father):
    
    # make a copy of the mother
    child = Layout(mother)

    # get the count of 'chromosomes' to swap
    chromosomes_to_swap = len(mother.get_guests()) // 2

    # for each of the chromosomes we need to swap, select a random 
    # number of a guest, select that guest and swap that spot with
    #  the position of the same guest on the father
    for chromosome in range(0, chromosomes_to_swap):

        selected = math.floor(random.uniform(1, len(mother.get_guests()))) + 1
        selected_guest = [guest for guest in mother.get_guests() if int(guest.guest_number) == selected]
        selected_guest_father_table_number = [guest for guest in father.get_guests() if int(guest.guest_number) == selected][0].table_number

def mutate(children=[], mutation_rate=0.05):
    '''
    mutate:
    randomly has a chance to mutate one child based on a mutation rate
    will not always mutate

    function(children=[], mutation_rate=0.05) -> Layout list
    '''

    # Calculate if the function will mutate a child
    if (random.random() > mutation_rate):
        return
    
    # Randomly shuffle the children and apply the mutation to the last element
    random.shuffle(children)
    children[-1].mutate_genome()


'''
    mutate_genome:
    Provides details on how to mutate a genome
    
    returns the mutated genome
'''
'''
    ***UNFINISHED***
'''
def mutate_genome(genome):
    
    # randomly select two guests and swap their seats
    selected_guest_a = genome.guests()[random.uniform(0, len(genome.guests()))]
    selected_guest_b = None

    while selected_guest_b is None or selected_guest_b is selected_guest_a:
        selected_guest_b = genome.guests()[random.uniform(0, len(genome.guests()))]

    pass


'''
    create_guests:
        Creates a list of guest objects formatted from the sample data
        These guests are not assigned to a table

    returns: a list of guest objects
'''
def create_guests(filename):

    guests = []

    if filename != '':
        with open(filename, newline='') as csvfile:
            guest_reader = csv.reader(csvfile, dialect='excel')

            title_row = guest_reader.__next__()
            number_of_sames = title_row.count("Same Table")
            number_of_notsames = title_row.count("Not Same Table")

            for row in guest_reader:
                first_sames = 3
                guests.append(Guest(row[0], row[1], row[2],
                                    row[first_sames:first_sames + number_of_sames],
                                    row[first_sames + number_of_sames:first_sames +
                                                                      number_of_sames + number_of_notsames]))

    return guests


'''
    __main__:
        main driver for the algorithm tester

    returns: None
'''
if __name__ == '__main__':

    CSV_FILE = 'seating_sample.csv'
    guests = create_guests(CSV_FILE)      
    
    GA(guests)
