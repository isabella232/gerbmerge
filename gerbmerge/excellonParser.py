import re
import string
import json

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

          converted = int(round(int(s)/divisor))
          #print s + ", converted = " + str(converted)
          V.append(converted)
        else:
          V.append(None)
      return tuple(V)

def xln2tenthou2(L, divisor, zeropadto):
      V = []
      for s in L:
        if s is not None:
          V.append(int(float(s)*1000*divisor))
        else:
          V.append(None)
      return tuple(V)

#---------------------------------------------------------------------
class ExcellonFormat:
    def __init__(self, integerPart, decimalPart, units, zeroSuppression):
        self._asignValues(integerPart, decimalPart, units, zeroSuppression)
        self.validate()

    @staticmethod
    def _printNoneIfNeded(obj):
        if obj == None:
           return 'None'
        else:
           return obj

    def __str__(self):
        return '\t' + str(self._printNoneIfNeded(self.integerPart)) + ':' + str(self._printNoneIfNeded(self.decimalPart)) + '\n\tUnits: ' + self._printNoneIfNeded(self.units) + '\n\tZero suppression: ' + self._printNoneIfNeded(self.zeroSuppression)

    def toDict(self):
        return {'integerPart' : self.integerPart, 'decimalPart' : self.decimalPart, 'units' : self.units, 'zeroSuppression' : self.zeroSuppression}

    @staticmethod
    def fromDict(dictionary):
        return ExcellonFormat(dictionary['integerPart'], dictionary['decimalPart'], dictionary['units'], dictionary['zeroSuppression'])

    def _asignValues(self, integer, decimals, units, zeroSuppression):
        self.integerPart = integer
        self.decimalPart = decimals
        self.units = units
        self.zeroSuppression = zeroSuppression

    def validate(self):
        possibleZeroSuppression = ['leading', 'trailing', None]
        possibleUnits = ['inch', 'metric', None]

        if self.zeroSuppression not in possibleZeroSuppression:
            raise "Unsupported zero suppression option: " + str(self.zeroSuppression)
        if self.units not in possibleUnits:
            raise "Unsupported units option: " + str(self.units)

    def isEqual(self, excellonFormat):
        if self.integerPart != excellonFormat.digits:
            return False
        if self.decimalPart != excellonFormat.decimalPart:
            return False
        if self.units != excellonFormat.units:
            return False
        if self.zeroSuppression != excellonFormat.zeroSuppression:
            return False
        return True

    def isEqualSkipNone(self, excellonFormat):
        if self.integerPart != None and excellonFormat.integerPart != None and self.integerPart != excellonFormat.integerPart:
            return False
        if self.decimalPart != None and excellonFormat.decimalPart != None and self.decimalPart != excellonFormat.decimalPart:
            return False
        if self.units != None and excellonFormat.units != None and self.units != excellonFormat.units:
            return False
        if self.zeroSuppression != None and excellonFormat.zeroSuppression != None and self.zeroSuppression != excellonFormat.zeroSuppression:
            return False
        return True

    def fillNoneFields(self, excellonFormat):
        if self.integerPart == None:
            self.integerPart = excellonFormat.integerPart
        if self.decimalPart == None:
            self.decimalPart = excellonFormat.decimalPart
        if self.units == None:
            self.units = excellonFormat.units
        if self.zeroSuppression == None:
            self.zeroSuppression = excellonFormat.zeroSuppression

    def getDigits(self):
        return self.integerPart + self.decimalPart

#---------------------------------------------------------------------
class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return json.dumps(self.toDict())

    def toDict(self):
        return {'x' : self.x, 'y' : self.y}

    @staticmethod
    def fromDict(dictionary):
        return Coordinates(dictionary['x'], dictionary['y'])

#---------------------------------------------------------------------
# Abstract class that is representing excellon command, specific comand should implement this interface
class Command:
    @staticmethod
    def fromString(string, excellonFormat):
        'This function should return Command object if it can be paresed from provided string or None'
        raise NotImplementedError("Subclass must implement abstract method")
    def toString(self, excelonFormat):
        raise NotImplementedError("Subclass must implement abstract method")
    @staticmethod
    def fromDict(dictionary):
        raise NotImplementedError("Subclass must implement abstract method")
    def toDict(self):
        raise NotImplementedError("Subclass must implement abstract method")

