#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time # for handling date strings
import re
import csv

# ==============================================================================
# Read a CSV file and return parsed lists of transaction of the regular account
# and transactions of the MasterCard account.
def read_db_cvsfile( file_name, delim = "," ):

    # read the file
    dbReader = csv.reader( open(file_name), delimiter=delim )

    transactions = []
    mc_transactions = []
    for row in dbReader:
        ta, is_mastercard_transaction = process_db_cvs_entry(row)
        if is_mastercard_transaction:
            transactions.append( ta )
        else:
            mc_transactions.append( ta )

    return transactions, mc_transactions
# ==============================================================================
def process_db_cvs_entry( row ):

    # Decode the columns.
    # This is DB Belgi\"e-specific.
    raw_date, message, account_amount, mastercard_amount, currency = row

    # get date
    date = get_formatted_date( raw_date )

    # Get 'amount'.
    is_mastercard_transaction = False
    if account_amount!="" and mastercard_amount=="":
        # account transaction
        amount = get_amount( account_amount )
    elif account_amount=="" and mastercard_amount!="":
        # mastercard transaction
        amount = get_amount( mastercard_amount )
        is_mastercard_transaction = True
    else:
        raise "Error."

    # extract the value date ("Valutadatum")
    message, value_date = extract_value_date( message )

    # strip "(18/04/09 14:09)"
    message = re.sub( "\(\d\d/\d\d/\d\d\xc2\xa0\d\d:\d\d\)", "", message )

    if is_mastercard_transaction:
        # handle mastercard transaction
        transaction = titanium( message )
    else:
        # handle regular transaction
        if proton(message) is not None:
            transaction = proton( message )
        elif interest(message) is not None:
            transaction = interest( message )
        elif outgoing_national( message ) is not None:
            transaction = outgoing_national( message )
        elif standing_national( message ) is not None:
            transaction = standing_national( message )
        elif bancontact( message ) is not None:
            transaction = bancontact( message )
        elif foreign_atm( message ) is not None:
            transaction = foreign_atm( message )
        elif standing_international( message ) is not None:
            transaction = standing_international( message )
        elif outgoing_international( message ) is not None:
            transaction = outgoing_international( message )
        elif incoming_transaction( message ) is not None:
            transaction = incoming_transaction( message )
        elif cards_clearance( message ) is not None:
            transaction = cards_clearance( message )
        elif direct_debit( message ) is not None:
            transaction = direct_debit( message )
        else:
            transaction = None
            raise "Could not decode entry."

    # merge the common entries into it
    transaction['date']   = date
    transaction['amount'] = amount
    transaction['value date'] = value_date

    return transaction, is_mastercard_transaction
# ==============================================================================
def get_formatted_date( raw_date ):
    # Decode 'date'.
    # DB has either long (2010) or short (10) year value, changing seemingly
    # randomly.
    try:
        date = time.strptime( raw_date, "%d/%m/%y" )
    except:
        date = time.strptime( raw_date, "%d/%m/%Y" )

    return date
# ==============================================================================
# gets a float value of a string such as "1.000,32" (=1000.32)
def get_amount( raw_amount ):
    # remove the thousand-delimiter and replace the decimal "," by
    # by a decimal "."
    amount = raw_amount.replace(".","").replace(",",".")
    return float( amount )
# ==============================================================================
def extract_value_date( message ):

    # get value date
    valuta_pattern = re.compile( ".* Valutadatum:\xc2\xa0(\d\d/\d\d/\d\d\d\d).*" )
    valdate = valuta_pattern.findall( message )
    if len(valdate)>0:
        value_date = time.strptime( valdate[0], "%d/%m/%Y" )
    else:
        value_date = None

    # strip "Valutadatum: xx/xx/xxxx"
    message = re.sub( " Valutadatum:\xc2\xa0\d\d/\d\d/\d\d\d\d", "", message )

    return message, value_date
# ==============================================================================
def empty_transaction():
    return { 'date': None,
             'amount': None,
             'account number': None,
             'bic': None,
             'iban': None,
             'payee': None,
             'address': None,
             'message': None,
             'number': None,
             'currency': None,
             'exchange rate': None,
             'location': None,
             'exchange fee': None,
             'payment fee': None,
             'value date': None }
