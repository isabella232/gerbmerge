import re
import string

# Patterns for Excellon interpretation
xtdef_pat = re.compile(r'^(T\d+)(?:F\d+)?(?:S\d+)?C([0-9.]+)$') # Tool+diameter definition with optional
                                                                # feed/speed (for Protel)
xtdef2_pat = re.compile(r'^(T\d+)C([0-9.]+)(?:F\d+)?(?:S\d+)?$') # Tool+diameter definition with optional
                                                                # feed/speed at the end (for OrCAD)


XIgnoreList = ( \
  re.compile(r'^%$'),
  re.compile(r'^M30$'),   # End of job
  re.compile(r'^M48$'),   # Program header to first %
  re.compile(r'^M72$'),   # Inches
  re.compile(r'^FMAT,2$'),# KiCad work-around
  re.compile(r'^G05$'),   # Drill Mode
  re.compile(r'^M71$'),   # Metric Mode
  re.compile(r'^G90$')    # Absolute Mode
  )

def xln2tenthou(L, divisor, zeropadto, zeroSuppression):
      V = []
      for s in L:
        if s is not None:
          if zeroSuppression == 'trailing':
            s = s + '0'*(zeropadto-len(s))
            #s = s[:6]
          
          converted = int(round(int(s)*divisor))  
          print s + ", converted = " + str(converted)            
          V.append(converted)
        else:
          V.append(None)
      return tuple(V)
      
def xln2tenthou2 (L, divisor, zeropadto):
      V = []
      for s in L:
        if s is not None:
          V.append(int(float(s)*1000*divisor))
        else:
          V.append(None)
      return tuple(V)

#---------------------------------------------------------------------
class ExcellonFormat:
    def __init__(self, digits, decimals, units, zeroSuppression):
        self.digits = digits
        self.decimals = decimals
        self.units = units
        self.zeroSuppression = zeroSuppression

#---------------------------------------------------------------------
class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
#---------------------------------------------------------------------
# Abstract class that is representing excellon command, specific comand should implement this interface
class Command:
    @staticmethod
    def fromString(string, excellonFormat):
        'This function should return Command object if it can be paresed from provided string or None'
        raise NotImplementedError("Subclass must implement abstract method")   
    def toString(self, excelonFormat):
        raise NotImplementedError("Subclass must implement abstract method")

#---------------------------------------------------------------------
class PlungeCommand(Command):
    def __init__(self, coordinates):
        self.coordinates = coordinates
    @staticmethod
    def fromString(string, excelonFormat, lastCoordinates, divisor):
        xydraw_pat = re.compile(r'^X([+-]?\d+)Y([+-]?\d+)(?:G85X([+-]?\d+)Y([+-]?\d+))?$')    # Plunge command with optional G85
        xydraw_pat2 = re.compile(r'^X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*)(?:G85X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*))?$')    # Plunge command with optional G85
        xdraw_pat = re.compile(r'^X([+-]?\d+)$')    # Plunge command, repeat last Y value
        ydraw_pat = re.compile(r'^Y([+-]?\d+)$')    # Plunge command, repeat last X value
        match = xydraw_pat.match(string)
        if match:
            x, y, stop_x, stop_y = xln2tenthou(match.groups(), divisor, excelonFormat.digits, excelonFormat.zeroSuppression)       
            return PlungeCommand(Coordinates(x, y))
        match = xydraw_pat2.match(string)
        if match:
            x, y, stop_x, stop_y = xln2tenthou2(match.groups(), divisor, excelonFormat.digits)
            return PlungeCommand(Coordinates(x, y))
        match = xdraw_pat.match(string)
        if match:
            x = xln2tenthou(match.groups(),divisor, excelonFormat.digits, excelonFormat.zeroSuppression)[0]
            return PlungeCommand(Coordinates(x, lastCoordinates.y))
        match = ydraw_pat.match(string)
        if match:
            y = xln2tenthou(match.groups(),divisor, excelonFormat.digits, excelonFormat.zeroSuppression)[0]
            return PlungeCommand(Coordinates(lastCoordinates.x, y))
        return None   
        
    def toString(self, excelonFormat):
        return
    def getCoordinates(self):
        return self.coordinates          

