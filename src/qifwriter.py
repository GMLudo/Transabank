#! /usr/bin/env python
# -*- coding: utf-8 -*-

import datetime


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

    if not entry['message'] is None:
        str.append( "M" + entry['message']  )

    if not entry['number'] is None:
        str.append( "N" + entry['number']  )

    # Cleared status: always mark 'reconciled'
    str.append( "C" + "r"  )

    # append a category
    str.append( "L" + "Travel:Fares"  )

    return "\n".join(str) + "\n^"
# ===============================================================================