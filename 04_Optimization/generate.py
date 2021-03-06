import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains_to_remove = []
        for domain in self.domains:
            for word in self.domains[domain]:
                if len(word) != domain.length:
                    domains_to_remove.append((domain, word))

        for domain, word in domains_to_remove:
            self.domains[domain].remove(word)          

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """ 
        overlap = self.crossword.overlaps[x, y]

        word_to_remove = []
        for possible_word in self.domains[x]:
            keep_word = False
            for possible_corresponding in self.domains[y]:
                if possible_corresponding == possible_word:
                    continue
                if self.get_letter(possible_word, overlap[0]) == self.get_letter(possible_corresponding, overlap[1]):
                    keep_word = True
                    break
            if not keep_word:
                word_to_remove.append(possible_word)
        for to_remove in word_to_remove:
            self.domains[x].remove(to_remove)

        return True if len(word_to_remove) != 0 else False

    def get_letter(self, word, position):
        result = word[position]
        return result        

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for possible_overlap in self.crossword.overlaps:
                overlap = self.crossword.overlaps[possible_overlap[0], possible_overlap[1]]
                if overlap != None and not arcs.__contains__(possible_overlap):
                    arcs.append(possible_overlap)
        while len(arcs) !=0:
            arc = arcs.pop()
            if self.revise(arc[0], arc[1]):
                if len(self.domains[arc[0]]) == 0:
                    return False
                for neighbour in self.crossword.neighbors(arc[0]):
                    arcs.append((neighbour, arc[0]))


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.domains) == len(assignment):
            return True
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for to_check in assignment:
            if to_check.length != len(assignment[to_check]):
                return False
            for possible_duplicate in assignment:
                if assignment[to_check] == assignment[possible_duplicate] and to_check != possible_duplicate:
                    return False
            for neighbor in self.crossword.neighbors(to_check):
                if not assignment.__contains__(neighbor):
                    continue
                overlap = self.crossword.overlaps[neighbor, to_check]
                if overlap == None:
                    continue
                word_neighbor = assignment[neighbor]
                letter_neighbor = word_neighbor[overlap[0]]
                word_to_check = assignment[to_check]
                letter_to_check = word_to_check[overlap[1]]
                if letter_neighbor != letter_to_check:
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        option_to_changes = []
        for option in self.domains[var]:
            counter_neighbour_changes = 0
            for neighbor  in self.crossword.neighbors(var):
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap == None or assignment.__contains__(neighbor):
                    continue
                letter = option[overlap[0]]
                for neighbor_word_option in self.domains[neighbor]:
                    if letter != neighbor_word_option[overlap[1]]:
                        counter_neighbour_changes +=1
            option_to_changes.append((option, counter_neighbour_changes))
        option_to_changes.sort(key=lambda x: x[1])
        sorted = []
        for element in option_to_changes:
            sorted.append(element[0])
        return sorted
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        current_fewest_domain = None
        fewest_count = -1
        for domain in self.domains:
            if assignment.__contains__(domain):
                continue
            if len(self.domains[domain]) > fewest_count and len(self.domains[domain]) > 0:
                fewest_count = len(self.domains[domain])
                current_fewest_domain = domain
            elif len(self.domains[domain]) == fewest_count:
                if len(self.crossword.neighbors(domain)) > len(self.crossword.neighbors(current_fewest_domain)):
                    current_fewest_domain = domain
        return current_fewest_domain
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):            
                return assignment if self.consistent(assignment) else None

        variable = self.select_unassigned_variable(assignment)
        order_domains = self.order_domain_values(variable, assignment)
        for value in order_domains:
            if self.consistent(assignment):
                assignment[variable] = value
                result = self.backtrack(assignment)
                if result != None:
                    return result
                assignment.pop(variable)
            else:   #improve performace, otherwise the loop would call self.consistent several (unecessary) times
                break
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
