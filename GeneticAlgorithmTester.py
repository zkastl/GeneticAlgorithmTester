import random, csv, math
from copy import deepcopy

''' REMEMBER!!!
        Python tends to pass everything by reference.
        When translating this to Java, I need to remember to pass-by-reference
        all of my values.

'''


class Guest:

    def __init__(self, guest_number, first_name, last_name, same_table, not_same_table, table_number=0):

        # Guest's Name
        self.first_name = first_name

        # guest's last name
        self.last_name = last_name

        # guest's number
        self.guest_number = int(guest_number)

        # list of guest numbers the guest should be seated near
        self.same_table = [int(same) for same in same_table if same != '']

        # list of guest numbers the guest should NOT be seated near
        self.not_same_table = [int(not_same) for not_same in not_same_table if not_same != '']

        # table number a guest is seated at
        self.table_number = int(table_number)

    def assign_table(self, table_number):
        self.table_number = int(table_number)

        
class Table:
    """
        Class: Table -
            Defines the table object

            Tables can add guests, or remove guests
    """
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


class Layout:
    """
        Class: Layout
            defines the layout of multiple tables

            cannot create tables itself, but stores a list of tables/guests and can
            evaluate its own fitness
    """

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
    @staticmethod
    def create_random_table_layout(guest_list, capacity=8, empty_seats=0):

        # Check for invalid parameters
        if guest_list is None or len(guest_list) == 0:
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
       
        HIGHER FITNESS SCORES ARE ALWAYS BETTER
        '''
        # Starting fitness score
        self.fitness_score = 0
        sum_of_fitnesses = 0

        for table in self.table_list:
            table_average = 0
            for guest in table.seated_guests:
                table_average += 1000 * len([neighbor for neighbor in table.seated_guests if neighbor.guest_number in guest.same_table])
                table_average += len([neighbor for neighbor in table.seated_guests if neighbor.guest_number in guest.not_same_table])
            sum_of_fitnesses += table_average

        self.fitness_score = sum_of_fitnesses // len(self.table_list)
        return self.fitness_score

    # print out the layout in a pretty form for debugging
    def print_layout(self):

        print("***Table Layout***")
        print("  Fitness Value: {0}".format(self.fitness_score))

        for table in self.table_list:
            print("    Table {0}:".format(table.table_number))
            for guest in table.seated_guests:
                print("      {0} {1} ({2}) - {3}, {4}".format(guest.first_name, guest.last_name, guest.guest_number, guest.same_table, guest.not_same_table))

    # fully copy the object, creating a complete copy of the object
    @staticmethod
    def deepcopy(layout):

        copied_list = deepcopy(layout.table_list)
        new_layout = Layout(copied_list)
        new_layout.evaluate_fitness()

        return new_layout


class GA:

    @staticmethod
    def GA(guests, capacity=8, empty_seats=2):
        """
            GA:
                Primary driver for the genetic algorithm
                Takes a guest list, table capacity, and the default number of empty seats
                and creates a evolved table listing based on GA

            returns: best table listing
        """
        # Parameter check
        if guests is None:
            print("Unable to run algorithm, guest list is empty.")
            return None

        # DEFAULT GA PARAMETERS; set these values to change how the algorithm works
        POPULATION_SIZE = 40
        MUTATION_RATE = 0.1
        DEATH_RATE = 0.2
        FITNESS_THRESHOLD = 1000
        MAX_GENERATIONS = 2000

        # Init
        population = []
        generation = 1
        max_fitness = 0

        # Create an initial population by randomly selecting guests
        # from the guest list. Relationships play no role in this.
        for genome in range(0, POPULATION_SIZE):
            # Create a randomized layout of guests at the table
            layout = Layout.create_random_table_layout(guests, capacity=capacity, empty_seats=empty_seats)

            # Evaluate the fitness of the layout
            layout.evaluate_fitness()

            # Add the member to the population
            population.append(layout)

        while generation < MAX_GENERATIONS:

            # Randomly select (round-robin) members to breed and create children
            children = GA.breed(population, DEATH_RATE)

            # Insert a mutation into the population
            GA.mutate(children, MUTATION_RATE)

            # Kill off the lowest fitness of the population to make room for the children
            # Sort the population by fitness value from greatest to smallest
            population.sort(key=lambda l: l.fitness_score, reverse=True)

            # remove the last X members: where X is the amount of children
            del population[-len(children):]

            # append the children to the population
            population.extend(children)

            # print the details of the most fit member
            # Repeat until the fitness is over a certain threshold.        
            population.sort(key=lambda l: l.fitness_score, reverse=True)
            if generation % 10 == 0: print('Generation {0} - Max fitness: {1}'.format(generation, population[0].fitness_score))
            generation += 1

        population[0].print_layout()


    '''
        breed:
        Breed for new members of the population. This function takes three parameters:
            The population to breed - List
            The fitness values for the population - List
            The death rate of the population for a generation

        Returns - list of children selected from parents in the population
    '''
    @staticmethod
    def breed(population, death_rate=0.1):
    
        # list to track selected parents
        _selected = []
        _children = []

        # Use round-robin selection to select members to breed
        members_to_select = math.ceil(len(population) * death_rate)
        if members_to_select % 2 != 0: members_to_select += 1

        for c in range(int(members_to_select)):
            select = None

            while select is None or select in _selected:
                select = GA.roulette_selection(population)
        
            _selected.append(select)

        # grab pairs of members and breed them to create a child
        index = 0
        while index < len(_selected):
            _children.append(GA.crossover(mother=_selected[index], father=_selected[index+1]))
            index += 2

        # DEBUG to make sure this is working right
        if len(_children) != members_to_select / 2:
            raise ValueError

        return _children


    @staticmethod
    def roulette_selection(population):
        """
        roulette_selection:
            randomly selects a member of a population based on the fitness values of the population
            higher fitness value -> higher chance of being selected
        
        returns: selected member of the population
        """
        fitness_values = [p.fitness_score for p in population]
        sum_of_fitness = sum(fitness_values)
        pick = random.uniform(0,sum_of_fitness)
        current = 0
        for p in population:
            current += p.fitness_score
            if current > pick:
                return p

        return population[-1]


    @staticmethod
    def crossover(mother: Layout, father: Layout):

        """
            Swaps portions of the mother and father's lists to create a child and returns a new genome with the swapped characteristics.
        """

        # make a copy of the mother
        child = Layout.deepcopy(mother)

        # get the count of 'chromosomes' to swap
        chromosomes_to_swap = len(child.get_guests()) // 2

        # for each of the chromosomes we need to swap, select a random 
        # number of a guest, select that guest and swap that spot with
        #  the position of the same guest on the father

        # NOTE: this works primarily because python is *pointer-happy*
        # i.e changing the data referenced by a label updates the label
        # this will probably have to change in the java implementation
        for chromosome in range(0, chromosomes_to_swap):

            # randomly select a guest number from the list of guests
            selected = math.floor(random.uniform(1, len(child.get_guests()))) + 1

            # select the guest in the mother's genome that corresponds to the number pid
            selected_guest = [guest for guest in child.get_guests() if int(guest.guest_number) == selected][0]

            # find the table number of the selected guest in the father's layout
            fathers_guest = [guest for guest in father.get_guests() if int(guest.guest_number) == selected][0]

            # find the first guest in the mother's layout that is at the table linked to by the father's layout
            swapped_guest = [guest for guest in child.get_guests() if int(guest.table_number) == fathers_guest.table_number][0]

            # swap the table numbers of the two selected guests
            backup_guest = selected_guest
            selected_guest = swapped_guest
            swapped_guest = backup_guest

            backup_number = selected_guest.table_number
            selected_guest.table_number = swapped_guest.table_number
            swapped_guest.table_number = backup_number

        child.evaluate_fitness()
        return child

    @staticmethod
    def mutate(children, mutation_rate=0.05):

        # Calculate if the function will mutate a child
        if random.random() > mutation_rate:
            return
    
        # Randomly shuffle the children and apply the mutation to the last element
        random.shuffle(children)

        # mutate
        GA.mutate_genome(children[-1])

    @staticmethod
    def mutate_genome(genome):

        """
            mutate_genome:
            Provides details on how to mutate a genome

            returns the mutated genome
        """

        # randomly select two guests and swap their seats
        selected_guest_a = None
        selected_guest_b = None

        # verify that the selected b guest is not the same guest
        while selected_guest_b is selected_guest_a:
            selected_guest_a = genome.get_guests()[int(random.uniform(0, len(genome.get_guests())))]
            selected_guest_b = genome.get_guests()[int(random.uniform(0, len(genome.get_guests())))]

        # swap the table numbers of the two guests
        table_number = selected_guest_a.table_number
        selected_guest_a.table_number = selected_guest_b.table_number
        selected_guest_b.table_number = table_number

        # swap the guests
        selected_backup = selected_guest_a
        selected_guest_a = selected_guest_b
        selected_guest_b = selected_backup


def create_guests(filename):

    """
        create_guests:
            Creates a list of guest objects formatted from the sample data
            These guests are not assigned to a table

        returns: a list of guest objects
    """
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
                                    row[first_sames + number_of_sames:first_sames + number_of_sames + number_of_notsames]))

    return guests


if __name__ == '__main__':

    """
        __main__:
            main driver for the algorithm tester

        returns: None
    """
    CSV_FILE = 'seating_sample.csv'    
    GA.GA(create_guests(CSV_FILE))
