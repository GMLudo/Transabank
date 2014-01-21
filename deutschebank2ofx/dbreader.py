#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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
import logging
from pprint import pprint
import datetime # for handling date strings
import re
import unicodecsv
# ==============================================================================
# Read a CSV file and return parsed lists of transaction of the regular account
# and transactions of the MasterCard account.

LOGGER = logging.getLogger(__name__)

def read_db_csvfile( file_name, delim = "|" ):

    # read the file
    db_reader = unicodecsv.reader( open(file_name), delimiter=delim.encode('utf-8'), encoding='cp1252')

    transactions = []
    mc_transactions = []
    for row in db_reader:
        LOGGER.debug("row: %r", row)
        # skip empty rows
        if not row:
            continue
        if row[1].startswith("D\xe9compte\xa0des\xa0d\xe9penses:\xa0carte\xa0de\xa0cr\xe9dit "):
            LOGGER.debug('"Décompte\xa0des\xa0dépenses" line dropped.')
        else:
            transaction, is_mastercard_transaction = _process_db_csv_entry( row )
            if is_mastercard_transaction:
                mc_transactions.append( _clean_transaction(transaction) )
                #LOGGER.debug("mastercard transaction: %r", transaction)
            else:
                transactions.append( _clean_transaction(transaction) )
                #LOGGER.debug("transaction: %r", transaction)
            #pprint(transaction)

    return transactions, mc_transactions
# ==============================================================================
def _clean_transaction(obj):
    if isinstance(obj, basestring):
        return obj.strip().replace('\xa0', ' ')
    elif isinstance(obj, list):
        return [_clean_transaction(o) for o in obj]
    elif isinstance(obj, tuple):
        return tuple(_clean_transaction(o) for o in obj)
    elif isinstance(obj, dict):
        return dict((k, _clean_transaction(v)) for (k,v) in obj.items())
    else:
        return obj
# ==============================================================================
def _process_db_csv_entry( row ):

    # Decode the columns.
    # This is DB Belgi\"e-specific.
    raw_date, message, account_amount, mastercard_amount, currency = row

    # get date
    date = _get_formatted_date( raw_date )

    # Get 'amount'.
    is_mastercard_transaction = False
    if account_amount != "" and mastercard_amount == "":
        # account transaction
        amount = _get_amount( account_amount )
    elif account_amount == "" and mastercard_amount != "":
        # mastercard transaction
        amount = _get_amount( mastercard_amount )
        is_mastercard_transaction = True
    else:
        raise Exception, "Error."

    # parse message body
    transaction = _process_message_body( message, is_mastercard_transaction )

    # merge the common entries into it
    transaction['date']   = date
    transaction['amount'] = amount

    return transaction, is_mastercard_transaction
# ==============================================================================
def _process_message_body( message, is_mastercard_transaction ):
    # extract the value date ("Valutadatum")
    print("="*50)
    print(message)
    message, value_date = _extract_value_date( message )

    # strip "(18/04/09 14:09)"
    message = re.sub( "\(\d\d/\d\d/\d\d\xa0\d\d:\d\d\)", "", message )

    if is_mastercard_transaction:
        # handle mastercard transaction
        transaction = _titanium( message )
    else:
        # handle regular transaction
        if _cash_withdrawal( message ) is not None:
            transaction = _cash_withdrawal( message )
        elif _repayment( message ) is not None:
            transaction = _repayment( message )
        elif _foreign_exchanges( message ) is not None:
            transaction = _foreign_exchanges( message )
        elif _clearance( message ) is not None:
            transaction = _clearance( message )
        elif _proton(message) is not None:
            transaction = _proton( message )
        elif _interest(message) is not None:
            transaction = _interest( message )
        elif _outgoing_national( message ) is not None:
            transaction = _outgoing_national( message )
        elif _standing_national( message ) is not None:
            transaction = _standing_national( message )
        elif _bancontact( message ) is not None:
            transaction = _bancontact( message )
        elif _atm_international( message ) is not None:
            transaction = _atm_international( message )
        elif _standing_international( message ) is not None:
            transaction = _standing_international( message )
        elif _outgoing_international( message ) is not None:
            transaction = _outgoing_international( message )
        elif _incoming_transaction( message ) is not None:
            transaction = _incoming_transaction( message )
        elif _cards_clearance( message ) is not None:
            transaction = _cards_clearance( message )
        elif _direct_debit( message ) is not None:
            transaction = _direct_debit( message )
        elif _refund( message ) is not None:
            transaction = _refund( message )
        elif _withdrawal( message ) is not None:
            transaction = _withdrawal( message )
        elif _currency_import( message ) is not None:
            transaction = _currency_import( message )
        elif _check( message ) is not None:
            transaction = _check( message )
        elif _transfer_cancelled( message ) is not None:
            transaction = _transfer_cancelled( message )

        else:
            transaction = None
            raise ValueError( "Could not decode entry \""
                              + message +"\"."
                            )

    transaction['value date'] = value_date

    return transaction