# ==============================================================================
# Dissect something like
# Uw overschrijving 410-0659001-06 John Doe Voidstreet 5, 2610 Alabama 080/0163/21631 Valutadatum: 01/01/1900
def outgoing_national( str ):

    ret = empty_transaction()

    # match account number and address, e.g.,
    # "410-0659001-06 Onafhankelijkxc2\xa0Ziekenfonds Boomsesteenwgxc2\xa05, 2610xc2\xa0Antwerpen"
    pattern = re.compile( "^Uw\xc2\xa0overschrijving (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) ([^,]*), (\d\d\d\d \w*) (.*)" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['account number'] = res[0][0]
        ret['payee']      = res[0][1]
        ret['address']    = res[0][1:4]
        ret['message']    = res[0][4]
        return ret

    # without address, e.g.
    # "Uw overschrijving 310-1610249-38 Doe Inc. 1342235809 Valutadatum: 01/01/1900"
    pattern = re.compile( "^Uw\xc2\xa0overschrijving (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) (\d+).*" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['account number'] = res[0][0]
        ret['payee']      = res[0][1]
        ret['message']    = res[0][2]
        return ret

    return None
# ==============================================================================
# Dissect something like
# Uw overschrijving -- RABONL2UXXX NL29 RABO 0105 8855 09 John Doe Voidstreet 130 1071 XW Amsterdam NL Com: this is some communication Valutadatum: 01/01/1900
def outgoing_international( str ):

    ret = empty_transaction()

    # cut "Com: .*"
    comm_pattern = re.compile( ".* Com:\xc2\xa0(.*)$" )
    res = comm_pattern.findall( str )
    if len(res)==1:
        ret['message'] = res[0]
        str = re.sub(  " Com:\xc2\xa0.*$", "", str )

    # match account number and address, e.g.
    # "410-0659001-06 Johnxc2\xa0Doe Voidstreetxc2\xa05, 2610xc2\xa0Alabama"
    pattern = re.compile( "^Uw\xc2\xa0overschrijving -- ([^ ]*) (\w\w\d\d\xc2\xa0\w\w\w\w\xc2\xa0\d\d\d\d\xc2\xa0\d\d\d\d\xc2\xa0\d*)\xc2\xa0(.*)" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['bic'] = res[0][0]
        ret['iban'] = res[0][1]
        ret['payee'] = res[0][2]
        return ret

    # "Uw overschrijving -- BE80777591050277 Distr. Alabama -- Finances Voidstreet 22 Bus 111 2600 Alabama US Com: +++001/0028/72387+++"
    pattern = re.compile( "^Uw\xc2\xa0overschrijving -- (\w\w\d+) ([^ ]*) (.*)$" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['account number'] = res[0][0]
        ret['payee'] = res[0][1]
        ret['address'] = res[0][2]
        return ret

    # "Uw overschrijving -- BE42091010100254 ZNA - - BE Com: +++510/9515/61064+++ Valutadatum: 01/01/1900"
    pattern = re.compile( "^Uw\xc2\xa0overschrijving -- (\w\w\d+) ([^ ]*).*$" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['account number'] = res[0][0]
        ret['payee'] = res[0][1]
        return ret

    pattern = re.compile( "^Overschrijving\xc2\xa0naar\xc2\xa0het\xc2\xa0buitenland --$" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['message'] = "Transfer to foreign country"
        return ret

    return None
# ==============================================================================
# Dissect something like
# Overschrijving te uwen gunste 424-5530811-85 GBA VOIDSTREET 5, 1000 BRUSSEL /A/ WERKGEVER: 0123456 WERKNEMER: 0123456 001 DATUM: 01/01/1900 Valutadatum: 01/01/1900
def incoming_transaction( str ):

    ret = empty_transaction()

    # incoming national
    pattern = re.compile( "^(Overschrijving\xc2\xa0te\xc2\xa0uwen\xc2\xa0gunste) (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) ([^,]*), ([^ ]*) (.*)" )
    res = pattern.findall( str )
    if len(res)==1:
        # no manual transaction
        ret['account number'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['address'] = res[0][3:5]
        ret['message'] = res[0][5]
        return ret

    # incoming international
    pattern = re.compile( "^Overschrijving\xc2\xa0te\xc2\xa0uwen\xc2\xa0gunste -- (\w\w\d+) (.*) Com:\xc2\xa0(.*)" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['account number'] = res[0][0]
        ret['payee'] = res[0][1]
        ret['message'] = res[0][2]
        return ret

    # Overschrijving te uwen gunste -- BBPIPTPL PT50 0010 0000 1943 9480 0011 3 JOHN DOE VOIDSTREET XXIII 117 3830 - 000 ILHAVO PORTUGAL PT Com: TEST MESSAGE Valutadatum: 01/01/1900
    pattern = re.compile( "^Overschrijving\xc2\xa0te\xc2\xa0uwen\xc2\xa0gunste -- (\w+) ([^ ]*) (.*) Com:\xc2\xa0(.*)" )
    res = pattern.findall( str )
    if len(res)==1:
        ret['bic'] = res[0][0]
        ret['iban'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['message'] = res[0][3]
        return ret

    return None
# ==============================================================================
# Dissect something like
# Bancontact 730-8661420-92 KBC BANK BERCHEM (01/01/00 10:00) Valutadatum: 01/01/1900
def bancontact( message ):

    ret = empty_transaction()

    # with payee
    pattern = re.compile( "^Bancontact (\d\d\d-\d\d\d\d\d\d\d-\d\d) (.*)\xc2\xa0" )
    results = pattern.findall( message )
    if len(results)==1:
        # bancontact found
        ret['account number'], ret['payee'] = results[0]
        return ret

    # w/o payee
    pattern = re.compile( "^Bancontact (\d\d\d-\d\d\d\d\d\d\d-\d\d)" )
    results = pattern.findall( message )
    if len(results)==1:
        # bancontact found
        ret['account number'] = results[0]
        return ret

    return None
# ==============================================================================
# Dissect something like
# Opladen Proton-kaart 012-1234567-89 Valutadatum: 01/01/1900
def proton( message ):

    ret = empty_transaction()

    pattern = re.compile( "^Opladen Proton-kaart 610-2011962-79" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['message'] = "Proton"
        return ret

    return None
# ==============================================================================
# Afrekening kaarten 012-0000000-83 Valutadatum: 01/01/1900
def cards_clearance( message ):
    ret = empty_transaction()

    pattern = re.compile( "^Afrekening\xc2\xa0kaarten 666-0000004-83$" )
    if len( pattern.findall( message ) ) > 0:
        ret['message'] = "Card clearance"
        return ret

    return None
# ==============================================================================
# Domiciliëring 000-0000000-00 LAMPS SA/NV DOM. : 012-3456789-01 MED. : E100316808                      REF. : 110/0316/80824 Valutadatum: 01/01/1900
def direct_debit( message ):
    ret = empty_transaction()

    pattern = re.compile( "^Domicili\xc3\xabring 000-0000000-00 (.*) DOM.\xc2\xa0:\xc2\xa0(\d\d\d-\d\d\d\d\d\d\d-\d\d)\xc2\xa0MED.\xc2\xa0:\xc2\xa0([\w\d]*).*REF.\xc2\xa0:\xc2\xa0(\d\d\d/\d\d\d\d/\d\d\d\d\d)$" )
    res = pattern.findall( message )
    if len(res)>0:
        ret['payee'], ret['account number'], ret['message'], ret['number'] = res[0]
        return ret
    else:
        return None
# ==============================================================================
# Dissect something like
# db Titanium Card Nr. 0123 5678 1234 5678 PAYDUDE LUL2240 Aanmaak uitgavenstaat: 01/01/1900  Boekingsdatum: 01/01/1900
def titanium( str ):
    ret = empty_transaction()

    # strip useless " Aanmaak uitgavenstaat: 22/02/2010  Boekingsdatum: 01/03/2010"
    str = re.sub( " Aanmaak\xc2\xa0uitgavenstaat:\xc2\xa0\d\d/\d\d/\d\d\d\d\xc2\xa0 Boekingsdatum:\xc2\xa0\d\d/\d\d/\d\d\d\d$", "", str )

    # get contents
    pattern = re.compile( "^db\xc2\xa0Titanium\xc2\xa0Card\xc2\xa0Nr.\xc2\xa05413\xc2\xa02754\xc2\xa09699\xc2\xa00902 (.*)" )
    res = pattern.findall( str )
    if len(res)==1:
        str = res[0]
    else:
        return None

    # check if it's a transaction in a foreign currency a la
    # "-22,50 GBP (Wisselkoers: 0,896) "
    pattern = re.compile( "(-?\d+),(\d\d)\xc2\xa0(\w+)\xc2\xa0\(Wisselkoers:\xc2\xa0(\d+),(\d+)\) (.*)" )
    res = pattern.findall( str )
    if len(res)==1:
        amount        = float(res[0][0])
        if amount < 0.0:
            amount -= float(res[0][1]) / 100.
        else:
            amount += float(res[0][1]) / 100.
        ret['amount'] = amount
        ret['currency'] = res[0][2]
        ret['exchange_rate'] = float(res[0][3]) + float(res[0][4]) / 100.
        ret['message'] = res[0][5]
    else:
        ret['message'] = str

    return ret
# ==============================================================================
# Dissect something like
# Uw doorlopende opdracht 012-3456789-12 John Doe 2018 Alabama STANDING ORDER 80174 Valutadatum: 01/01/1900
def standing_national( message ):
    ret = empty_transaction()

    # pattern *with address
    pattern = re.compile( "Uw\xc2\xa0doorlopende\xc2\xa0opdracht (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) ([^ ]*) STANDING ORDER (\d\d\d\d\d)$" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['account number'], ret['payee'], ret['address'], ret['number'] = results[0]
        return ret

    # pattern without address
    pattern = re.compile( "Uw\xc2\xa0doorlopende\xc2\xa0opdracht (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) STANDING ORDER (\d\d\d\d\d)$" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['account number'], ret['payee'], ret['number'] = results[0]
        return ret

    return None
# ==============================================================================
# Dissect something like
# Uw doorlopende opdracht -- RABONL2U NL29 RABO 0105 8855 09 JOHN DOE VOIDSTREET 130 1071 XW ALABAMA NL Valutadatum: 01/01/1900
def standing_international( message ):
    ret = empty_transaction()

    # pattern *with address
    pattern = re.compile( "^Uw\xc2\xa0doorlopende\xc2\xa0opdracht -- (\w\w\w\w\w\w\w\w)\xc2\xa0(\w\w\d\d\xc2\xa0\w\w\w\w\xc2\xa0\d\d\d\d\xc2\xa0\d\d\d\d\xc2\xa0\d*) (.*)$" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['bic'], ret['iban'], ret['payee'] = results[0]
        return ret

    return None
# ==============================================================================
# Bancontact Geldopvraging te: DENVER            Datum: 04/04/10 Valutadatum: 01/01/1900
# Bancontact Geldopvraging te: LONDON            Tegenwaarde:     50,00 GBP Koers: 1 EUR = 0,90220137 GBP Betalingsprovisie: 2,50 EUR Wisselprovisie:  0,83 EUR Datum: 01/01/00 Valutadatum: 01/01/1900
def foreign_atm( message ):
    ret = empty_transaction()

    # in the same currency:
    pattern = re.compile("^Bancontact Geldopvraging\xc2\xa0te:\xc2\xa0(\w*)(.*)")
    res = pattern.findall( message )
    if len(res)>0:
        ret['location'] = res[0][0]

        # check for foreign currency in the remainder
        pattern = re.compile( "Tegenwaarde:[\xc2\xa0]+(\d+),(\d\d)\xc2\xa0(\w+) Koers:\xc2\xa01\xc2\xa0EUR\xc2\xa0=\xc2\xa0(\d+),(\d+)\xc2\xa0\w+ Betalingsprovisie:\xc2\xa0(\d+),(\d+)\xc2\xa0\w+ Wisselprovisie:\xc2\xa0\xc2\xa0(\d+),(\d+)\xc2\xa0\w+ (.*)")
        res = pattern.findall( res[0][1] )
        if len(res)>0:
            ret['amount'] = float(res[0][0]) + float(res[0][1]) / 100.
            ret['currency'] = res[0][2]
            ret['exchange rate'] = float(res[0][3]) + float(res[0][4]) * 10**(-len(res[0][4]))
            ret['payment fee'] = float(res[0][5]) + float(res[0][6]) * 10**(-len(res[0][6]))
            ret['exchange fee'] = float(res[0][7]) + float(res[0][8]) * 10**(-len(res[0][8]))

        return ret
    else:
        return None
# ==============================================================================
# Intresten - kosten -- Valutadatum: 01/01/1900
def interest( message ):
    ret = empty_transaction()

    # in the same currency:
    pattern = re.compile("^Intresten\xc2\xa0-\xc2\xa0kosten --$")
    res = pattern.findall( message )

    if len(res)>0:
        return ret

    return None
# ==============================================================================