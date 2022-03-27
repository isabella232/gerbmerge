rusEFI note: this fork uses python 3!

<P><FONT SIZE="+2">GerbMerge -- A Gerber-file merging program</FONT></P>

<P><HR ALIGN=LEFT></P>

<H2>What's New</H2>
<p>In release 1.9.4</p>
<ul>
<li>Metric support fixed and tested with Diptrace</li>
<li>Support for Cygwin environment</li>
<li>Fixed Windows installation</li>
<li>Some Gerber parsing fixes</li>
</ul>

<p>In release 1.9</p>
<ul>
<li>Added metric support</li>
<li>Added default timeout for random tile placement</li>
<li>Added DipTrace support</li>
<li>Use boardoutline files (when present) to build cutlines in silkscreen layers instead of the default calculated algorithm. This change permits non-rectangular board outlines.</li>
</ul>
<P>In release 1.8:
<UL>
<LI>Released under more recent GPL v3 license</LI>
<LI>Summary statistics prints out smallest drill tool diameter</LI>
<LI>Added <A HREF="cfgfile.html#FiducialPoints"><TT>FiducialPoints</TT></A>, <A HREF="cfgfile.html#FiducialCopperDiameter"><TT>FiducialCopperDiameter</TT></A>, and <A HREF="cfgfile.html#FiducialMaskDiameter"><TT>FiducialMaskDiameter</TT></A> configuration options</LI>
<LI>Added option to write fiducials to final panel</LI>
<LI>Scoring lines now go all the way across a panel</LI>
</UL>

<P>In release 1.7:
<UL>
<LI>Added a new command-line option <TT>--search-timeout</TT> to time-limit the automatic placement process.</LI>
<LI>Added preliminary support for a GUI controller interface.</LI>
</UL>

<P><A NAME="Introduction"></A></P>
<H2>Introduction</H2>

  <P>GerbMerge is a program for combining (panelizing) the CAM data from multiple printed
  circuit board designs into a single set of CAM files. The purpose of
  doing so is to submit a single job to a board manufacturer, thereby saving on manufacturing costs.
  <P>GerbMerge currently works with:
  <UL>
  <LI>CAM data generated by the <A HREF="http://www.cadsoft.de">Eagle</A> and
      <A HREF="http://www.diptrace.com">DipTrace</A> circuit board
      design programs, with &quot;best effort&quot; support for Orcad, Protel, and <A HREF="http://www.sourceforge.net/projects/pcb">PCB</A></LI>
  <LI>Artwork in Gerber RS274-X format</LI>
  <LI>Drill files in Excellon format</LI>
  </UL>
  Here is <A HREF="doc/sample.jpg">one sample</A> and <A HREF="doc/sample2.jpg">another sample</A> of the program's output. These samples
  demonstrate panelizing multiple, different jobs, and also demonstrate board rotation.


<P><A NAME="Requirements"></A></P>
<H2>Requirements</H2>
  <P>GerbMerge is written in pure <A HREF="http://www.python.org">Python</A>. It
  depends upon the following packages for operation:
  <UL>
  <LI><A HREF="http://www.python.org">Python</A> version 2.4 or later</LI>
  <LI><A HREF="http://simpleparse.sourceforge.net">SimpleParse</A> version 2.1.0 or later</LI>
  </UL>
  <P>All of the above packages come with easy installation programs for both Windows, Mac OS X,
  and Linux.


## Automatic Installation with PIP

This repository can generate a tarball for installation with PIP. In the repository, run:
```
$ python setup.py sdist
$ pip install dist/gerbmerge-1.9.4.tar.gz
```

PIP will automatically resolve the dependencies. `-1.9.4` will change with the current tool version.

To easily run the installed package without looking up your python path, use python's "run module as script" feature:
```
$ python -m gerbmerge <args>
```


<P><A NAME="Installation"></A></P>
<H2>Installation</H2>

