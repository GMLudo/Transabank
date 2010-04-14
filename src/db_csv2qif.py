#! /usr/bin/env python
# -*- coding: utf-8 -*-

import dbreader
import ofxwriter
import qifwriter

# ==============================================================================
file_name = 'TransactionListHistory-sun.csv'
delim = ','

transactions, mc_transactions = dbreader.read_db_cvsfile( file_name, delim )

print qifwriter.print_qif( transactions )


# ==============================================================================