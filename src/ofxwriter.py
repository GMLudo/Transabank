#! /usr/bin/env python
# -*- coding: utf-8 -*-

import xml.dom.minidom
from xml.dom.minidom import Document
import time

# ==============================================================================
def create_ofx( entry ):

    # instantiate document
    doc = Document()

    stmtrs = doc.createElementNS( None , "STMTRS" )
    doc.appendChild(stmtrs)

    # add curdef
    currency_element = doc.createElementNS( None, "CURDEF" )
    stmtrs.appendChild(currency_element)
    c = doc.createTextNode("EUR")
    currency_element.appendChild(c)

    # bank account from
    bankacctfrom = doc.createElementNS( None, "BANKACCTFROM" )
    stmtrs.appendChild(bankacctfrom)

    # bank transfer list
    stmtrs.appendChild( create_ofx_banktranlist(entry) )

    # ledger balance
    ledgerbal = doc.createElementNS( None, "LEDGERBAL" )
    stmtrs.appendChild( ledgerbal )
    # amount
    balamt = doc.createElementNS( None, "BALAMT" )
    ledgerbal.appendChild(balamt)
    balamt.appendChild( doc.createTextNode("0.00") )
    # date as of
    dtasof = doc.createElementNS( None, "DTASOF" )
    ledgerbal.appendChild(dtasof)
    dtasof.appendChild( doc.createTextNode("01-01-2010") )


    import xml.dom.ext
    return xml.dom.ext.PrettyPrint(doc)
# ==============================================================================
def create_ofx_banktranlist( entry ):

    doc = xml.dom.minidom.Document()

    banktranlist = doc.createElementNS( None, "BANKTRANLIST" )

    # start date
    dtstart = doc.createElementNS( None, "DTSTART" )
    banktranlist.appendChild(dtstart)
    dtstart.appendChild( doc.createTextNode("01-01-1900") )

    # end date
    dtend = doc.createElementNS( None, "DTEND" )
    banktranlist.appendChild(dtend)
    dtend.appendChild( doc.createTextNode("01-01-2100") )

    # loop over the transactions
    banktranlist.appendChild( create_ofx_transaction( entry ) )

    return banktranlist
# ==============================================================================
def create_ofx_transaction( entry ):

    doc = xml.dom.minidom.Document()

    stmttrn = doc.createElementNS(None, "STMTTRN")

    # decide upon the transaction type
    trntype = doc.createElementNS(None, "TRNTYPE")
    stmttrn.appendChild( trntype )
    if entry['amount']>0:
        trntype.appendChild( doc.createTextNode("CREDIT") )
    else:
        trntype.appendChild( doc.createTextNode("DEBIT") )

    # date posted
    dtposted = doc.createElementNS(None, "DTPOSTED")
    stmttrn.appendChild( dtposted )
    dtposted.appendChild( doc.createTextNode( time.strftime('%Y-%m-%d', entry['date']) ) )

    # value date
    if  entry['value date'] is not None:
        dtavail = doc.createElementNS(None, "DTAVAIL")
        stmttrn.appendChild( dtavail )
        dtavail.appendChild( doc.createTextNode( time.strftime('%Y-%m-%d', entry['value date']) ) )

    # amount of transaction
    trnamt = doc.createElementNS(None, "TRNAMT")
    stmttrn.appendChild( trnamt )
    trnamt.appendChild( doc.createTextNode( "%.2f" % entry['amount'] ) )

    # unique ID
    fitid = doc.createElementNS(None, "FITID")
    stmttrn.appendChild( fitid )
    fitid.appendChild( doc.createTextNode( "abc" ) )

    # payee
    stmttrn.appendChild( create_ofx_payee(entry) )

    # bank account to
    stmttrn.appendChild( create_ofx_bankaccount(entry) )

    # memo
    memo = doc.createElementNS(None, "MEMO")
    stmttrn.appendChild( memo )
    memo.appendChild( doc.createTextNode( entry['message'] ) )

    if entry['currency'] is not None:
        currency = doc.createElementNS(None, "ORIGINALCURRENCY")
        stmttrn.appendChild( currency )
        currency.appendChild( doc.createTextNode( entry['currency'] ) )

    return stmttrn
# ==============================================================================
def create_ofx_payee( entry ):

    doc = xml.dom.minidom.Document()

    payee = doc.createElementNS(None, "PAYEE")

    # name
    name = doc.createElementNS(None, "NAME")
    payee.appendChild( name )
    if entry['payee'] is not None:
        name.appendChild( doc.createTextNode( entry['payee'] ) )

    # address 1
    addr1 = doc.createElementNS(None, "ADDR1")
    payee.appendChild( addr1 )
    if entry['address'] is not None:
        addr1.appendChild( doc.createTextNode( entry['address'] ) )

    # city
    city = doc.createElementNS(None, "CITY")
    payee.appendChild( city )
    city.appendChild( doc.createTextNode( "mycity" ) )

    # state (leave empty)
    state = doc.createElementNS( None, "STATE" )
    payee.appendChild( state )

    # postal code
    postalcode = doc.createElementNS( None, "POSTALCODE" )
    payee.appendChild( postalcode )
    postalcode.appendChild( doc.createTextNode( "1234" ) )

    # optional: country

    # phone
    phone = doc.createElementNS( None, "PHONE" )
    payee.appendChild( phone )

    return payee
# ==============================================================================
def create_ofx_bankaccount( entry ):

    doc = xml.dom.minidom.Document()

    tofrom = "BANKACCTTO"

    bankacct = doc.createElementNS( None, tofrom )

    if entry['account number'] is not None:
        bank_id_parser = re.compile( "(\d\d\d)-.*" )
        res = bank_id_parser.findall( entry['account number'] )
        bank_id    = res[0]
        account_id = entry['account number']
    elif entry['bic'] is not None and entry['iban'] is not None:
        bank_id    = entry['bic']
        account_id = entry['iban']
    else:
        bank_id    = ""
        account_id = ""

    # TODO: extract first three items off of account number
    # bank ID
    bankid = doc.createElementNS( None, "BANKID" )
    bankacct.appendChild( bankid )
    bankid.appendChild( doc.createTextNode( bank_id ) )

    # account ID
    acctid = doc.createElementNS( None, "ACCTID" )
    bankacct.appendChild( acctid )
    acctid.appendChild( doc.createTextNode( account_id ) )

    # account type;
    # one of CHECKING, SAVINGS, MONEYMRKT, CREDITLINE
    accttype = doc.createElementNS( None, "ACCTTYPE" )
    bankacct.appendChild( accttype )
    accttype.appendChild( doc.createTextNode( "CHECKING" ) )

    return bankacct
# ==============================================================================