#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
def print_qif( entry ):

    str = []

    if not entry['date'] is None:
        str.append( "D" + time.strftime('%Y-%m-%d', entry['date']) )

    if not entry['amount'] is None:
        str.append( "T" + "%.2f" % entry['amount'] )

    if not entry['payee'] is None:
        str.append( "P" +  entry['payee'] )

    if not entry['address'] is None:
        if isinstance( entry['address'], tuple ):
            for item in entry['address']:
                str.append( "A" + item )
        else:
            str.append( "A" + entry['address'] )

    if not entry['message'] is None:
        str.append( "M" + entry['message']  )

    if not entry['number'] is None:
        str.append( "N" + entry['number']  )

    return "\n".join(str) + "\n^"
# ==============================================================================
#def qif_entry_proton( date, amount ):

    #message = "Proton"

    #str = "D" + time.strftime('%Y-%m-%d', date) + "\n" + \
          #"T" +  "%.2f" % amount + "\n" + \
          #"M" + message + "\n" + \
          #"^"
    #return str
## ==============================================================================
#def qif_interest( date, amount ):

    #message = "Interest and costs"

    #str = "D" + time.strftime('%Y-%m-%d', date) + "\n" + \
          #"T" +  "%.2f" % amount + "\n" + \
          #"M" + message + "\n" + \
          #"^"
    #return str
## ==============================================================================
#def qif_outgoing_national( date, amount, account_no, payee, address, message ):
    #str = "D" + time.strftime('%Y-%m-%d', date) + "\n" + \
          #"T" +  "%.2f" % amount + "\n" + \
          #"P" + ", ".join( [payee,account_no] ) + "\n" + \
          #"A" + "\nA".join(address) + "\n" + \
          #"M" + message + "\n" + \
          #"^"
    #return str
## ==============================================================================
#def qif_standing_national( date, amount, account_no, payee, address, order_no ):
    #message = "standing order"
    #if isinstance(address,str):
        #return "D" + time.strftime('%Y-%m-%d', date) + "\n" + \
              #"T" +  "%.2f" % amount + "\n" + \
              #"P" + ", ".join( [payee,account_no] ) + "\n" + \
              #"A" + address + "\n" + \
              #"M" + message + "\n" + \
              #"N" + order_no + "\n" + \
              #"^"
    #else:
        #return "D" + time.strftime('%Y-%m-%d', date) + "\n" + \
              #"T" +  "%.2f" % amount + "\n" + \
              #"P" + ", ".join( [payee,account_no] ) + "\n" + \
              #"A" + "\nA".join(address) + "\n" + \
              #"M" + message + "\n" + \
              #"N" + order_no + "\n"
## ==============================================================================
#def qif_bancontact( date, amount, account_no, payee ):
    #return "D" + time.strftime('%Y-%m-%d', date) + "\n" + \
           #"T" +  "%.2f" % amount + "\n" + \
           #"P" + ", ".join( [payee,account_no] ) + "\n" + \
           #"^"
## ==============================================================================
#def qif_atm( date, amount, location ):
    #return "D" + time.strftime('%Y-%m-%d', date) + "\n" + \
           #"T" +  "%.2f" % amount + "\n" + \
           #"N" + "ATM" + "\n" + \
           #"M" + location + "\n" + \
           #"^"
## ==============================================================================