#---------------------------------------------------------------------
class PlungeCommand(Command):
    def __init__(self, coordinates, tool=None):
        self.coordinates = coordinates
        self.tool = tool

    def __repr__(self):
        return json.dumps(self.toDict())

    @staticmethod
    def fromString(string, excelonFormat, lastCoordinates, divisor):
        xydraw_pat  = re.compile(r'^X([+-]?\d+)Y([+-]?\d+)$')    # Plunge command without G85
        xydraw_pat2 = re.compile(r'^X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*)$')    # Plunge command without G85
        xdraw_pat = re.compile(r'^X([+-]?\d+)$')    # Plunge command, repeat last Y value
        ydraw_pat = re.compile(r'^Y([+-]?\d+)$')    # Plunge command, repeat last X value
        match = xydraw_pat.match(string)
        if match:
            x, y = xln2tenthou(match.groups(), divisor, excelonFormat.getDigits(), excelonFormat.zeroSuppression)
            return PlungeCommand(Coordinates(x, y))
        match = xydraw_pat2.match(string)
        if match:
            x, y = xln2tenthou2(match.groups(), divisor, excelonFormat.getDigits())
            return PlungeCommand(Coordinates(x, y))
        match = xdraw_pat.match(string)
        if match:
            x = xln2tenthou(match.groups(),divisor, excelonFormat.getDigits(), excelonFormat.zeroSuppression)[0]
            return PlungeCommand(Coordinates(x, lastCoordinates.y))
        match = ydraw_pat.match(string)
        if match:
            y = xln2tenthou(match.groups(),divisor, excelonFormat.getDigits(), excelonFormat.zeroSuppression)[0]
            return PlungeCommand(Coordinates(lastCoordinates.x, y))
        return None

    def toString(self, excelonFormat):
        return

    def toDict(self):
	if self.tool:
            tool = self.tool.toDict()
        else:
            tool = None
        return dict({'command': 'Plunge','tool': tool, 'coordinates': self.coordinates.toDict()})

    @staticmethod
    def fromDict(dictionary):
        return PlungeCommand(Coordinates.fromDict(dictionary['coordinates']), dictionary['tool'])

    def getCoordinates(self):
        return self.coordinates

#---------------------------------------------------------------------
class SlotCommand(Command):
    def __init__(self, startCoordinates, endCoordinates, tool=None):
        self.startCoordinates = startCoordinates
        self.endCoordinates = endCoordinates
        self.tool = tool

    @staticmethod
    def fromString(string, excelonFormat, divisor):
        xydraw_pat = re.compile(r'^X([+-]?\d+)Y([+-]?\d+)G85X([+-]?\d+)Y([+-]?\d+)$')    # Plunge command with G85
        xydraw_pat2 = re.compile(r'^X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*)G85X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*)$')    # Plunge command with G85
        match = xydraw_pat.match(string)
        if match:
            x, y, stop_x, stop_y = xln2tenthou(match.groups(), divisor, excelonFormat.getDigits(), excelonFormat.zeroSuppression)
            return SlotCommand(Coordinates(x, y), Coordinates(stop_x, stop_y))
        match = xydraw_pat2.match(string)
        if match:
            x, y, stop_x, stop_y = xln2tenthou2(match.groups(), divisor, excelonFormat.getDigits())
            return SlotCommand(Coordinates(x, y), Coordinates(stop_x, stop_y))
        return None

   # def toString(self, excellonFormat):
   #     return ''

    def toDict(self):
        return {'command' : 'Slot', 'startCoordinates' : self.startCoordinates, 'endCoordinates' : self.endCoordinates, 'tool' : self.tool}

    def getCoordinates(self):
        return (self.startCoordinates, self.endCoordinates)