<H3>Windows / Cygwin</H3>
<p>Install Cygwin with <i>python</i>, <i>python-setuptools</i>, and <i>gcc</i> packages (gcc is needed
for simpleparse). Launch Cygwin shell and install <i>pip</i>, then <i>simpleparse</i>:
<ul>
<pre>
easy_install-x.y pip
pip install simpleparse
</pre>
</ul>
<p>(x.y is the current Python version)
<p>Donwload and unpack <i>gerbmerge</i> sources, navigate to its folder in Cygwin shell and run:
<ul>
<pre>
python setyp.py sdist
pip install dist/gerbmerge-1.9.4.tar.gz
</pre>
</ul>
<p>Now you can use it by running <i>gerbmerge</i> in Cygwin shell.

<p>To uninstall gerbmerge, launch Cygwin shell and run:
<ul>
<pre>
pip uninstall gerbmerge
</pre>
</ul>

<H3>Windows (native)</H3>

<p><a href="https://www.python.org/downloads/release/python-2711/">Download</a> and install Python-2.7,
<i>pip</i> will be installed too. Assuming Python installation folder is C:\Python27, open command propmt
and run:
<ul>
<pre>
cd c:\python27\
scripts\pip.exe install simpleparse
</pre>
</ul>

<p><p>Donwload and unpack <i>gerbmerge</i> sources, navigate to its folder and run:
<ul>
<pre>
c:\python27\python.exe setyp.py sdist
c:\python27\scripts\pip.exe istall dist\gerbmerge-1.9.4.zip
</pre>
</ul>

<p>Now you can use it by running <i>c:\python27\gerbmerge.bat</i> in command prompt.

<p>To uninstall gerbmerge, launch command prompt and run:
<ul>
<pre>
c:\python27\scripts\pip.exe uninstall gerbmerge
</pre>
</ul>

<H3>Unix / Mac OS X</H3>
<p>Install python, gcc (required to build simpleparse), and pip (recommended)
<p>Launch shell and install <i>simpleparse</i>:
<ul>
<pre>
sudo pip install simpleparse
</pre>
</ul>
<p>Donwload and unpack <i>gerbmerge</i> sources, navigate to its folder and run:
<ul>
<pre>
python setyp.py sdist
sudo pip istall dist/gerbmerge-1.9.4.tar.gz
</pre>
</ul>
<p>Now you can use it by running <i>gerbmerge</i>.

<p>To uninstall gerbmerge, open shell and run:
<ul>
<pre>
sudo pip uninstall gerbmerge
</pre>
</ul>

<P><A NAME="Running"></A></P>
<H2>Running GerbMerge</H2>

<H3>Windows / Cygwin</H3>

<p>Launch Cygwin shell and type
<ul>
<pre>
gerbmerge
</pre>
</ul>

<H3>Windows (native)</H3>
<P>Open a DOS command prompt and laucnh gerberge.bat file:
<PRE><CENTER>c:\python27\gerbmerge.bat</CENTER></PRE>

<H3>Unix / Mac OS X</H3>
<p>Open shell and type
<ul>
<pre>
gerbmerge
</pre>
</ul>

