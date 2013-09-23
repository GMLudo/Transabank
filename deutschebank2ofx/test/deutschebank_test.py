#!/usr/bin/env python
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
import datetime
import unittest
# ==============================================================================
class TestDeutscheBankReader( unittest.TestCase ):

    # --------------------------------------------------------------------------
    def test_outgoing_national(self):
        message = 'Uw\xc2\xa0overschrijving 410-0659001-06 John\xc2\xa0Doe Voidstreet\xc2\xa05, 2610\xc2\xa0Alabama 080/0163/21631 Valutadatum: 01/01/1922'
        transaction = dbreader.process_message_body( message, False )
        self.assertEqual( transaction['account number'], '410-0659001-06' )
        self.assertEqual( transaction['payee'], 'John\xc2\xa0Doe' )
        self.assertEqual( transaction['address'], 'Voidstreet\xc2\xa05' )
        self.assertEqual( transaction['city'], 'Alabama' )
        self.assertEqual( transaction['postal code'], '2610' )
        self.assertEqual( transaction['value date'], datetime.date(1922,1,1) )
        self.assertEqual( transaction['message'], '080/0163/21631' )
    # --------------------------------------------------------------------------
    def test_outgoing_national2(self):
        message = 'Uw overschrijving 310-1610249-38 Doe\xc2\xa0Inc. 1342235809 Valutadatum: 01/01/1923'
        transaction = dbreader.process_message_body( message, False )
        self.assertEqual( transaction['account number'], '310-1610249-38' )
        self.assertEqual( transaction['payee'], 'Doe\xc2\xa0Inc.' )
        self.assertEqual( transaction['message'], '1342235809' )
        self.assertEqual( transaction['value date'], datetime.date(1923,1,1) )
    # --------------------------------------------------------------------------
    def test_outgoing_international(self):
        message = 'Uw\xc2\xa0overschrijving -- RABONL2UXXX NL29\xc2\xa0RABO\xc2\xa00105\xc2\xa08855\xc2\xa009 John\xc2\xa0Doe Voidstreet\xc2\xa0130\xc2\xa01071\xc2\xa0XW\xc2\xa0Amsterdam\xc2\xa0NL Com: this is some communication Valutadatum: 01/01/1900'
        transaction = dbreader.process_message_body( message, False )
        self.assertEqual( transaction['bic'], 'RABONL2UXXX' )
        self.assertEqual( transaction['iban'], 'NL29\xc2\xa0RABO\xc2\xa00105\xc2\xa08855\xc2\xa009' )
        self.assertEqual( transaction['payee'], 'John\xc2\xa0Doe\xc2\xa0Voidstreet\xc2\xa0130\xc2\xa01071\xc2\xa0XW\xc2\xa0Amsterdam\xc2\xa0NL' )
        self.assertEqual( transaction['message'], 'this is some communication' )
        self.assertEqual( transaction['value date'], datetime.date(1900,1,1) )
    # --------------------------------------------------------------------------
    def test_outgoing1(self):
        message = 'Uw\xc2\xa0overschrijving -- BE80777591050277 Distr. Alabama\xc2\xa0--\xc2\xa0Finances Voidstreet\xc2\xa022\xc2\xa0Bus\xc2\xa0111\xc2\xa02600 Alabama US Com: +++001/0028/72387+++'
        transaction = dbreader.process_message_body( message, False )
        self.assertEqual( transaction['account number'], 'BE80777591050277' )
        self.assertEqual( transaction['payee'], 'Distr.' )
        self.assertEqual( transaction['address'], 'Alabama\xc2\xa0--\xc2\xa0Finances Voidstreet\xc2\xa022\xc2\xa0Bus\xc2\xa0111\xc2\xa02600 Alabama US' )
        self.assertEqual( transaction['message'], '+++001/0028/72387+++' )
    # --------------------------------------------------------------------------
    def test_outgoing2( self ):
        message = 'Uw\xc2\xa0overschrijving -- BE42091010100254 ZNA - - BE Com: +++510/9515/61064+++ Valutadatum: 01/01/1900'
        transaction = dbreader.process_message_body( message, False )
        self.assertEqual( transaction['account number'], 'BE42091010100254' )
        self.assertEqual( transaction['payee'], 'ZNA\xc2\xa0-\xc2\xa0-\xc2\xa0BE' )
        self.assertEqual( transaction['message'], '+++510/9515/61064+++' )
        self.assertEqual( transaction['value date'], datetime.date(1900,1,1) )
    # --------------------------------------------------------------------------
# ==============================================================================
if __name__ == '__main__':
    unittest.main()
# ==============================================================================