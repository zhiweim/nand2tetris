from predefined_symbol_table import symbols, comp, jump, dest


class Parsembler:
    """
    A parser/assembler class that reads from a symbolic machine language program
    and translates it to 16 bit binary code that can be executed by the computer.
    Starts by adding any undefined labels to the symbols table and cleans up the
    asm file so the instructions are in a more readable format by stripping away
    comments and white spaces. Any undefined symbols are then added to the symbols
    table before the instructions are translated into 16 bit binary code. 
    """
    def __init__(self, input_file):
        """
        Initialize class variables and runs class methods using the input file
        """
        self.instructions = []
        self.symbols = symbols
        self.add_labels(input_file)
        self.clean_instructions(input_file)
        self.translate()

    def add_labels(self, input_file):
        """
        Reads the asm file and adds any undefined labels to the symbol's dictionary
        :param input_file: asm file
        :return: None
        """
        current_line = 0  # used to keep track of what line it is currently at on the asm file
        lines = open(input_file).readlines()
        for line in lines:
            if line.startswith('//') or line.startswith('\n'):  # parse through each line in the file, ignoring // or \n
                continue

            if line.startswith('('):
                self.symbols[line[1:-2]] = current_line  # line[1:-2] removes the parenthesis (LOOP) -> LOOP
                continue  # continue so current_line doesn't get incremented from label

            current_line += 1

    def add_symbols(self):
        """
        Reads the asm file and adds any undefined symbols to the symbol's dictionary. If the 
        symbol is an int, do nothing as their memory address will be their respective number.
        Otherwise, start from memory address 16 and increment for every new symbol.
        :return: None
        """
        current_instruction = 16  # new variables will start at memory address 16
        for line in self.instructions:
            if line.startswith('@'):
                symbol = line[1:]
                try:
                    symbol = int(symbol)
                except ValueError:
                    if symbol not in self.symbols:
                        self.symbols[symbol] = current_instruction
                        current_instruction += 1

    def clean_instructions(self, input_file):
        """
        Reads the asm file and appends to instructions in a more readable format, stripping comments
        and any white spaces in the program. Calls to add_symbols() to add any undefined symbols
        to the current symbols dictionary
        :param input_file: asm file
        :return: None
        """
        lines = open(input_file).readlines()
        for line in lines:
            if line.startswith('//') or line.startswith('\n'):
                continue

            stripped = line.strip()  # strip any whitespaces in the beginning
            if '//' in stripped:  # detecting any in line comments, stripping any white spaces and ignoring the comments
                self.instructions.append(stripped.split("//")[0].strip())
            else:
                self.instructions.append(stripped)  # no in line comments detected, just append to instructions normally
        self.instructions = list(filter(lambda x: x != '', self.instructions))  # filters any spaces in the instructions
        self.instructions = list(filter(lambda x: '(' not in x, self.instructions))  # filter labels
        self.add_symbols()

    def a_instruction(self, instruction):
        """
        Takes in an A instruction and converts it to 16 bit binary
        :param instruction: A instruction
        :return: 16 bit binary representation of instruction
        """
        instruction = instruction[1:]  # removes the @
        try:
            instruction = int(instruction)  # if the @ is an integer, convert through here
            x = '{0:016b}'.format(instruction)
            return x
        except ValueError:
            x = f"{int(self.symbols[instruction]):0>16b}"
            return x

    def translate(self):
        """
        Translates the instructions into 16 bit binary format and writes it into output file
        NOTE: This function assumes that jump bits are not in the same line as a C instruction and presets the jump bits
        to null or '000'
        :return: None
        """
        if len(self.instructions) == 0:
            return

        f = open('Pong.hack', 'w')  # change to whatever asm file name to test against

        for instruction in self.instructions:
            if '@' in instruction:  # A-instruction is found
                x = self.a_instruction(instruction)
                f.write(x + '\n')

            elif '=' in instruction:  # C-instruction is found
                d = instruction.split('=')[0]  # first part of instruction before = is dest; D=M-1 -> d=D
                c = instruction.split('=')[-1]  # last part of instruction after = is comp; D=M-1 -> c=M-1
                c_beginning = '111'
                null_jump = '000'  # ASSUMING NO JUMP ON C instruction
                final_dest = dest[d]
                final_comp = comp[c]
                final = c_beginning+final_comp+final_dest+null_jump
                f.write(final + '\n')

            elif ';' in instruction:
                c = instruction.split(';')[0]
                j = instruction.split(';')[-1]
                d = '000'
                c_beginning = '111'
                final_comp = comp[c]
                final_jump = jump[j]
                final = c_beginning+final_comp+d+final_jump
                f.write(final + '\n')


parser = Parsembler('test_file')

