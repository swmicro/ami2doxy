#!/usr/bin/python
# -*- coding: utf-8 -*-


import getopt, codecs, re, sys, os
import fnmatch
import shutil, errno
import glob



# file header
pattern_FHDR_start = r'^//(|.+)<AMI_FHDR_START>(|.+)$'
pattern_FHDR_end = r'^//(|.+)<AMI_FHDR_END>(|.+)$'

# file header
pattern_INT_FHDR_start = r'^//(|.+)<INT:AMI_FHDR_START>(|.+)$'
pattern_INT_FHDR_end = r'^//(|.+)<INT:AMI_FHDR_END>(|.+)$'

# headers
pattern_xHDR_start = r'^//(|.+)<AMI_.HDR_START>(|.+)$'
pattern_xHDR_end = r'^//(|.+)<AMI_.HDR_END>(|.+)$'
pattern_INT_xHDR_start = r'^//(|.+)<INT:AMI_.HDR_START>(|.+)$'
pattern_INT_xHDR_end = r'^//(|.+)<INT:AMI_.HDR_END>(|.+)$'

pattern_2slash = r'^//(|.+)'

pattern_procedure = r'^//(|.+)Procedure:'
pattern_name = r'^//(|.+)Name:'
pattern_description = r'^//(|.+)Description:'
pattern_input = r'^//(|.+)Input:'
pattern_output = r'^//(|.+)Output:'
pattern_return = r'^//(|.+)Return:'
pattern_notes = r'^//(|.+)Notes:'
pattern_line = r'^//(\*+|-+|=+)'


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    help_string ='Usage: ami2doxy -i <inputdir> -o <outputdir>'
    version_string = 'ami2doxy version 1.1' 
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:],"hvi:o:",["idir=","odir="])
        except getopt.error, msg:
            raise Usage(msg)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, help_string
        return 2

    for opt, arg in opts:
        if opt == '-h':
            print help_string
            sys.exit()
        elif opt == '-v':
            print version_string
            sys.exit()
        elif opt in ("-i", "--idir"):
            inputdir = os.path.abspath(arg)
        elif opt in ("-o", "--odir"):
            outputdir = os.path.abspath(arg)

    print inputdir, " => ", outputdir
    for root, dirnames, filenames in os.walk(inputdir):
        for filename in filenames:
            inputfile = os.path.join(root, filename)
            outputfile = inputfile.replace(inputdir,outputdir,1)
            print inputfile, outputfile
            if not os.path.exists(os.path.dirname(outputfile)):
                os.makedirs(os.path.dirname(outputfile))
            if fnmatch.fnmatch(filename, '*.c') or fnmatch.fnmatch(filename, '*.h'):
                try:
                    fin = codecs.open(inputfile, 'r')
                except IOError as e:
                    print 'Error: input file does not exist'
                    continue

                try:
                    fout = codecs.open(outputfile, 'w')
                except IOError as e:
                    print 'Error: can not create output file'
                    continue

                header_flag = False
                comment_flag = False
                for line in fin.readlines():
                
                    # escape comments frames: /* */ 
                    index1 = line.find('//')
                    index2 = line.rfind('/*')
                    index3 = line.rfind('*/')
                    if index1 != -1: 
                        if index1 < index2:
                            index2 = -1
                        if index1 < index3:
                            index3 = -1
                    if index2 > index3:
                        comment_flag = True
                        header_flag = False
                    elif index2 < index3:
                        comment_flag = False
                    
                    if comment_flag is False:
                        if re.match(pattern_FHDR_start, line) != None or re.match(pattern_INT_FHDR_start, line) != None:
                            header_flag = True
                            line = '/** @file ' + '\n'
                        elif re.match(pattern_xHDR_start, line) != None:
                            header_flag = True
                            line = '/** ' + '\n'
                        elif re.match(pattern_2slash, line) == None:
                            if header_flag is True:
                                line = ' **/ \n' + line
                            header_flag = False
                        elif header_flag is True:
                            if re.match(pattern_xHDR_end, line) != None or re.match(pattern_INT_xHDR_end, line) != None:
                                header_flag = False
                                line = '**/ ' + '\n' 
                            elif re.match(pattern_procedure, line) != None:
                                continue
                            elif re.match(pattern_name, line) != None:
                                continue
                            elif re.match(pattern_description, line) != None:
                                line = line.replace("Description:","",1)
                            elif re.match(pattern_input, line) != None:
                                line = line.replace("Input:","@param ",1)
                            elif re.match(pattern_output, line) != None:
                                line = line.replace("Output:","@retval ",1)
                            elif re.match(pattern_return, line) != None:
                                line = line.replace("Return:","@retval ",1)
                            elif re.match(pattern_notes, line) != None:
                                line = line.replace("Notes:","@note ",1)
                            elif re.match(pattern_line, line) != None:
                                continue
                            elif re.match(pattern_2slash, line) != None:
                                line = line.replace("//","  ",1)
                            else:
                                header_flag = False
                            if header_flag is True and re.match(pattern_2slash, line) != None:
                                line = line.replace("//","  ",1)
                        else:
                            header_flag = False
                    fout.write(line)
                
                fin.close()
                fout.close()
            else:
                try:
                    shutil.copy(inputfile, os.path.dirname(outputfile))
                except IOError as e:
                    print 'Error: can not copy the file'


if __name__ == "__main__":
    sys.exit(main())
