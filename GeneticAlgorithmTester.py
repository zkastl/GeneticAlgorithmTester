import random, csv, math


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

    def deep_clone(guest_list):

        copy_list = []
        for guest in guest_list:
            copy_list.append(guest)

        return copy_list

'''
    Class: Layout
        defines the layout of multiple tables

        cannot create tables itself, but stores a list of tables/guests and can
        evaulate its own fitness

    NOT READY FOR PRIMETIME
'''
class Layout:

    def __init__(self, empty_seats, guest_list):

        # property determining the number of required empty seats at a table
        self.empty_seats = empty_seats
        self.table_list = table_list
        self.all_guests = [table.seated_guests for table in table_list ]


    def create_random_table_layout(guest_list=[], capacity=8, empty_seats=0):

    # Check for invalid parameters
        if len(guest_list) == 0:
            return None

        num_current_tables = 1
        # add a first table
        table_list = [Table(num_current_tables, capacity, empty_seats)]

        # randomly shuffle the guests around
        random.shuffle(guest_list)

        # Create tables until all of the guests have been allocated
        for guest in guest_list:

            # Try to add the guest to the last table...
            if not table_list[-1].add_guest(guest):

                # If the table is full, add a new table...
                num_current_tables += 1
                table_list.append(Table(num_current_tables, capacity, empty_seats))

                # ...and add the guest
                table_list[-1].add_guest(guest)

        return table_list

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

        # for each guest in the layout:
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
        
        for guest in self.all_guests:
            good_neighbors = [guest.same_table] # good_neighbors = self.all_guests.Where(x => guest.same_table.Contains(x.guest_number)) 





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
                self.seated_guests.append(guest)
                self.seated_guests[-1].table_number = self.table_number
                return True

        return False

    def remove_guest(self, guest):
        if guest in self.seated_guests:
            self.seated_guests.remove(guest)
            return True

        return False

'''
    GA:
        Primary driver for the genetic algorithm
        Takes a guest list, table capacity, and the default number of empty seats
        and creates a evolved table listing based on GA

    returns: best table listing
'''
def GA(guest_list, capacity=8, empty_seats=2):

   # Parameter check
    if (len(guest_list) == 0):
        print("Unable to run algorithm, guest list is empty.")
        return None

    # DEFAULT GA PARAMETERS; these do not change throughout algorithm
    POPULATION_SIZE = 100
    MUTATION_RATE = 0.05
    DEATH_RATE = 0.01

    # Init
    population = []
    temp_list = guest_list.deep_clone()

    # Create an initial population by randomly selecting guests
    # from the guest list. Relationships play no role in this.
    for genome in range(0, POPULATION_SIZE):

        # Create a randomized layout of guests at the table
        table_list = create_random_table_layout(temp_list)

        # Add the member to the population
        population.append(table_list)  
        
    # Once the population is created, evaluate the fitness of each member.
    population_with_fitness = [(member, evaulate_fitness(member)) for member in population]

    # Randomly select (round-robin) members to breed and create children
    children = breed(population_with_fitness, DEATH_RATE)

    # Insert a mutation into the population
    mutate(children, MUTATION_RATE)

    # Kill off the lowest fitness of the population to make room for the children


'''
    evaluate_fitness:
        evaluates the fitness of a particular genome
        value ranges from 0-inf; higher values are better

    returns: integer value/fitness score
'''
def evaulate_fitness(genome):
    pass

'''
    breed:
    Breed for new members of the population. This function takes three parameters:
        The population to breed - List
        The fitness values for the population - List
        The death rate of the population for a generation

    Returns - list of children selected from parents in the population
'''
def breed(population_with_fitness=([],[]), death_rate=0.1):
    
    # list to track selected parents
    _selected = []
    _children = []

    # Use round-robin selection to select members to breed
    for c in range(0, (len(population) * death_rate * 2)):

        # do some sort of round-robin selection voodoo
        # _selected.append(rr_select(population, fitness, _selected))
        pass

    index = 0
    while index < len(_selected):
        _children.append(crossover(mother=_selected[index], father=_selected[index+1]))

    # DEBUG to make sure this is working right
    if (len(_children) != len(population) * death_rate * 2):
        raise ValueError

    return _children


'''
    crossover:
    swaps portions of the mother and father's lists to create a child

    returns a new genome with the swapped characteristics
'''
def crossover(mother, father):
    pass


'''
    mutate:
    randomly has a chance to mutate one child based on a mutation rate
    will not always mutate

    returns the list of children, potentially with the mutated member
'''
def mutate(children=[], mutation_rate=0.05):

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
def mutate_genome(genome):
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

    layout = Layout.create_random_table_layout(guests) # returns a list of tables, not a Layout object yet

    for guest in guests:

        st = []
        for g in guests:
            if g.guest_number in guest.same_table:
                st.append(g)

