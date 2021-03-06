import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count
        self.mines = set()
        self.safe = set()
        #self.check_sentence_terminalState()


    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        return self.mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        return self.safe

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if self.cells.__contains__(cell):
            self.mines.add(cell)
            self.cells.remove(cell)
            self.count = self.count-1          

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if self.cells.__contains__(cell):
            self.safe.add(cell)
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)

        for sentence in self.knowledge:
            sentence.mark_mine(cell)
            self.check_sentence_terminalState(sentence)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            self.check_sentence_terminalState(sentence)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        all_neighbours, countMines = self.get_relevant_neighbours(cell)

        newSentence = Sentence(all_neighbours, count-countMines)
        
        self.checkIntersections(newSentence)
        
        newSentence = self.check_sentence_terminalState(newSentence)
        self.knowledge.append(newSentence)

        self.update_known_fields_clear_knowledge()     

    def checkIntersections(self, newSentence):
        for sentence in self.knowledge:
            if newSentence.cells < sentence.cells and len(newSentence.cells)>0:
                newIntersection = sentence.cells.difference(newSentence.cells)
                minecount = self.subtract_numbers_positiv_result(sentence.count,newSentence.count)                
                newDataSet = Sentence(newIntersection, minecount)

                if not self.knowledge.__contains__(newDataSet):
                    newDataSet = self.check_sentence_terminalState(newDataSet)
                    self.knowledge.append(newDataSet)
            elif newSentence.cells > sentence.cells and len(sentence.cells)>0:
                newIntersection =newSentence.cells.difference(sentence.cells)
                minecount = self.subtract_numbers_positiv_result(newSentence.count, sentence.count)               
                newDataSet =  Sentence(newIntersection, minecount)

                if not self.knowledge.__contains__(newDataSet):
                    newDataSet = self.check_sentence_terminalState(newDataSet)
                    self.knowledge.append(newDataSet)

    
    def update_known_fields_clear_knowledge(self):
        useless_knowledge = []
        for sentence in self.knowledge:
            for safe in sentence.safe:
                if not self.safes.__contains__(safe):
                    self.mark_safe(safe)
            for mine in sentence.mines:
                if not self.mines.__contains__(mine):
                    self.mark_mine(mine)

        for sentence in self.knowledge:
            if len(sentence.cells)==0:
                useless_knowledge.append(sentence)       
        for useless in useless_knowledge:
            self.knowledge.remove(useless)

    def get_relevant_neighbours(self, cell):
        all_neighbours =self.get_neighbours(cell)
        not_relevent_neighbours = set()
        countMines = 0
        for neighbour in all_neighbours:
            if self.mines.__contains__(neighbour):
                not_relevent_neighbours.add(neighbour)
                countMines +=1
            if self.safes.__contains__(neighbour):
                not_relevent_neighbours.add(neighbour)
        for not_relevant in not_relevent_neighbours:
            all_neighbours.remove(not_relevant)
        return (all_neighbours,countMines)

    def subtract_numbers_positiv_result(self, number1, number2):
        minecount = number1-number2
        if minecount < 0:
            minecount = 0
        return minecount

    def get_neighbours(self, cell):
        neighbours = set()
        for i in range(cell[0]-1,cell[0]+2):
            if i < 0 or i>self.height-1 :
                continue 
            for a in range(cell[1]-1,cell[1]+2):
                if a < 0 or a>self.width-1:
                    continue
                if (i,a) == cell:
                    continue
                neighbours.add((i,a))
        return neighbours

    def check_sentence_terminalState(self, sentence):
        if len(sentence.cells) == sentence.count:
            safeCells=set(sentence.cells)
            for cell in safeCells:
                self.mark_mine(cell)
                sentence.mark_mine(cell)
            return sentence
        if sentence.count==0 and len(sentence.cells)>0:
            safeCells=set(sentence.cells)
            for cell in safeCells:
                self.mark_safe(cell)
                sentence.mark_safe(cell)
            return sentence  
        return sentence  

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for field in self.safes:
            if not self.moves_made.__contains__(field):
                return field
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height) :
            for a in range(self.width):
                currentfield = (i,a)
                if not self.moves_made.__contains__(currentfield) and not self.mines.__contains__(currentfield):
                    return currentfield
        return None