<H3>Operation</H3>
There are three ways to run GerbMerge:
<OL><LI>By manually specifying the relative placement of jobs</LI>
<LI>By manually specifying the absolute placement of jobs</LI>
<LI>By letting GerbMerge automatically search for a placement that minimizes total panel area</LI>
</OL>
<H4>Manual Relative Placement</H4>
For the manual relative placement approach, GerbMerge needs two input text files:
<UL>
<LI><P>The <I>configuration file</I> specifies global options and defines the jobs
to be panelized</LI>
<LI><P>The <I>layout file</I> specifies how the jobs are to be laid out.</LI>
</UL>
<P>The names of these files are the two required parameters to GerbMerge:
<PRE><CENTER>gerbmerge file.cfg file.def</CENTER></PRE>
<P>The following links describe the contents of the <A HREF="cfgfile.html">configuration
file</A> and <A HREF="layoutfile.html">layout file</A>.
<H4>Manual Absolute Placement</H4>
<P>For the manual absolute placement approach, GerbMerge also needs the configuration file
as well as another text file that specifies where each job is located on the panel and
whether or not it is rotated:
<PRE><CENTER>gerbmerge --place-file=place.txt file.cfg</CENTER></PRE>
<P>The <TT>place.txt</TT> file looks something like:
<PRE>job1 0.100 0.100
cpu 0.756 0.100
cpu*rotated 1.35 1.50
</PRE>
<P>This method of placement is not meant for normal use. It can be used to recreate
a previous invocation of GerbMerge, since GerbMerge saves its results in a text file
(whose name is set in the <A HREF="cfgfile.html#MergeOutputFiles"><TT>[MergeOutputFiles]</TT></A>
section of the configuration file) after every run. Thus, you can experiment with
different parameters, save a placement you like, do some more experimentation, then return
to the saved placement if necessary.
<P>Alternatively, this method of placement can be used with third-party back ends that
implement intelligent auto-placement algorithms, using GerbMerge only for doing the
actual panelization.
<H4>Automatic Placement</H4>
<P>For the <A HREF="autosearch.html">automatic placement</A> approach, GerbMerge only needs the configuration file:
<PRE><CENTER>gerbmerge file.cfg</CENTER></PRE>
Command-line options can be used to modify the search algorithm. See the
<A HREF="autosearch.html">Automatic Placement</A> page for more information.
<H3>Input File Requirements</H3>
GerbMerge requires the following input CAM files:
<UL>
<LI><P>Each job must have a Gerber file describing the board outline, which is assumed
rectangular. In Eagle, a board outline is usually generated from the Dimension layer.
This board outline is a width-0 line describing the physical extents of the board. If you're
not using Eagle, you don't have to generate a width-0 rectangle, but GerbMerge does need
to use some Gerber layer to determine the extents of the board. GerbMerge will take the maximum
extents of all drawn objects in this layer as the extents of the board.</LI>
<LI><P>Each job must have an Excellon drill file.</LI>
<LI><P>Each job can have any number of optional Gerber files describing copper
layers, silkscreen, solder masks, etc.</LI>
<LI><P>All files must have the same offset and must be shown looking from the
top of the board, i.e., not mirrored.</LI>
<LI><P>Each job may have an optional tool list file indicating the tool names
used in the Excellon file and the diameter of each tool. This file is not necessary
if tool sizes are embedded in the Excellon file. A typical tool list file looks like:
<PRE>
          T01 0.025in
          T02 0.032in
          T03 0.045in
</PRE>          
</UL>

<P><A NAME="Verifying"></A></P>
<H2>Verifying the Output</H2>

<P>Before sending your job to be manufactured, it is imperative that you verify
the correctness of the output. Remember that GerbMerge comes with NO WARRANTY.
Manufacturing circuit boards costs real money and a single mistake can render
an entire lot of boards unusable.
<P>I recommend the following programs for viewing the final output data. Take
the time to become very familiar with at least one of these tools and to use
it before every job you send out for manufacture.
<DL>
<DT><B>gerbv</B></DT>
<DD>For Linux, the best option (currently) for viewing Gerber and Excellon files
is the <A HREF="http://gerbv.sourceforge.net"><TT>gerbv</TT></A> program. Simply
type in the names of all files generated by GerbMerge as parameters to <TT>gerbv</TT>:
<CENTER><PRE>gerbv merged.*.ger merged.*.xln</PRE></CENTER></DD>
<DT><B>GC-Prevue</B></DT>
<DD><P>For Windows, <A HREF="http://www.graphicode.com">GC-Prevue</A> is a good program
that I have used often. It is a free program. GraphiCode makes lots of other, more
powerful Gerber manipulation and viewing programs but they are quite pricey ($495 and up).</DD>
<DT><B>ViewMate</B></DT>
<DD><P>Another free Windows program, <A HREF="http://www.pentalogix.com">ViewMate</A> is similar
to GC-Prevue. I have not used ViewMate much, but that is mostly due to familiarity with
GC-Prevue. The two programs are comparable, although I'm sure that someone who is much
more familiar with both could point out some differences.</DD>
</DL>

<P><A NAME="Limitations"></A></P>
<H2>Limitations</H2>