#---------------------------------------------------------------------
class SlotCommand(Command):
    def __init__(self, startCoordinates, endCoordinates):
        self.startCoordinates = startCoordinates
        self.endCoordinates = endCoordinates
        
    @staticmethod
    def fromString(string, excellonFormat, divisor):
        xydraw_pat = re.compile(r'^X([+-]?\d+)Y([+-]?\d+)(?:G85X([+-]?\d+)Y([+-]?\d+))?$')    # Plunge command with optional G85
        xydraw_pat2 = re.compile(r'^X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*)(?:G85X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*))?$')    # Plunge command with optional G85
        match = xydraw_pat.match(string)
        if match:
            x, y, stop_x, stop_y = xln2tenthou(match.groups(), divisor, excelonFormat.digits, excelonFormat.zeroSuppression)       
            return SlotCommand(Coordinates(x, y), Coordinates(stop_x, stop_y))
        match = xydraw_pat2.match(string)
        if match:
            x, y, stop_x, stop_y = xln2tenthou2(match.groups(), divisor, excelonFormat.digits)
            return SlotCommand(Coordinates(x, y), Coordinates(stop_x, stop_y))
        return None
        
    def toString(self, excellonFormat):
        return ''
        
    def getCoordinates(self):
        return (self.startCoordinates, self.endCoordinates)            

#---------------------------------------------------------------------
class ToolchangeCommand:
    def __init__(self, toolnumber):
        self.tool = toolnumber
    @staticmethod
    def fromString(string):
        match = re.compile(r'^(T\d+)$').match(string)          # Tool selection
        if match:
            return ToolchangeCommand(int(match.group()[1:]))
        return None
    def toString(self):
        return 'T%02d' % self.tool          