# ==============================================================================
def _get_formatted_date( raw_date ):
    # Decode 'date'.
    # DB has either long (2010) or short (10) year value, changing seemingly
    # randomly.
    try:
        date = datetime.datetime.strptime( raw_date, "%d/%m/%y" ).date()
    except:
        date = datetime.datetime.strptime( raw_date, "%d/%m/%Y" ).date()

    return date
# ==============================================================================
# gets a float value of a string such as "1.000,32" (=1000.32)
def _get_amount( raw_amount ):
    # remove the thousand-delimiter and replace the decimal "," by
    # by a decimal "."
    amount = raw_amount.replace(".","").replace(",",".")
    return float( amount )
# ==============================================================================
def _extract_value_date( message ):

    # get value date
    valuta_pattern = re.compile( ".* (Valutadatum|Date\xa0valeur):\xa0(\d\d/\d\d/\d\d\d\d).*" )
    valdate = valuta_pattern.findall( message )

    if len(valdate) > 0:
        value_date = datetime.datetime.strptime( valdate[0][1], "%d/%m/%Y" ).date()
    else:
        value_date = None

    # strip "Valutadatum: xx/xx/xxxx"
    message = re.sub( " (Valutadatum|Date\xa0valeur):\xa0\d\d/\d\d/\d\d\d\d", "", message )

    return message, value_date
# ==============================================================================
def _empty_transaction():
    return { 'date': None,
             'amount': None,
             'account number': None,
             'bic': None,
             'iban': None,
             'payee': None,
             'address': None,
             'city': None,
             'postal code': None,
             'country': None,
             'message': None,
             'number': None,
             'mode': None,
             'foreign amount': None,
             'currency': None,
             'exchange rate': None,
             'location': None,
             'exchange fee': None,
             'payment fee': None,
             'value date': None,
             'phone number': None
           }
