#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================================
#
# Copyright (C) 2010 Nico Schl"omer
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
import datetime
import categories
# ==============================================================================
def print_qif( entries ):

    str = []

    # first get the bank file
    str.append( "!Type:Bank" )
    str.append( "D" + datetime.date.today().isoformat() )
    str.append( "T0.00" )
    str.append( "CX" )
    str.append( "POpening Balance" )
    str.append( "L[dasd]" )
    str.append( "^" )

    # loop over all entries
    for entry in entries:
        str.append( print_qif_transaction(entry) )

    return "\n".join(str)
# ==============================================================================
def print_qif_transaction( entry ):

    str = []

    # Do not record credit card clearance;
    # this is accounted for on the credit card already.
    if entry['number'] == "Card clearance":
        return ''

    if not entry['date'] is None:
        str.append( "D" + entry['date'].isoformat() )

    if not entry['amount'] is None:
        str.append( "T" + "%.2f" % entry['amount'] )

    if not entry['payee'] is None:
        str.append( "P" +  entry['payee'] )

    # if the raw address is given, use it;
    # otherwise fall back to city, country, postal code (if given)
    if not entry['address'] is None:
        if isinstance( entry['address'], tuple ):
            for item in entry['address']:
                str.append( "A" + item )
        else:
            str.append( "A" + entry['address'] )
    else:
        if entry['city'] is not None and entry['postal code'] is not None:
            if entry['country']=='US':
                str.append( "A" +  entry['city'] + " " + entry['postal code'] )
            elif entry['country']=='BE' or entry['country']=='FR' or entry['country']=='DE':
                str.append( "A" +  entry['postal code'] + " " + entry['city']  )
            elif entry['country']=='GB':
                str.append( "A" + entry['city']  )
                str.append( "A" + entry['postal code']  )
            else:
                str.append( "A" +  entry['city'] + ", " + entry['postal code'] )
        if entry['country'] is not None:
            str.append( "A" +  entry['country'] )

    if entry['message'] is not None:
        str.append( "M" + entry['message']  )
    elif entry['location'] is not None:
        str.append( "M" + entry['location']  )

    if not entry['number'] is None:
        str.append( "N" + entry['number']  )

    # Cleared status: always mark 'reconciled'
    str.append( "C" + "r"  )

    # append a category
    cat = categories.get_category( entry )
    if cat is not None:
        str.append( "L" + cat )

    return "\n".join(str) + "\n^"
# ===============================================================================