#---------------------------------------------------------------------
class excellonParser:
    def __init__(self, expectedDigits=None, expectedUnits = 'inch'):
        self.toollist = []   
        # Excellon commands are grouped by tool number in a dictionary.
        # This is to help sorting all jobs and writing out all plunge
        # commands for a single tool.
        # 
        # The key to this dictionary is the full tool name, e.g., T03 as a
        # string. Each command is an (X,Y,STOP_X,STOP_Y) integer tuple.
        # STOP_X and STOP_Y are not none only if this is a G85 command.
        self.xcommands = {}
        # This is a dictionary mapping LOCAL tool names (e.g., T03) to diameters
        # in inches for THIS JOB. This dictionary will be initially empty
        # for old-style Excellon files with no embedded tool sizes. The
        # main program will construct this dictionary from the global tool
        # table in this case, once all jobs have been read in.
        self.xdiam = {}
        
        self.expectedDigits = expectedDigits
        self.expectedUnits = expectedUnits
        self.zeroSuppression = 'leading' 
        self.digits = None
        self.units = None             
        self.ToolList = None
 
    def spliteFile(self, fileContent):
        headerEnd = ["%", "M95"]

        header = ""
        content = ""
        footer = ""    
        headerBeginFound = False
        
        for line in fileContent.xreadlines():
            line = line.strip()            
            header = header + line + "\n"
            if line == "M48":
                headerBeginFound = True
            if headerBeginFound and line in headerEnd:
                break
                
        for line in fileContent.xreadlines():
            line = line.strip()
            content = content + line + "\n"
                            
        return header, content, footer
 
    def parseHeader(self, header, filename):
        unitAndZerosPosition = re.compile(r'^(INCH|METRIC),((?:[LT])Z)?$')      # Leading/trailing zeros INCLUDED
        fileFormat = re.compile(r';FILE_FORMAT=(\d):(\d)')
        plating = re.compile(r';TYPE=(.+)')
        
        currtool = None        
        for line in header.splitlines():
            line = line.strip()
            # Check for measurement unit and for leading/trailing zeros included ("INCH,LZ" or "INCH,TZ" or "METRIC,LZ" or "METRIC,TZ")
            match = unitAndZerosPosition.match(line)
            if match:
                unit, zerosPosition = match.groups()         
                if unit == "INCH":
                    self.units = 'inch'
                elif unit == "METRIC":
                    self.units = 'metric'
                else:
                    raise "Unsupported measurement unit."

                if zerosPosition == "LZ":
                    self.zeroSuppression = 'trailing'
                elif zerosPosition == "TZ":
                    self.zeroSuppression = 'leading'
                else:
                    raise "Unsupported zero suppression command"

            match = fileFormat.match(line)
            if match:
                numbersStr, decimalsStr = match.groups()    
                print numbersStr
                print decimalsStr
                self.digits = int(numbersStr) + int(decimalsStr)
            
            match = plating.match(line)
            if match:
                platingOption = match.group(1)
                print platingOption  
                
            # See if a tool is being defined. First try to match with tool name+size
            match = xtdef_pat.match(line)    # xtdef_pat and xtdef2_pat expect tool name and diameter
            if match is None:                # but xtdef_pat expects optional feed/speed between T and C
                match = xtdef2_pat.match(line) # and xtdef_2pat expects feed/speed at the end
            if match:
                currtool, diam = match.groups()
                try:
                    diam = float(diam)
                except:
                    raise RuntimeError, "File %s has illegal tool diameter '%s'" % (filename, diam)

                # Canonicalize tool number because Protel (of course) sometimes specifies it
                # as T01 and sometimes as T1. We canonicalize to T01.
                currtool = 'T%02d' % int(currtool[1:])

                print currtool + " diam: " + str(diam)
                
                if self.xdiam.has_key(currtool):
                    raise RuntimeError, "File %s defines tool %s more than once" % (filename, currtool)
                self.xdiam[currtool] = diam
                continue  
                
    def getToolDiameter(self, tool, filename):
        # Diameter will be obtained from embedded tool definition, local tool list or if not found, the global tool list
        try:
            diam = self.xdiam[tool]
        except:
            if self.ToolList:
                try:
                    diam = self.ToolList[tool]
                except:
                    raise RuntimeError, "File %s uses tool code %s that is not defined in the job's tool list" % (filename, tool)
            else:
                try:
                    diam = config.DefaultToolList[tool]
                except:                    
                    raise RuntimeError, "File %s uses tool code %s that is not defined in default tool list" % (filename, tool)
        return diam

    def parseContent(self, content, filename):
        excellonFormat = ExcellonFormat(digits=2, decimals=self.digits-2, units=self.units, zeroSuppression=self.zeroSuppression)
        divisor = 10.0**(4 - (self.digits-2))
        lastCoordinates = None
        currtool = None
        
        for line in content.splitlines():
            toolCommand = ToolchangeCommand.fromString(line)
            if toolCommand:         
                if toolCommand.toString() != 'T00': # KiCad specific fixes, tool T00 is KiCad specific
                    self.xdiam[toolCommand.toString()] = self.getToolDiameter(toolCommand.toString(), filename)
                    currtool = toolCommand.toString()
                continue
                
            command = PlungeCommand.fromString(line, excellonFormat, lastCoordinates, divisor)
            if command:
                lastCoordinates = command.getCoordinates()                
                if currtool is None:
                    raise RuntimeError, 'File %s has plunge command without previous tool selection' % filename
                tmp = (command.getCoordinates().x, command.getCoordinates().y, None, None)
                if currtool in self.xcommands:
                    self.xcommands[currtool].append(tmp)
                else:
                    self.xcommands[currtool] = [tmp]
                continue

            slotCommand = SlotCommand.fromString(line, excellonFormat, divisor)
            if slotCommand:
                if currtool is None:
                    raise RuntimeError, 'File %s has plunge command without previous tool selection' % filename                    
                tmp = (slotCommand.getCoorcinates()(0).x, slotCommand.getCoorcinates()(0).y, slotCommand.getCoorcinates()(1).x, slotCommand.getCoorcinates()(1).y)
                if currtool in self.xcommands:
                    self.xcommands[currtool].append(tmp)
                else:
                    self.xcommands[currtool] = [tmp]
                continue                

            # It had better be an ignorable
           # for pat in XIgnoreList:
           #     if pat.match(line):
           #         break
           # else:
           #     raise RuntimeError, 'File %s has uninterpretable line:\n  %s' % (filename, line)
                 
    def loadFile(self, filename):
        print 'Reading data from %s ...' % filename
        fileContent = file(filename, 'rt')
        header, content, footer = self.spliteFile(fileContent)        
        self.parseHeader(header, filename)
        if self.units == None:
            if self.expectedUnits != None:
                self.units = self.expectedUnits
            else:
                raise "missing units configuration"
        if self.digits == None:
            if self.expectedDigits != None:
                self.digits = self.expectedDigits
            else:
                raise "Missing digits configuration"            
                    
        self.parseContent(content, filename)

    def getToollist(self):
        return self.ToolList
    def getxdiam(self):            
        return self.xdiam
    def getxcommands(self):
        return self.xcommands
               
 
        

def main(): 
    p = excellonParser() 
    p.loadFile('test.txt')
   # p.parseExcellon('test.txt')

if __name__=="__main__":
    main()