# ==============================================================================
# Dissect something like
# Uw overschrijving 410-0659001-06 John Doe Voidstreet 5, 2610 Alabama 080/0163/21631 Valutadatum: 01/01/1900
def _outgoing_national( message ):

    ret = _empty_transaction()

    ret['mode'] = 'Transfer (national)'

    # match account number and address, e.g.,
    # "410-0659001-06 Onafhankelijkxc2\xa0Ziekenfonds Boomsesteenwgxc2\xa05, 2610xc2\xa0Antwerpen"
    pattern = re.compile( "^(Uw\xa0overschrijving|Votre\xa0virement) (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) ([^,]*), (\d\d\d\d) (\w*) (.*)" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['account number'] = res[0][0]
        ret['payee']      = res[0][1]
        ret['address']    = res[0][2]
        ret['postal code'] = res[0][3]
        ret['city'] = res[0][4]
        ret['message']    = res[0][5]
        return ret

    # without address, e.g.
    # "Uw overschrijving 310-1610249-38 Doe Inc. 1342235809 Valutadatum: 01/01/1900"
    pattern = re.compile( "^(Uw\xa0overschrijving|Votre\xa0virement) (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) (\d+).*" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['account number'] = res[0][0]
        ret['payee']      = res[0][1]
        ret['message']    = res[0][2]
        return ret

    return None
# ==============================================================================
# Dissect something like
# Uw overschrijving -- RABONL2UXXX NL29 RABO 0105 8855 09 John Doe Voidstreet 130 1071 XW Amsterdam NL Com: this is some communication Valutadatum: 01/01/1900
def _outgoing_international( message ):

    ret = _empty_transaction()

    # cut "Com: .*"
    comm_pattern = re.compile( ".* Com:\xa0(.*)$" )
    res = comm_pattern.findall( message )
    if len(res)==1:
        ret['message'] = res[0]
        message = re.sub(  " Com:\xa0.*$", "", message )

    # match account number and address, e.g.
    # "410-0659001-06 Johnxc2\xa0Doe Voidstreetxc2\xa05, 2610xc2\xa0Alabama"
    pattern = re.compile( "^(Uw\xa0overschrijving|Votre\xa0virement) -- ([^ ]*) (\w\w\d\d\xa0\w\w\w\w\xa0\d\d\d\d\xa0\d\d\d\d\xa0\d*)\xa0(.*)" )
    res = pattern.findall( message )
    if len(res)==1:
        ret['bic'] = res[0][1]
        ret['iban'] = res[0][2]
        ret['payee'] = res[0][3]
        ret['mode'] = 'Transfer (EU)'
        return ret

    # "Uw overschrijving -- BE80777591050277 Distr. Alabama -- Finances Voidstreet 22 Bus 111 2600 Alabama US Com: +++001/0028/72387+++"
    pattern = re.compile( "^(Uw\xa0overschrijving|Votre\xa0virement) -- (\w\w\d+) ([^ ]*) (\d+)\xa0(\w+)\xa0(\w+)$" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['account number'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['postal code'] = res[0][3]
        ret['city'] = res[0][4]
        ret['country'] = res[0][5]
        ret['mode'] = 'Transfer (international)'
        return ret

    # "Uw overschrijving -- BE80777591050277 Distr. Alabama -- Finances Voidstreet 22 Bus 111 2600 Alabama US Com: +++001/0028/72387+++"
    pattern = re.compile( "^(Uw\xa0overschrijving|Votre\xa0virement) -- (\w\w\d+) ([^ ]*) (.*)$" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['account number'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['address'] = res[0][3]
        ret['mode'] = 'Transfer (international)'
        return ret

    # "Uw overschrijving -- BE42091010100254 ZNA - - BE Com: +++510/9515/61064+++ Valutadatum: 01/01/1900"
    pattern = re.compile( "^(Uw\xa0overschrijving|Votre\xa0virement) -- (\w\w\d+) ([^ ]*).*$" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['account number'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['mode'] = 'Transfer (international)'
        return ret

    # "Uw overschrijving -- BE42091010100254 ZNA - - BE Com: +++510/9515/61064+++ Valutadatum: 01/01/1900"
    pattern = re.compile( "^(Uw\xa0overschrijving|Votre\xa0virement) -- (\w\w\d+) ([^ ]*).*$" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['account number'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['mode'] = 'Transfer (international)'
        return ret

    pattern = re.compile( "^Overschrijving\xa0naar\xa0het\xa0buitenland --$" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['mode'] = 'Transfer (international)'
        return ret

    return None
# ==============================================================================
# Dissect something like
# Overschrijving te uwen gunste 424-5530811-85 GBA VOIDSTREET 5, 1000 BRUSSEL /A/ WERKGEVER: 0123456 WERKNEMER: 0123456 001 DATUM: 01/01/1900 Valutadatum: 01/01/1900
def _incoming_transaction( message ):

    ret = _empty_transaction()

    # incoming national
    pattern = re.compile( "^(Overschrijving\xa0te\xa0uwen\xa0gunste|Virement\xa0en\xa0votre\xa0faveur) (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) ([^,]*), ([^ ]*) (.*)" )
    res = pattern.findall( message )
    if len(res) == 1:
        # no manual transaction
        ret['account number'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['address'] = res[0][3:5]
        ret['message'] = res[0][5]
        return ret

    # incoming international
    # Overschrijving\xa0te\xa0uwen\xa0gunste -- BE08737000540213 CAP\xa0MARIANNE\xa0CUPERUSSTRAAT\xa034\xa02018 ANTWERPEN\xa0BE Com:\xa0INTERNET
    split_message = message.split(' ')
    pattern = re.compile( "^(Overschrijving\xa0te\xa0uwen\xa0gunste|Virement\xa0en\xa0votre\xa0faveur) -- (\w\w\d+) ([^ ]*\d\d\d\d \w+\xa0\w\w) Com:\xa0(.*)" )
    res = pattern.findall( message )
    if len(res) == 1:
        ret['account number'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['message'] = res[0][3]
        return ret

    # Overschrijving te uwen gunste -- BBPIPTPL PT50 0010 0000 1943 9480 0011 3 JOHN DOE VOIDSTREET XXIII 117 3830 - 000 ILHAVO PORTUGAL PT Com: TEST MESSAGE Valutadatum: 01/01/1900
    pattern = re.compile( "^(Overschrijving\xa0te\xa0uwen\xa0gunste|Virement\xa0en\xa0votre\xa0faveur) -- (\w+) ([^ ]*) (.*) Com:\xa0(.*)" )
    res = pattern.findall( message )
    if len(res)==1:
        ret['bic'] = res[0][1]
        ret['iban'] = res[0][2]
        ret['payee'] = res[0][3]
        ret['message'] = res[0][4]
        return ret

    pattern = re.compile( "^(Overschrijving\xa0te\xa0uwen\xa0gunste|Virement\xa0en\xa0votre\xa0faveur) -- ([^ ]*) (.*) Com:\xa0(.*)" )
    res = pattern.findall( message )
    if len(res)==1:
        ret['iban'] = res[0][1]
        ret['payee'] = res[0][2]
        ret['message'] = res[0][3]
        return ret

    return None
# ==============================================================================
# Dissect something like
# Bancontact 730-8661420-92 KBC BANK BERCHEM (01/01/00 10:00) Valutadatum: 01/01/1900
def _bancontact( message ):

    ret = _empty_transaction()

    ret['mode'] = 'Bancontact'

    # with payee
    pattern = re.compile( "^Bancontact (\d\d\d-\d\d\d\d\d\d\d-\d\d) (.*)\xa0" )
    results = pattern.findall( message )
    if len(results)==1:
        # _bancontact found
        ret['account number'], ret['payee'] = results[0]
        return ret

    # w/o payee
    pattern = re.compile( "^Bancontact (\d\d\d-\d\d\d\d\d\d\d-\d\d)" )
    results = pattern.findall( message )
    if len(results)==1:
        # _bancontact found
        ret['account number'] = results[0]
        return ret

    return None
# ==============================================================================
# Opneming van contanten --
def _withdrawal( message ):
    ret = _empty_transaction()

    pattern = re.compile("^Opneming\xa0van\xa0contanten --$")
    res = pattern.findall( message )

    if len(res) > 0:
        ret[ 'mode' ] = 'Withdrawal'
        return ret

    return None
# ==============================================================================
# "Uw verkoop vreemde bankbiljetten --"
def _currency_import( message ):
    ret = _empty_transaction()

    pattern = re.compile("^Uw\xa0verkoop\xa0vreemde\xa0bankbiljetten --$")
    res = pattern.findall( message )

    if len(res) > 0:
        ret[ 'mode' ] = 'Currency import'
        return ret

    return None
# ==============================================================================
# "Afgifte cheque onder gewoon voorbehoud -- 1 CHEQUE(S)"
def _check( message ):
    ret = _empty_transaction()

    pattern = re.compile("^Afgifte\xa0cheque\xa0onder\xa0gewoon\xa0voorbehoud -- 1\xa0CHEQUE\(S\)$")
    res = pattern.findall( message )

    if len(res) > 0:
        ret[ 'mode' ] = 'Check'
        return ret

    return None
# ==============================================================================
# Dissect something like
# Diverse�verrichtingen -- TERUGBETALING
def _repayment( message ):

    ret = _empty_transaction()

    pattern = re.compile( "^Diverse\xa0verrichtingen -- TERUGBETALING" )
    results = pattern.findall( message )
    if len(results)==1:
        ret[ 'mode' ] = "Repayment"
        return ret

    return None
# ==============================================================================
# Dissect something like
# Uw�verkoop�vreemde�bankbiljetten -- Valutadatum:�20/09/2010
def _foreign_exchanges( message ):

    ret = _empty_transaction()

    pattern = re.compile( "^Uw\xa0verkoop\xa0vreemde\xa0bankbiljetten --" )
    results = pattern.findall( message )
    if len(results)==1:
        ret[ 'mode' ] = "Foreign exchanges"
        return ret

    return None
# ==============================================================================
# Dissect something like
# Afrekening�kaarten 666-0000004-83 Valutadatum:�01/03/2010
def _clearance( message ):

    ret = _empty_transaction()

    pattern = re.compile( "^Afrekening\xa0kaarten \d\d\d-\d\d\d\d\d\d\d-\d\d" )
    results = pattern.findall( message )
    if len(results)==1:
        ret[ 'mode' ] = "Cards clearance"
        return ret

    return None
# ==============================================================================
# Dissect something like
# Opneming�van�contanten -- Valutadatum:�20/09/2010
def _cash_withdrawal( message ):

    ret = _empty_transaction()

    pattern = re.compile( "^Opneming\xa0van\xa0contanten" )
    results = pattern.findall( message )
    if len(results) == 1:
        ret[ 'mode' ] = "Cash withdrawal"
        return ret

    return None
# ==============================================================================
# Dissect something like
# Opladen Proton-kaart 012-1234567-89 Valutadatum: 01/01/1900
def _proton( message ):

    ret = _empty_transaction()

    pattern = re.compile( "^Opladen\xa0Proton-kaart \d\d\d-\d\d\d\d\d\d\d-\d\d" )
    results = pattern.findall( message )
    if len(results)==1:
        ret[ 'mode' ] = "Proton"
        return ret

    return None
# ==============================================================================
# Dissect something like
# Opladen Proton-kaart 012-1234567-89 Valutadatum: 01/01/1900
def _proton( message ):

    ret = _empty_transaction()

    pattern = re.compile( "^Opladen\xa0Proton-kaart \d\d\d-\d\d\d\d\d\d\d-\d\d" )
    results = pattern.findall( message )
    if len(results)==1:
        ret[ 'mode' ] = "Proton"
        return ret

    return None
# ==============================================================================
# Afrekening kaarten 012-0000000-83 Valutadatum: 01/01/1900
def _cards_clearance( message ):
    ret = _empty_transaction()

    pattern = re.compile( "^Afrekening\xa0kaarten \d\d\d-\d\d\d\d\d\d\d-\d\d$" )
    if len( pattern.findall( message ) ) > 0:
        ret['mode'] = "Card clearance"
        return ret

    return None
# ==============================================================================
# Domicili"ering 000-0000000-00 LAMPS SA/NV DOM. : 012-3456789-01 MED. : E100316808                      REF. : 110/0316/80824 Valutadatum: 01/01/1900
def _direct_debit( message ):
    ret = _empty_transaction()

    pattern = re.compile( "^(Domicili\xebring|Domiciliation) 000-0000000-00 (.*) DOM.\xa0:\xa0(\d\d\d-\d\d\d\d\d\d\d-\d\d)\xa0MED.\xa0:\xa0([\w\d]*).*REF.\xa0:\xa0(\d\d\d/\d\d\d\d/\d\d\d\d\d)$" )
    res = pattern.findall( message )
    if len(res)>0:
        ret['payee'], ret['account number'] = res[0][1:3]
        if res[0][3] != '':
            ret['message'] = res[0][3]
        ret['number'] = res[0][4]
        ret['mode'] = 'Direct debit'
        return ret
    else:
        pattern = re.compile( "^(Domicili\xebring|Domiciliation) -- (BE\d\d\xa0\d\d\d\xa0\d\d\d\d\d\d\d\xa0\d\d)\xa0(.*) Ref:\xa0.*$" )
        res = pattern.findall( message )
        print(res)
        if len(res)>0:
            ret['account number'], ret['payee']  = res[0][1:3]
            ret['mode'] = 'Direct debit'
            return ret
        else:
            return None
# ==============================================================================
# Dissect something like
# db Titanium Card Nr. 0123 5678 1234 5678 PAYDUDE LUL2240 Aanmaak uitgavenstaat: 01/01/1900  Boekingsdatum: 01/01/1900
def _titanium( message ):
    ret = _empty_transaction()

    ret[ 'mode' ] = 'Credit card'

    # strip useless " Aanmaak uitgavenstaat: 22/02/2010  Boekingsdatum: 01/03/2010"
    message = re.sub( " (Aanmaak\xa0uitgavenstaat|Création\xa0état\xa0des\xa0dépenses):\xa0\d\d/\d\d/\d\d\d\d\xa0 (Boekingsdatum|Date\xa0de\xa0comptabilisation):\xa0\d\d/\d\d/\d\d\d\d$",
                      "",
                      message
                    )

    # get contents
    pattern = re.compile( "^db\xa0Titanium\xa0Card\xa0N[ro].\xa0\d\d\d\d\xa0\d\d\d\d\xa0\d\d\d\d\xa0\d\d\d\d (.*)" )

    res = pattern.findall( message )
    if len(res) == 1:
        message = res[0]
    else:
        raise ValueError( "Is not a MasterCard transaction." )

    # _check if it's a transaction in a foreign currency a la
    # "-22,50 GBP (Wisselkoers: 0,896) "
    pattern = re.compile( "(-?\d+),(\d\d)\xa0(\w+)\xa0\(Wisselkoers:\xa0(\d+),(\d+)\) (.*)" )
    res = pattern.findall( message )
    if len(res)==1:
        amount        = float(res[0][0])
        if amount < 0.0:
            amount -= float(res[0][1]) / 100.
        else:
            amount += float(res[0][1]) / 100.
        ret[ 'amount' ] = amount
        ret[ 'currency' ] = res[0][2]
        ret[ 'exchange_rate' ] = float(res[0][3]) + float(res[0][4]) / 100.
        payee_message = res[0][5]
    else:
        payee_message = message

    # Deutsche Bank Belgi\"e's uses a fixed format for the MasterCard transaction record:
    # columns    content
    # 1-25       digits for payee
    # 26-38      city OR reference number
    # 38-39      country code
    # 39ff.      postal code

    # first get rid of the non-breakable spaces and other weird symbols
    payee_message = payee_message.replace( "\xa0", " " )
    payee_message = payee_message.replace( "\xa3", " " )
    payee_message = payee_message.replace( "\xa7", " " )

    # payee with trimmed whitespace
    ret['payee'] = payee_message[0:25].strip()
    payee_message[25:37]
    if payee_message[25].isdigit():
        ret['phone number'] = payee_message[25:37].strip()
    else:
        ret['city'] = payee_message[25:37].strip()

    ret['country'] = payee_message[38:40]
    pcode = payee_message[40:]
    if pcode != "N/A":
        ret['postal code'] = payee_message[40:]

    return ret
# ==============================================================================
# Dissect something like
# Uw doorlopende opdracht 012-3456789-12 John Doe 2018 Alabama STANDING ORDER 80174 Valutadatum: 01/01/1900
def _standing_national( message ):
    ret = _empty_transaction()

    # pattern *with address
    pattern = re.compile( "(Uw\xa0doorlopende\xa0opdracht|Votre\xa0ordre\xa0permanent) (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) ([^ ]*) STANDING ORDER (\d\d\d\d\d)$" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['account number'], ret['payee'], ret['address'], ret['number'] = results[0][1:]
        return ret

    # pattern without address
    pattern = re.compile( "(Uw\xa0doorlopende\xa0opdracht|Votre\xa0ordre\xa0permanent) (\d\d\d-\d\d\d\d\d\d\d-\d\d) ([^ ]*) STANDING ORDER (\d\d\d\d\d)$" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['account number'], ret['payee'], ret['number'] = results[0][1:]
        return ret

    return None
# ==============================================================================
# Dissect something like
# Uw doorlopende opdracht -- RABONL2U NL29 RABO 0105 8855 09 JOHN DOE VOIDSTREET 130 1071 XW ALABAMA NL Valutadatum: 01/01/1900
def _standing_international( message ):
    ret = _empty_transaction()

    # cut "Com: .*"
    comm_pattern = re.compile( ".* Com:\xa0(.*)$" )
    res = comm_pattern.findall( message )
    if len(res)==1:
        ret['message'] = res[0]
        message = re.sub(  " Com:\xa0.*$", "", message )

    # pattern *with address
    pattern = re.compile( "^(Uw\xa0doorlopende\xa0opdracht|Votre\xa0ordre\xa0permanent) -- (\w\w\w\w\w\w\w\w)\xa0(\w\w\d\d\xa0\w\w\w\w\xa0\d\d\d\d\xa0\d\d\d\d\xa0\d*) (.*)$" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['mode'] = 'Standing order'
        ret['bic'], ret['iban'], ret['payee'] = results[0][1:]
        return ret

    # pattern *without bic
    pattern = re.compile( "^(Uw\xa0doorlopende\xa0opdracht|Votre\xa0ordre\xa0permanent) -- (\w\w\d\d\xa0[\xa0\d]*)\xa0(.*)$" )
    results = pattern.findall( message )
    if len(results)==1:
        ret['mode'] = 'Standing order'
        ret['iban'], ret['payee'] = results[0][1:]
        return ret

    return None
# ==============================================================================
# Bancontact Geldopvraging te: DENVER            Datum: 04/04/10 Valutadatum: 01/01/1900
# Bancontact Geldopvraging te: LONDON            Tegenwaarde:     50,00 GBP Koers: 1 EUR = 0,90220137 GBP Betalingsprovisie: 2,50 EUR Wisselprovisie:  0,83 EUR Datum: 01/01/00 Valutadatum: 01/01/1900
def _atm_international( message ):
    ret = _empty_transaction()

    ret['mode'] = 'ATM (international)'

    # Split the message by spaces (not \xa0's and the like).
    split_message = message.split( " " )

    pattern = re.compile("^(Geldopvraging\xa0te|Retrait\xa0d'argent\xa0\xe0):\xa0(.*)")
    res = pattern.findall( split_message[1] )

    if split_message[0] == "Bancontact" and len(res) > 0:
        # 'Bancontact', location, date information present
        ret['location'] = res[0][1].replace('\xa0'," ").strip()

        if len(split_message) >= 6: # foreign currency information present
            # Get value.
            pattern = re.compile( "Tegenwaarde:[\xa0]+(\d+),(\d\d)\xa0(\w+)")
            res = pattern.findall( split_message[2] )
            if len(res) > 0:
                ret['foreign amount'] = float(res[0][0]) + float(res[0][1]) / 100.
                ret['currency'] = res[0][2]

            # Get exchange rate.
            pattern = re.compile( "Koers:\xa01\xa0EUR\xa0=\xa0+(\d+),(\d+)\xa0\w+")
            res = pattern.findall( split_message[3] )
            if len(res) > 0:
                ret['exchange rate'] = float(res[0][0]) + float(res[0][1]) * 10**(-len(res[0][1]))

            # Get payment fee.
            pattern = re.compile( "Betalingsprovisie:\xa0(\d+),(\d+)\xa0\w+")
            res = pattern.findall( split_message[4] )
            if len(res) > 0:
                ret['payment fee'] = float(res[0][0]) + float(res[0][1]) * 10**(-len(res[0][1]))

            # Get exchange fee.
            pattern = re.compile( "Wisselprovisie:\xa0\xa0(\d+),(\d+)\xa0\w+")
            res = pattern.findall( split_message[5] )
            if len(res) > 0:
                ret['exchange fee'] = float(res[0][0]) + float(res[0][1]) * 10**(-len(res[0][1]))

        return ret
    else:
        return None
# ==============================================================================
# Intresten - kosten -- Valutadatum: 01/01/1900
def _interest( message ):
    ret = _empty_transaction()

    # in the same currency:
    pattern = re.compile("^(Intresten\xa0-\xa0kosten|Int\xe9r\xeats\xa0-\xa0Frais) --$")
    res = pattern.findall( message )

    if len(res)>0:
        ret['mode'] = 'Interest -- fees'
        return ret

    return None
# ==============================================================================
# Diverse verrichtingen -- TERUGBETALING
def _refund( message ):
    ret = _empty_transaction()

    pattern = re.compile("^Diverse\xa0verrichtingen -- TERUGBETALING$")
    res = pattern.findall( message )

    if len(res) > 0:
        ret[ 'mode' ] = 'Miscellaneous'
        return ret

    return None
# ==============================================================================
# Diverse verrichtingen -- TERUGBETALING
def _transfer_cancelled( message ):
    ret = _empty_transaction()

    # cut "Com: .*"
    comm_pattern = re.compile( ".* Com:\xa0(.*)$" )
    res = comm_pattern.findall( message )
    if len(res)==1:
        ret['message'] = res[0]
        message = re.sub(  " Com:\xa0.*$", "", message )

    pattern = re.compile( "^(Annulation\xa0virement) -- ([^ ]*) (\w\w\d\d\xa0\w\w\w\w\xa0\d\d\d\d\xa0\d\d\d\d\xa0\d*)\xa0(.*)" )
    res = pattern.findall( message )
    if len(res)==1:
        ret['bic'] = res[0][1]
        ret['iban'] = res[0][2]
        ret['payee'] = res[0][3]
        ret[ 'mode' ] = 'cancelled transfer'
        return ret

    pattern = re.compile( "^Transfert\xa0entre\xa0vos\xa0comptes\xa0Deutsche\xa0Bank --" )
    res = pattern.findall( message )
    if len(res)==1:
        ret[ 'mode' ] = 'internal transfer'
        return ret

    return None
