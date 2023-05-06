import string
import copy
import sys



# A B C D E F G H I J K L M N O P Q R S T U V W X Y 

neg_inf = -sys.maxsize
pos_inf = sys.maxsize
num_cells = 25
letters = list(string.ascii_uppercase)
letters.remove('Z')
common_elements = lambda a, b: list(filter(lambda x: x in a, b))

# generates the letter domains, which letter should have which letter in nighborhood.
letter_possible_domain= {'A': ['B']}
for i in range(len(letters)):
    if letters[i] not in ['A', 'Y']:
        letter_possible_domain[letters[i]] = [letters[i-1], letters[i+1]]
letter_possible_domain['Y'] = ['X']

board = ['_' for _ in range(num_cells)]

board[4] = "Y"
board[5] = "R"
board[6] = "A"
board[16] = "E"
board[24] = "K"



class Board:
    def __init__(self, board, parent = None, path = ()):
        self.board = board
        self.parent = parent
        self.path = path
        self.num_cells = num_cells
        self.available_letters = self.get_available_letters()
        self.empty_cells = self.get_empty_cells()
        self.filled_cells = self.get_filled_cells()
        self.used_letters = self.get_used_letters()

    
    # methods below gets available, empty, filles and used letters
    def get_available_letters(self):
        return [i for i in letters if i not in self.board]
    def get_empty_cells(self):
        return [i for i in  range(len(self.board))  if self.board[i] == '_']
    def get_filled_cells(self):
        return [i for i in  range(len(self.board))  if self.board[i] != '_']
    def get_used_letters(self):
        return [i for i in self.board if i != '_']

    # inputs the value into a board
    def input_letter(self, index, letter):
        new_board = self.board.copy()
        new_board[index] = letter
        return Board(new_board, self, self.path + ((index, letter), ))

    # checks is it safe to input a letter into a board
    def is_safe(self, letter, index):
        test_board = self.input_letter(index, letter)
        if not test_board.is_consistant or not test_board.arc():
            return False
        return True
    
    
    # check if the board has cells with empty domain. Empty domain means no letter can be assigned to it. 
    # Domain in this code means all the possible letters that can be assigned to a cell. 
    def is_consistant(self):
        for i in self.empty_cells:
            if len(self.get_cell_domain(i)) == 0:
                return False
        return True

    # Gets the domain of the cell. 2 Ifs, first one for the cell all neighbors of which are known, and 
    # the second if for all others
    def get_cell_domain(self, i, pr = False):
        right, left, top, bottom = self.get_cell_neighbors(i)
        cell_neighbor = [self.board[k] for k in self.get_cell_neighbors(i) if k != neg_inf]   
        domain = []
        if "_" not in cell_neighbor:
            for letter in cell_neighbor:
                domain.extend(letter_possible_domain[letter])
            domain = list(set(domain))
            domain = [i for i in domain if i in self.available_letters]
            for letter in domain:
                for letter_neighbor in letter_possible_domain[letter]:
                    if letter_neighbor in self.used_letters and letter_neighbor not in cell_neighbor:
                        domain.remove(letter)
        else:
            for letter in self.available_letters:
                skip = False
                # chech if a neghbors of letters are already used
                for letter_neighbor in letter_possible_domain[letter]:
                    if letter_neighbor in self.used_letters and letter_neighbor not in cell_neighbor:
                        skip = True
                if skip:
                    continue
                else:
                    domain.append(letter)                    
        domain = list(set(domain))

        temp_domain = domain.copy()
        for letter in temp_domain:
            if not self.is_safe(letter, i):
                domain.remove(letter)
        return domain
    
    
    
    # counts the domain size
    def get_domain_size(self):
        size = 0
        for i in range(25):
            size+=len(self.get_cell_domain(i))
        return size         

    
    # using minimum remaining value method to find the next cell to assign a letter. Among all empty letters 
    # finds the one with minimum domain size. (domain size is the pool of all leters that can be assigned to a letter)
    def mrv(self):
        best_cells = []
        for i in self.empty_cells:
            best_cells.append({i:len( self.get_cell_domain(i))})
        highest_indexes = [k for d in sorted(best_cells, key=lambda x: list(x.values())[0]) for k in d.keys()]
        moves = []
        n = 1
        c = 0
        for i in highest_indexes:
            moves_i = []
            for letter in self.get_cell_domain(i):
                if self.path + ((i, letter),) not in all_paths:
                    moves_i.append((i, letter))

            moves.append(moves_i)
            c+=1
            if c == n:
                break
        return moves
    
    # Using mrv method to get a cell to assign a letter. After getting a cell it picks the least restricting letter
    # to asssign.It counts sum of domain sizes of all empty cells after assigning this letter and chooses the maximum one. 
    def lcv(self, all_paths, pr = False):
        possible_moves = self.mrv()
        smart_moves = []

        for moves in possible_moves:
            smart_moves_i = {}
            for moves_i in moves:
                new_state = self.input_letter(moves_i[0], moves_i[1])
                smart_moves_i.update({(moves_i[0], moves_i[1]): new_state.get_domain_size()})
            if pr == True:
                print(smart_moves_i)
            sorted_dict = dict(sorted(smart_moves_i.items(), key=lambda x: x[1], reverse = True))
            smart_moves.extend(sorted_dict)

        return smart_moves[0] if len(smart_moves) != 0 else []
    
    # gets the neighbors of a cell.
    def get_cell_neighbors(self, i):
        right = i + 1 if (i+1) % 5 != 0 else neg_inf
        left = i - 1 if i % 5 != 0 else neg_inf
        top = i-5 if i not in range(0,4) else neg_inf
        bottom = i+5 if i not in range(20,25) else neg_inf
        return [right, left, top, bottom]
    
    # show_board
    def sb(self):
        for i in range(len(self.board)):
            print(self.board[i] + " ", end = "")
            if (i+1) % 5 == 0 and i != 0:
                print("\n")
                
    # for each used letter, it gets the neighboring in alphabet letters and checks if all adjacent in board letters are in that neighborhood
    def arc(self):
        for i in self.filled_cells:
            c = 0
            neighbors = self.get_cell_neighbors(i)
            letter_neighbors = [self.board[k] for k in neighbors if k != neg_inf] 
            if self.board[i] in ['A', 'Y']:
                c+=1
            c+= letter_neighbors.count('_')
            for adjacent in letter_possible_domain[self.board[i]]:
                if adjacent in letter_neighbors:
                    c+=1
                
            if c <2:
                return False
        return True
            
    # decides is the board target
    def is_target(self):
        for i in range(25):        
            is_neighbor = 0
            if self.board[i]  == "_":
                return False
            values = []
            # print(i, self.board[i] , locations)
            if self.board[i]  in ['A', 'Y']:
                is_neighbor+=1
            for location in self.get_cell_neighbors(i):
                if location!=neg_inf:
                    if  self.board[location]  in letter_possible_domain[self.board[i] ]:
                        is_neighbor+=1
            if is_neighbor != 2:
                # print(i, self.board[i] )
                return False
        return True


b = Board(board)


b.sb()
b.get_cell_neighbors(0)
all_paths = []
in_game = True
(index, letter) = (-1, -1)
counter = 0 

passed_nodes = []
history = []
board_history = []



history_of_cells = [[] for i in range(25)]
prev_step = (-1, -1)
retrieve = True
possible_nodes = []




while in_game:

    counter +=1
    # checks if the target is reached
    if b.is_target():
        print('done')
        break
    
    # generates next move
    possible_nodes = b.lcv(all_paths)
    
    # if there are no move available, backtracks
    if len(possible_nodes) == 0:
        print('\n\n\n\n', 'backtracking')
        b = b.parent
        
        continue
    
    # Otherwise assigns a choosen letter for a choosen cell. 
    index, letter = possible_nodes
    b = b.input_letter(index, letter)
    
    # adds path to storage, and in next moves will check to not repeat already passed moves
    all_paths.append(b.path)
    history_of_cells[index].append((index, letter))
    if counter % 1 == 0:
        print('__________')
        b.sb()
        print('\n')
b.sb()

    
    
