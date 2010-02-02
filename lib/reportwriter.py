#!/usr/bin/env python
#  Copyright (c) 2010 Corey Goldberg (corey@goldb.org)
#  License: GNU LGPLv3
#  
#  This file is part of Multi-Mechanize
#


class Report(object):
    def __init__(self, results_dir):
        self.results_dir = results_dir
        self.fn = results_dir + 'results.html'
        self.write_head_html()

    
    def write_line(self, line):
        with open(self.fn, 'a') as f:
            f.write('%s\n' % line)


    def write_head_html(self):
        with open(self.fn, 'w') as f:
            f.write("""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>Multi-Mechanize - Results</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <meta http-equiv="Content-Language" content="en" />
    <style type="text/css">
        body {
            background-color: #FFFFFF;
            color: #000000;
            font-family: Trebuchet MS, Verdana, sans-serif;
            font-size: 11px;
            padding: 10px;
        }
        h1 {
            font-size: 16px;
            margin-bottom: 0.5em;
            background: #FF9933;
            padding-left: 5px;
            padding-top: 2px;
        }
        h2 {
            font-size: 12px;
            background: #C0C0C0;
            padding-left: 5px;
            margin-top: 2em;
            margin-bottom: .75em;
        }
        h3 {
            font-size: 11px;
            margin-bottom: 0.5em;
        }
        h4 {
            font-size: 11px;
            margin-bottom: 0.5em;
        }
        p {
            margin: 0;
            padding: 0;
        }
        table {
            margin-left: 30px;
        }
        td {
            text-align: right;
            color: #000000;
            background: #FFFFFF;
            padding-left: 10px;
            padding-right: 8px;
            padding-bottom: 0px;
        }
        th {
            text-align: center;
            font-size: 12px;
            padding-right: 30px;
            padding-left: 30px;
            color: #000000;
            background: #C0C0C0;
        }
    </style>
</head>
<body>
""")
  

    def write_closing_html(self):
        with open(self.fn, 'a') as f:
            f.write("""\
<p><br /></p>
<hr />
</body>
</html>
""")





