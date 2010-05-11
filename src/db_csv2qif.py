#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================================
#
# Copyright (C) 2010 Nico Schlömer
#
# This file is part of deutschebank2ofx.
#
# deutschebank2ofx is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# deutschebank2ofx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deutschebank2ofx.  If not, see <http://www.gnu.org/licenses/>.
#
# ==============================================================================
import dbreader
import ofxwriter
import qifwriter
# ==============================================================================
file_name = 'TransactionListHistory-sun.csv'
delim = ','

transactions, mc_transactions = dbreader.read_db_cvsfile( file_name, delim )

print qifwriter.print_qif( transactions )
#print ofxwriter.print_ofx( transactions )
# ==============================================================================