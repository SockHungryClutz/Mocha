# Handler for parsing CSV files
# Using this because I don't like how the default CSV parser has to read a
# file handle and sit inside a "with open"
class CSVParser():
    @staticmethod
    def readFile(filename):
        with open(filename) as f:
            return f.readlines()
    
    @staticmethod
    # Returns a cleaned list from a csv file
    def parseFile(filename):
        r = FileParser.readFile(filename)
        l = len(r) - 1
        i = l
        lastChar = r[l][-1]
        while i >= 0:
            r[i] = r[i][:-1].split(',')
            i -= 1
        if not lastChar.isspace():
            r[l][len(r[l])-1] = r[l][len(r[l])-1] + lastChar
        return r
    
    @staticmethod
    # Writes out to a file, can take a mode as argument
    def writeFile(filename, content, mode):
        with open(filename, mode) as f:
            f.write(content)

    @staticmethod
    # Writes a nested list to a csv file (2 layers deep max)
    def writeNestedList(filename, lst, mode):
        ostr = ""
        for n in lst:
            for o in n:
                ostr += o + ','
            ostr = ostr[:-1] + '\n'
        FileParser.writeFile(filename, ostr, mode)
