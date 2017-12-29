import sublime
import sublime_plugin
import re
import sys

class TableToOutlineCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # array for headers
        headerIndex     = []
        headerElement   = []
        headerAll       = ''
        # array for contents
        content         = []
        contentAll      = ''

        # getting copied area. this "sel_area" is array
        sel_area = self.view.sel()

        # if there is no selected area or are more than 2 selected area
        if (sel_area[0].empty() or len(sel_area) > 1):
            sublime.message_dialog("Select any area.")
        # if there is on selected area
        else:
            # store selected area to "region_text" which type is string.
            region_text = self.view.substr(sel_area[0])
            # split by '\n' into arry_data
            arry_data = region_text.split('\n')

        # processing headers part
        h1                      = TableHeaders(arry_data)
        headerStr               = h1.getHeaderString()
        headerIndex             = h1.getIndexHeaderSeparator()
        headerElement           = h1.getHeaderElement(headerStr,headerIndex)
        headerAll               = h1.makeHeader(headerElement)
        print ("headerStr: ",headerStr)
        print ("headerIndex: ",headerIndex)
        for i in headerElement:
            print ("header",i)
        print ("headerAll: ",headerAll)

        # processing contents part
        c1 = TableContents(arry_data)
        content = c1.makeContentElement()
        contentAll = c1.changeContentFromTableToMarkdown(content)
        print ("contentAll: ",contentAll)

        # replacing selected area and inserting contents
        self.view.replace(edit,sel_area[0],headerAll)
        self.view.insert(edit,sel_area[0].end(),contentAll)

class TableHeaders:
    def __init__(self,arry):
        self.arry = arry

    def getHeaderString(self):
        return self.arry[0]

    # get index of Header separators
    def getIndexHeaderSeparator(self):
        self.index_of_separator             = []
        self.index_of_escaped_separator     = []
        # detecting the index of '|'
        self.index = -1
        while True:
            self.index = self.arry[0].find('|', self.index + 1)
            if self.index == -1:
                break
            self.index_of_separator.append(self.index)
            # print ("start=%d" % self.index )
        print("self.index_of_separator: ",self.index_of_separator)

        # detecting the index of '\|'
        self.index = -1
        while True:
            self.index = self.arry[0].find('\|', self.index + 1)
            if self.index == -1:
                break
            self.index_of_escaped_separator.append(self.index + 1)
            # print ("start=%d" % self.index )
        print("self.index_of_escaped_separator: ",self.index_of_escaped_separator)
        self.a      = set(self.index_of_separator)
        self.b      = set(self.index_of_escaped_separator)
        self.diff   = self.a.difference(self.b)
        print("difference: ",self.a.difference(self.b))
        return sorted(self.diff)

    # get Header Element with argument of headerIndex
    def getHeaderElement(self,myHeaderStr,myHeaderIndex):
        myHeaderElement = []
        for i in range(0,len(myHeaderIndex)-1):
            index1 = myHeaderIndex[i]+1
            index2 = myHeaderIndex[i+1]
            myString = myHeaderStr[index1:index2].strip()
            myHeaderElement.append(myString)
        return myHeaderElement

    # make Header texts
    def makeHeader(self,myHeaderElement):
        myHeader = ''
        for i in range(0,len(myHeaderElement)):
            myHeader += "\t"*i+"+ "+myHeaderElement[i]+"\n"
        return myHeader

class TableContents:
    def __init__(self,myArry):
        self.arry    = myArry

    def makeContentElement(self):
        for i in range(0,len(self.arry)):
            print("self.arry: ",self.arry[i])
        return self.arry[2:]

    def changeContentFromTableToMarkdown(self,myContent):
        self.myContent = myContent
        self.myContentAll = ''
        for i in self.myContent:
            # splitting i by '|' to splittedContent
            splittedContent = re.split(r'\|',i)[1:-1]
            for j in range(0,len(splittedContent)):
                if(re.match(r"^ {1,}",splittedContent[j])):
                    self.myContentAll += '\t'*j+'-'+splittedContent[j]+'\n'
                else:
                    self.myContentAll += '\t'*j+'- '+splittedContent[j]+'\n'                    
        return self.myContentAll