#---------------------------------------------------------------------
class Tool:
    def __init__(self, number, diameter):
        self.number = number # T#
        self.diameter = diameter # C#
        self.zAxisFeedRate = None # optional, F#
        self.zAxisRetractRate = None # optional, B#
        self.rotationSpeed = None # optional, S#

    @staticmethod
    def fromString(string, filename):
        # Patterns for Excellon interpretation
        xtdef_pat = re.compile(r'^(T\d+)(?:F\d+)?(?:S\d+)?C([0-9.]+)$') # Tool+diameter definition with optional
                                                                # feed/speed (for Protel)
        xtdef2_pat = re.compile(r'^(T\d+)C([0-9.]+)(?:F\d+)?(?:S\d+)?$') # Tool+diameter definition with optional
                                                                # feed/speed at the end (for OrCAD)

        # See if a tool is being defined. First try to match with tool name+size
        matchA = xtdef_pat.match(string)    # xtdef_pat and xtdef2_pat expect tool name and diameter
        matchB = xtdef2_pat.match(string) # and xtdef_2pat expects feed/speed at the end
        if matchA is None and matchB is None:
            return None
        if matchA:
            match = matchA
        else:
            match = matchB

        currtool, diam = match.groups()
        try:
            diam = float(diam)
        except:
            raise RuntimeError, "File %s has illegal tool diameter '%s'" % (filename, diam)

        # Canonicalize tool number because Protel (of course) sometimes specifies it
        # as T01 and sometimes as T1. We canonicalize to T01.
        currtool = 'T%02d' % int(currtool[1:])
        return Tool(currtool, diam)

    def toDict(self):
        return dict({'tool': self.number, 'diam': self.diameter})

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
    def __init__(self, expectedExcellonFormat=None):
        self.ToolList = {}
        self.expectedExcellonFormat = expectedExcellonFormat
        self.excellonFormatFromHeader = ExcellonFormat(integerPart=None, decimalPart=None, units=None, zeroSuppression=None)
        self.toolList = {'PTH': [], 'NPTH': []}
        self.commands = {'PTH': [], 'NPTH': []}

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
        if filename.lower().find('npth') > -1:
          layer = 'NPTH'
          platingOption = 'NON_PLATED'
        else:
          layer = 'PTH'
          platingOption = 'PLATED'

        currtool = None
        for line in header.splitlines():
            line = line.strip()
            # Check for measurement unit and for leading/trailing zeros included ("INCH,LZ" or "INCH,TZ" or "METRIC,LZ" or "METRIC,TZ")
            match = unitAndZerosPosition.match(line)
            if match:
                unit, zerosPosition = match.groups()
                if unit == "INCH":
                    self.excellonFormatFromHeader.units = 'inch'
                elif unit == "METRIC":
                    self.excellonFormatFromHeader.units = 'metric'
                else:
                    raise "Unsupported measurement unit."

                if zerosPosition == "LZ":
                    self.excellonFormatFromHeader.zeroSuppression = 'trailing'
                elif zerosPosition == "TZ":
                    self.excellonFormatFromHeader.zeroSuppression = 'leading'
                else:
                    raise "Unsupported zero suppression command"

            match = fileFormat.match(line)
            if match:
                numbersStr, decimalsStr = match.groups()
                print numbersStr + ':' + decimalsStr
                self.excellonFormatFromHeader.integerPart = int(numbersStr)
                self.excellonFormatFromHeader.decimalPart = int(decimalsStr)

            match = plating.match(line)
            if match:
                platingOption = match.group(1)
            #print platingOption

            tool = Tool.fromString(line, filename)
            if tool:
                if tool in self.toolList[layer]:
                    raise RuntimeError, "File %s defines tool %s more than once" % (filename, currtool)
                self.toolList[layer].append(tool)
                continue

    def getToolDiameter(self, tool, filename, layer):
        # Diameter will be obtained from embedded tool definition, local tool list or if not found, the global tool list
        try:
            for tool in self.toolList[layer]:
                if tool.tool == tool:
                    diam = tool.diam
        except:
            if self.ToolList:
                try:
                    diam = self.ToolList[layer][tool]
                except:
                    raise RuntimeError, "File %s uses tool code %s that is not defined in the job's tool list" % (filename, tool)
            else:
                try:
                    diam = config.DefaultToolList[layer][tool]
                except:
                    raise RuntimeError, "File %s uses tool code %s that is not defined in default tool list" % (filename, tool)
        return diam

    def getToolFromToolList(self, toolnumber, layer):
        for tool in self.toolList[layer]:
            if tool.number == toolnumber:
                return tool
        return None

    def parseContent(self, content, filename):
        excellonFormat = self.excellonFormatFromHeader
        divisor = 10.0**(4 - excellonFormat.decimalPart)
        lastCoordinates = None
        currtool = None

        if filename.lower().find('npth') > -1:
            layer = 'NPTH'
        else:
            layer = 'PTH'

        for line in content.splitlines():
            toolCommand = ToolchangeCommand.fromString(line)
            if toolCommand:
                if toolCommand.toString() != 'T00': # KiCad specific fixes, tool T00 is KiCad specific
                    currtool = self.getToolFromToolList(toolCommand.toString(), layer)
                continue

            command = PlungeCommand.fromString(line, excellonFormat, lastCoordinates, divisor)
            if command:
                lastCoordinates = command.getCoordinates()
                if currtool is None:
                    raise RuntimeError, 'File %s has plunge command without previous tool selection' % filename
                command.tool = currtool
                self.commands[layer].append(command)
                continue

            slotCommand = SlotCommand.fromString(line, excellonFormat, divisor)
            if slotCommand:
                if currtool is None:
                    raise RuntimeError, 'File %s has plunge command without previous tool selection' % filename
                slotCommand.tool = currtool
                self.commands[layer].append(slotCommand)
                continue

            # It had better be an ignorable
            for pat in XIgnoreList:
                if pat.match(line):
                    break
            else:
                raise RuntimeError, 'File %s has uninterpretable line:\n  %s' % (filename, line)

    def loadFile(self, filename):
        print 'Reading data from %s ...' % filename
        fileContent = file(filename, 'rt')
        header, content, footer = self.spliteFile(fileContent)
        self.parseHeader(header, filename)
        self.excellonFormatFromHeader.fillNoneFields(self.expectedExcellonFormat)
        if self.expectedExcellonFormat.isEqualSkipNone(self.excellonFormatFromHeader) == False:
            print "Expected excellon file format:"
            print self.expectedExcellonFormat
            print "But form header data decoded excellon fotmat:"
            print self.excellonFormatFromHeader
            raise RuntimeError, "Mismatch in excellon format configuration."

        self.parseContent(content, filename)

    def toJsonFile(self, filename, layer):
        import json
        commandsList = []
        for command in self.commands[layer]:
            commandsList.append(command.toDict())

        fileContent = {'OryginalFileFormat': self.excellonFormatFromHeader.toDict(), 'ToolList': self.toolList, 'Commands': commandsList }
        with open(filename, 'w') as outfile:
            outfile.write(json.dumps(fileContent, indent=4, sort_keys=True, separators=(',', ': ')))

    #deprecated functin should be removed when other part of gerbmerge will be changed
    def getToollist(self):
        return None

    #deprecated functin should be removed when other part of gerbmerge will be changed
    def getxdiam(self, layer):
        xdiam = {}
        for tool in self.toolList[layer]:
            xdiam[tool.toDict()['tool']] = tool.toDict()['diam']
        return xdiam

    #deprecated functin should be removed when other part of gerbmerge will be changed
    def getxcommands(self, layer):
        xcommands = {}
        for command in self.commands[layer]:
            if isinstance(command, PlungeCommand):
                tmp = (command.getCoordinates().x, command.getCoordinates().y, None, None)
            else:
                tmpStart, tmpStop = command.getCoordinates()
                tmp = (tmpStart.x, tmpStart.y, tmpStop.x, tmpStop.y)

            if command.tool.toDict()['tool'] in xcommands:
                xcommands[command.tool.toDict()['tool']].append(tmp)
            else:
                xcommands[command.tool.toDict()['tool']] = [tmp]
        return xcommands

def main():
    import argparse
    import datetime
    scriptStartTime = datetime.datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="Path to excelon file that will be parsed.")
    parser.add_argument("-u", "--units", help="Type of units used in excellon file, possible options: inch, metric")
    parser.add_argument("-d", "--digits", help="Digit format used in file, possible values: 2:4, 2:5, etc.")
    parser.add_argument("-s", "--zeroSuppression", help="Kind of zerro suppresion used in file, possible options: leading, trailing")
    args = parser.parse_args()

    excellonFormatFromArguments = ExcellonFormat(integerPart=2, decimalPart=5, units=args.units, zeroSuppression=args.zeroSuppression)
    p = excellonParser(expectedExcellonFormat=excellonFormatFromArguments)
    p.loadFile(args.file)
   # p.parseExcellon('test.txt')
    p.toJsonFile('test.json')
    print "execution time: " + str(datetime.datetime.now() - scriptStartTime)

if __name__=="__main__":
    main()