<UL>
<LI>This program has mainly been tested with output from Eagle CAD and Diptrace programs.
Limited testing has been performed with Orcad, Protel, and PCB.
Other CAD programs will NOT WORK with a very high probability, as the input
parser is quite primitive.
<P>If you have the need/motivation to adapt GerbMerge to other CAD programs,
have a look at the <TT>gerber2pdf</TT> program. It is written in Python and
implements a much more complete RS274-X input file parser. Combining GerbMerge
with <TT>gerber2pdf</TT> should be a fairly simple exercise. Also, feel free to
send us samples of Gerber/Excellon output of your CAD tool and we'll see if we can
add support for it.
<LI><P>This program handles apertures that are rectangles, ovals, circles, macros
without parameters or operators, and Eagle octagons (which are defined using a macro with a single parameter, hence currently handled as a special case).
<LI><P>The panelizing capabilities of this program do not allow for arbitrary
placement of jobs, although there is a fair amount of flexibility.
<LI><P>All jobs are assumed to be rectangular in shape. Non-rectangular jobs
can be handled but will lead to wasted space in the final panel.
<LI><P>A maximum of 26 different drill sizes is supported for generating a
fabrication drawing.</LI>
</UL>

<P><A NAME="ProgramOptions"></A></P>
<H2>Program Options</H2>

  <DL>
   <DT>--octagons=normal</DT>
   <DT>--octagons=rotate</DT>
   <DD>The <TT>--octagons</TT> option affects how the octagon aperture is defined in the output files. The parameter 
  to this option must either be <TT>rotate</TT> or <TT>normal</TT>. Normally,
  octagons begin at an angle of 22.5 degrees, but some Gerber viewers have a problem
  with that (notably CircuitMaker from LPKF). These programs expect octagons to begin
  at 0.0 degrees.
  <P>The <TT>--octagons=normal</TT> option is the default (22.5 degrees) and need not
  be specified. A rotation of 0.0 degrees can be achieved by specifying <TT>--octagons=rotate</TT>.</DD>

   <P><DT>--random-search</DT>
   <DD>This option is the default when only a configuration file is specified (see the documentation on <A HREF="autosearch.html">Automatic Placement</A> for more information). It indicates that a randomized search of possible job tilings is
   to be performed. This option does not make sense when a layout file is specified.</DD>

   <P><DT>--full-search</DT>
   <DD>This option may be specified to indicate that all possible job tilings are to be searched (see the documentation on <A HREF="autosearch.html">Automatic Placement</A> for more information). This option does not make sense when a layout file
   is specified.</DD>

   <P><DT>--rs-fsjobs=N</DT>
   <DD>This option is used with randomized search to indicate how many jobs are to undergo full search for each tiling. See the documentation on <A HREF="autosearch.html">Automatic Placement</A> for more information.</DD>

   <P><DT>--place-file=filename</DT>
   <DD>This option performs a panel layout based upon absolute job positions in
   the given text file, rather than by random/full search or by a layout file.
   The placement file created by GerbMerge can be used as an input file to 
   this option in order to recreate a previous layout.</DD>

   <P><DT>--no-trim-gerber</DT>
   <DD>This option prevents GerbMerge from trying to trim all Gerber data to lie within the
   extents of a given job's board outline. Normally, GerbMerge will try to do so to prevent
   one job's Gerber data (most notably, silkscreen lines for connectors that protrude from
   the board) from interfering with a neighboring job on the final panel. Specify this
   command-line option if you do not want this trimming to occur.</DD>

   <P><DT>--no-trim-excellon</DT>
   <DD>This option prevents GerbMerge from trying to trim all Excellon data to lie within the
   extents of a given job's board outline. Normally, GerbMerge will try to do so to prevent
   one job's drill holes from landing in the middle of a neighboring job on the final panel. Specify
   this command-line option if you do not want this trimming to occur.</DD>

   <P><DT>--search-timeout=seconds</DT>
   <DD>When random placements are used, this option can be used to automatically terminate the
   search process after the specified number of seconds. If the number of seconds is 0 or this
   option is not specified, then random placements are tried forever, until Ctrl-C is pressed
   to stop the process and keep the best placement so far.</DD>

   <P><DT>-h, --help</DT>
   <DD>The '<TT>-h</TT>' or '<TT>--help</TT>' option prints a brief summary of available options.

   <P><DT>-v, --version</DT>
   <DD>The '<TT>-v</TT>' or '<TT>--version</TT>' option prints the current program version and author contact information.</DD>
  </DL>

