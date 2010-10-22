#!/usr/bin/env python
"""
Author: Brian Smith <pingwin@gmail.com>
Date: 2010/10/21
Description:
  Convert a IETF RFC txt format into an html document readable on the kindle.

  ./rfctxt2kindlehtml.py rfc1034.txt > rfc1034.html
"""

import sys, logging, getopt, os
try:
    from PIL import Image, ImageDraw
except ImportError, err:
    print err
    print "please install the python imaging library (PIL)"
    sys.exit(2)

def usage():
    """ print usage message """
    print "Convert IETF RFC TXT file to HTML for kindlegen"
    print "-h --help    This message"
    print "-v           verbosity"
    print "-i --input   input file"
    print "-o --output  output file"
    sys.exit(2)

def find_open_file(c=0):
    try:
        c += 1
        open('_file_%d.gif' % c)
    except IOError:
        return '_file_%d.gif' % c
    return find_open_file(c)

def create_image(picture_me):
    img = find_open_file()
    os.system("convert -font /usr/share/cups/fonts/Monospace label:'%s' %s" % (picture_me.replace("'", "\'"), img))
    return img

def is_image_part(line):
    chars = [
        '+-',
        '|',
        '---',
        '0                   1',
        '0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5',
        '  /  '
        ]
    for c in chars:
        if line.find(c) != -1:
            return True
    return False

def main():
    """ Begin process """
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hvi:o:",
                                   [
                                       'help',
                                       'input',
                                       'output'
                                       ])
    except getopt.GetoptError, err:
        logging.exception(err)
        usage()

    input      = None
    output    = None
    log_level = logging.ERROR
    for opt, a in opts:
        if opt in ('-h', '--help'):
            usage()
        if opt == '-v' and log_level > 10:
            log_level -= 10

        if opt in ('-i', '--input'):
            input = a
        if opt in ('-o', '--output'):
            output = a

    if not input or not output:
        usage()
    
    input  = open(input,  'r')
    output = open(output, 'w+')
    in_p   = False
    has_title = False
    in_toc    = False
    in_image  = False
    toc_itm   = 0
    buffer = []
    buffer.append('<body>')
    for line in input:
        if line.find('Table of Contents') != -1 or in_toc:
            # image
            if not in_toc:
                image = []
            if in_toc:
                image.append(line.replace('...', '.'))
                toc_itm += 1

            in_toc = True
            if len(line) < 2 and toc_itm > 1:
                buffer.append('<img src="%s" />' % create_image(''.join(image)))
                in_toc = False
            continue

        
        if line[:2] == '  ':
            if is_image_part(line):
                # image
                if not in_image:
                    image = []
                    in_image = True
                image.append(line)
                continue
            if not has_title:
                output.write('<title>%s</title>' % line)
                has_title = True
        if in_image:
            in_image = False
            buffer.append('<img src="%s" />' % create_image(''.join(image)))
            
        
        if len(line) < 2:
            if not in_p:
                buffer.append('<p>')
                in_p = True
            else:
                buffer.append('</p><br />')
                in_p = False
            continue
        
        buffer.append(line.replace("\n", ''))

    buffer.append('</body>')
    buffer = ''.join(buffer)

    output.write(buffer)
    input.close()
    output.close()

if __name__ == "__main__":
    main()
