import re
import string

# Patterns for Excellon interpretation
xtool_pat = re.compile(r'^(T\d+)$')           # Tool selection
xydraw_pat = re.compile(r'^X([+-]?\d+)Y([+-]?\d+)(?:G85X([+-]?\d+)Y([+-]?\d+))?$')    # Plunge command with optional G85
xydraw_pat2 = re.compile(r'^X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*)(?:G85X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*))?$')    # Plunge command with optional G85
xdraw_pat = re.compile(r'^X([+-]?\d+)$')    # Plunge command, repeat last Y value
ydraw_pat = re.compile(r'^Y([+-]?\d+)$')    # Plunge command, repeat last X value
xtdef_pat = re.compile(r'^(T\d+)(?:F\d+)?(?:S\d+)?C([0-9.]+)$') # Tool+diameter definition with optional
                                                                # feed/speed (for Protel)
xtdef2_pat = re.compile(r'^(T\d+)C([0-9.]+)(?:F\d+)?(?:S\d+)?$') # Tool+diameter definition with optional
                                                                # feed/speed at the end (for OrCAD)
xzsup_pat = re.compile(r'^(?:INCH|METRIC)(,([LT])Z)?$')      # Leading/trailing zeros INCLUDED

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
  
class coordinates:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0  
        
          

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
     
 # Helper function to convert X/Y strings into integers in units of ten-thousandth of an inch.
 @staticmethod
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

 # Helper function to convert X/Y strings into integers in units of ten-thousandth of an inch.
 @staticmethod
 def xln2tenthou2 (L, divisor, zeropadto):
      V = []
      for s in L:
        if s is not None:
          V.append(int(float(s)*1000*divisor))
        else:
          V.append(None)
      return tuple(V)
 
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
                print unit
                if unit == "INCH":
                    self.units = 'inch'
                elif unit == "METRIC":
                    self.units = 'metric'
                else:
                    raise "Unsupported measurement unit."
                print zerosPosition                
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
                
 def parseContent(self, content, filename):
        divisor = 10.0**(4 - (self.digits-2))
        for line in content.splitlines():
            # Didn't match TxxxCyyy. It could be a tool change command 'Tdd'.
            match = xtool_pat.match(line)
            if match:
                currtool = match.group(1)

                # Canonicalize tool number because Protel (of course) sometimes specifies it
                # as T01 and sometimes as T1. We canonicalize to T01.
                currtool = 'T%02d' % int(currtool[1:])

                # KiCad specific fixes
                if currtool == 'T00':
                    continue
                # end KiCad fixes
 
                # Diameter will be obtained from embedded tool definition, local tool list or if not found, the global tool list
                try:
                    diam = self.xdiam[currtool]
                except:
                    if self.ToolList:
                        try:
                            diam = self.ToolList[currtool]
                        except:
                            raise RuntimeError, "File %s uses tool code %s that is not defined in the job's tool list" % (filename, currtool)
                    else:
                        try:
                            diam = config.DefaultToolList[currtool]
                        except:
                            #print config.DefaultToolList
                            raise RuntimeError, "File %s uses tool code %s that is not defined in default tool list" % (filename, currtool)

                self.xdiam[currtool] = diam
                continue

            # Plunge command?
            match = xydraw_pat.match(line)
            if match:
                x, y, stop_x, stop_y = self.xln2tenthou(match.groups(), divisor, self.digits, self.zeroSuppression)
            else:
                match = xydraw_pat2.match(line)
                if match:
                    x, y, stop_x, stop_y = self.xln2tenthou2(match.groups(), divisor, self.digits)
                else:
                    match = xdraw_pat.match(line)
                    if match:
                        x = self.xln2tenthou(match.groups(),divisor, self.digits, self.zeroSuppression)[0]
                        y = last_y
                    else:
                        match = ydraw_pat.match(line)
                        if match:
                            y = self.xln2tenthou(match.groups(),divisor, self.digits, self.zeroSuppression)[0]
                            x = last_x      
              
            if match:
                if currtool is None:
                    raise RuntimeError, 'File %s has plunge command without previous tool selection' % filename

                try:
                    self.xcommands[currtool].append((x,y,stop_x,stop_y))
                except KeyError:
                    self.xcommands[currtool] = [(x,y,stop_x,stop_y)]
              
                print "X: " + str(x) + ", Y: " + str(y)  

                last_x = x
                last_y = y
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