<P><A NAME="Examples"></A></P>
<H2>Examples</H2>
<p>Example layout config files and gerber files (both original and merged) can be found in gerbmerge/examples folder
  
<P><A NAME="Copyright"></A></P>
<H2>Copyright &amp; License</H2>

  <p>Copyright &copy; 2016 <a href="http://www.unwireddevices.com">Unwired Devices LLC</a>.

  <p>This repo is a fork of gerbmerge, version 1.9 from ProvideYourOwn.com, with additional patches by
  Ian Hartwig and Paulo Henrique Silva</p>
  
  <p>Copyright &copy; 2013 <a href="http://provideyourown.com">ProvideYourOwn.com</a>. All Rights Reserved.

  <p>This repo is a fork of gerbmerge, version 1.8 from Rugged Circuits LLC: </p>

  <P>Copyright &copy; 2011 <A HREF="http://ruggedcircuits.com">Rugged Circuits LLC</A>. All Rights Reserved.
  mailto: <A HREF="mailto:support@ruggedcircuits.com?subject=GerbMerge">support@ruggedcircuits.com</A>
  <P>GerbMerge comes with ABSOLUTELY NO WARRANTY. This
  is free software licensed under the terms of the <A HREF="gpl.html">GNU General
  Public License</A> Version 3. You are welcome to copy, modify and redistribute this software
  under certain conditions. For more details, see the LICENSE file or
  visit <A HREF="http://www.fsf.org">The Free Software Foundation</A>.

<P><A NAME="Todo"></A></P>
<H2>To Do</H2>

  <ol>
    <li>Proper metric/inch support: parse files with arbitrary units, output files with units
	specified in the config</li>
    <LI>Accept outputs from more CAD programs</LI>
    <LI>A graphical interface for interactive placement</LI>
    <LI>Better reporting of parse errors in the layout and configuration files</LI>
    <LI>Implement simple primitive for panelizing a single job in an array</LI>
    <LI>More intelligent placement algorithms, possibly based on the fabric cutting problem.</LI>
    <LI>Accept aperture macro parameters and operators
  </OL>

<P><A NAME="Credits"></A></P>

<H2>Credits</H2>
  <P>Thanks to Jace Browning for major contributions to this code. This help file is based on a template for the help file for mxTools
  by <A HREF="http://starship.python.net/crew/lemburg">M.A. Lemburg</A>.
  This software was created with <A HREF="http://www.vim.org/">VIM</A>;
  thanks to the authors of this program and special thanks for
  the Python syntax support. Thanks to M.A. Lemburg for his
  <A HREF="http://www.egenix.com/files/python/eGenix-mx-Extensions.html">mxBase</A>
  package, Mike Fletcher for his
  <A HREF="http://simpleparse.sourceforge.net">SimpleParse</A> package, and
  the authors of <A HREF="http://gerbv.sourceforge.net">gerbv</A>, a great
  Gerber file viewer for Linux/Mac OS X, and, of course, to the
  <A HREF="http://www.python.org">Python</A> developers and
  support community.</P>
  <P>Thanks to Joe Pighetti for making me start writing this program, and to
  the Grand Valley State University Firefighting Robot Team for making me finish it.</P>
  <P>Thanks to Matt Kavalauskas for identifying Eagle's annulus and thermal macros and supporting
  the development of the aperture macro code.</P>
  <P>Thanks to Bohdan Zograf for the <A HREF="http://webhostingrating.com/libs/gerbmerge-be">Belorussian translation</A> of this documentation.</P>

<HR ALIGN=LEFT>

<center><font size="-1">
<p>Copyright &copy; 2016 <a href="http://www.unwireddevices.com">Unwired Devices LLC</a>. All Rights Reserved.</p>
<p>Portions (version 1.9.3 & prior): Copyright &copy; 2013 <a href="http://provideyourown.com">ProvideYourOwn.com</a>. All Rights Reserved.</p>
<p><center><font size="-1">Portions (version 1.8 & prior): Copyright &copy; 2003-2011, Copyright by <A HREF="http://ruggedcircuits.com">Rugged Circuits LLC</A>; All Rights Reserved. mailto: <A HREF="mailto:support@ruggedcircuits.com?subject=GerbMerge">support@ruggedcircuits.com</A></p></font></center>
