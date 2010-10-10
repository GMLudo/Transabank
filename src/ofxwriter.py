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
import xml.dom.minidom
from xml.dom.minidom import Document
import datetime
import re
# ==============================================================================
def print_ofx( entries ):

    # instantiate document
    doc = Document()

    stmtrs = doc.createElementNS( None , "STMTRS" )
    doc.appendChild(stmtrs)

    # add curdef
    currency_element = doc.createElementNS( None, "CURDEF" )
    stmtrs.appendChild(currency_element)
    c = doc.createTextNode( "EUR" )
    currency_element.appendChild( c )

    # bank account from
    bankacctfrom = doc.createElementNS( None, "BANKACCTFROM" )
    stmtrs.appendChild(bankacctfrom)

    # add the transaction list
    stmtrs.appendChild( create_ofx_banktranlist(entries) )

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
    dtasof.appendChild( doc.createTextNode(
                            datetime.date.today().isoformat()
                        )
                      )

    # install pyxml for this
    import xml.dom.ext
    return xml.dom.ext.PrettyPrint( doc )
# ==============================================================================
def create_ofx_banktranlist( entries ):

    doc = xml.dom.minidom.Document()

    banktranlist = doc.createElementNS( None, "BANKTRANLIST" )

    # start date
    dtstart = doc.createElementNS( None, "DTSTART" )
    banktranlist.appendChild(dtstart)
    dtstart.appendChild( doc.createTextNode("01-01-1900") )

    # end date
    dtend = doc.createElementNS( None, "DTEND" )
    banktranlist.appendChild(dtend)
    dtend.appendChild( doc.createTextNode( datetime.date.today().isoformat() ) )

    # loop over the transactions
    for entry in entries:
        banktranlist.appendChild( create_ofx_transaction( entry ) )

    return banktranlist
# ==============================================================================
def create_ofx_transaction( entry ):

    doc = xml.dom.minidom.Document()

    stmttrn = doc.createElementNS(None, "STMTTRN")

    # decide upon the transaction type
    trntype = doc.createElementNS(None, "TRNTYPE")
    stmttrn.appendChild( trntype )
    if entry['amount'] > 0:
        trntype.appendChild( doc.createTextNode("CREDIT") )
    else:
        trntype.appendChild( doc.createTextNode("DEBIT") )

    # date posted
    dtposted = doc.createElementNS(None, "DTPOSTED")
    stmttrn.appendChild( dtposted )
    dtposted.appendChild( doc.createTextNode(
                              entry['date'].strftime('%Y-%m-%d')
                          )
                        )

    # value date
    if entry['value date'] is not None:
        dtavail = doc.createElementNS(None, "DTAVAIL")
        stmttrn.appendChild( dtavail )
        dtavail.appendChild( doc.createTextNode(
                                 entry['value date'].strftime('%Y-%m-%d')
                             )
                           )

    # amount of transaction
    trnamt = doc.createElementNS(None, "TRNAMT")
    stmttrn.appendChild( trnamt )
    trnamt.appendChild( doc.createTextNode( "%.2f" % entry['amount'] ) )

    # unique ID
    fitid = doc.createElementNS(None, "FITID")
    stmttrn.appendChild( fitid )
    # for now, create the ID of date, %y%m%d, plus the amount
    fitid.appendChild( doc.createTextNode(
                           entry['value date'].strftime('%y%m%d')
                           + "%d" % (abs(entry['amount'])*100)
                       )
                     )

    # payee
    stmttrn.appendChild( create_ofx_payee(entry) )

    # bank account to
    stmttrn.appendChild( create_ofx_bankaccount(entry) )

    # memo
    if entry['message'] is not None:
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
    addr1 = doc.createElementNS( None, "ADDR1" )
    payee.appendChild( addr1 )
    if entry['address'] is not None:
        if type(entry['address']) == str:
            addr1.appendChild( doc.createTextNode( entry['address'] ) )
        elif type(entry['address']) == tuple:
            for addline in entry['address']:
                addr1.appendChild( doc.createTextNode( addline ) )
        else:
            raise ValueError( "Illegal address field, \""
                              + entry['address'] + "\"."
                            )

    # city
    city = doc.createElementNS(None, "CITY")
    payee.appendChild( city )
    if entry['city'] is not None:
        city.appendChild( doc.createTextNode( entry['city'] ) )

    # state (leave empty)
    state = doc.createElementNS( None, "STATE" )
    payee.appendChild( state )

    # postal code
    postalcode = doc.createElementNS( None, "POSTALCODE" )
    payee.appendChild( postalcode )
    if entry['postal code'] is not None:
        postalcode.appendChild( doc.createTextNode( entry['postal code'] ) )

    # optional: country

    # phone
    phone = doc.createElementNS( None, "PHONE" )
    payee.appendChild( phone )
    if entry['phone number'] is not None:
        postalcode.appendChild( doc.createTextNode( entry['phone number'] ) )

    return payee
# ==============================================================================
def create_ofx_bankaccount( entry ):

    doc = xml.dom.minidom.Document()

    tofrom = "BANKACCTTO"

    bankacct = doc.createElementNS( None, tofrom )

    if entry['account number'] is not None:
        bank_id_parser = re.compile( "(\d\d\d)-.*" )
        res = bank_id_parser.findall( entry['account number'] )
        if len(res)>0:
            bank_id    = res[0]
            account_id = entry['account number']
        else:
            bank_id    = ""
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