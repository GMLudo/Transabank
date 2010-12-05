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
import re
# ==============================================================================
def get_category( entry ):

    # to case-insensitive matching
    re.IGNORECASE

    print repr( entry['payee'] )

    if entry['payee'] is not None:
        # ---------------------------------------------------------------------
        pat = re.compile( '^GB.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Groceries'

        pat = re.compile( '^DOME\xc2\xa0BVBA$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Groceries'

        # Delhaize
        pat = re.compile( '^DELH.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Groceries'

        pat = re.compile( '^COLRUYT.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Groceries'

        pat = re.compile( '^VLEUGELS.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Groceries'

        pat = re.compile( '^BUERMANS.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Groceries'

        pat = re.compile( '^PAIN QUOTIDIEN$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Groceries'
        # ---------------------------------------------------------------------
        pat = re.compile( '^PIZZA HUT.*$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Dining Out'

        pat = re.compile( '^EXKI.*$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Dining Out'

        pat = re.compile( '^QUICK.*$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Dining Out'

        pat = re.compile( '^SUBWAY$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Food:Dining Out'
        # ---------------------------------------------------------------------
        pat = re.compile( '^NMBS.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Travel:Fares'

        pat = re.compile( '^SNCB\xc2\xa0NMBS.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Travel:Fares'

        # Metro Brussels
        pat = re.compile( '^STIB.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Travel:Fares'
        # ---------------------------------------------------------------------
        pat = re.compile( '^H&M.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Clothing'

        pat = re.compile( '^ZARA.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Clothing'

        pat = re.compile( '^WE\xc2\xa0MEN.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Clothing'

        pat = re.compile( '^BALTIC\xc2\xa0TEXTILE$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Clothing'

        pat = re.compile( '^EPISODE\xc2\xa0BELGIUM$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Clothing'

        pat = re.compile( '^COS.*$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Clothing'
        # ---------------------------------------------------------------------
        pat = re.compile( '^SCHEDOM\xc2\xa0NV/SA.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Bills:Telephone'

        pat = re.compile( '^schedom nv/sa.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Bills:Telephone'

        pat = re.compile( '^LAMPIRIS.*$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Bills:Electricity'

        pat = re.compile( '^Electrabel.*$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Bills:Electricity'

        pat = re.compile( '^AWW.*$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Bills:Water & sewage'
        # --------------------------------------------------------------------
        pat = re.compile( '^Onafhankelijk Ziekenfonds$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Insurance'

        pat = re.compile( '^ONAFHANKELIJK\xc2\xa0ZIEKENFONDS$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Insurance'
        # ---------------------------------------------------------------------
        pat = re.compile( '^AZ MIDDELHEIM$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Healthcare:Hospital'
        # ---------------------------------------------------------------------
        pat = re.compile( '^KBC.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Cash Withdrawal'

        pat = re.compile( '^DEXIA.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Cash Withdrawal'

        pat = re.compile( "^SELF'BANK MERCAT$" )
        if pat.match( entry['payee'] ) is not None:
            return 'Cash Withdrawal'

        pat = re.compile( "^WILRIJK BOUDEWIJ$" )
        if pat.match( entry['payee'] ) is not None:
            return 'Cash Withdrawal'

        pat = re.compile( "^ANTW . GROENPL.$" )
        if pat.match( entry['payee'] ) is not None:
            return 'Cash Withdrawal'

        pat = re.compile( "^BERCHEM GROTE ST$" )
        if pat.match( entry['payee'] ) is not None:
            return 'Cash Withdrawal'

        pat = re.compile( "^ELSENE NAAMSEPOO$" )
        if pat.match( entry['payee'] ) is not None:
            return 'Cash Withdrawal'
        # ---------------------------------------------------------------------
        pat = re.compile( '^FWO*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Employment:Salary & wages'
        # ---------------------------------------------------------------------
        pat = re.compile( '^IKEA.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Household:Furnishings'

        pat = re.compile( '^BRICO.*' )
        if pat.match( entry['payee'] ) is not None:
            return 'Household:Furnishings'
        # ---------------------------------------------------------------------
        pat = re.compile( '^UA$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Employment:Foreign'
        # ---------------------------------------------------------------------
        pat = re.compile( '^KOPPIE-KOPIE$' )
        if pat.match( entry['payee'] ) is not None:
            return 'Business:Other'
        # ---------------------------------------------------------------------

    if entry['message'] is not None:
        # ---------------------------------------------------------------------
        pat = re.compile( '^electrabel.*' )
        if pat.match( entry['message'] ) is not None:
            return 'Bills:Electricity'

        pat = re.compile( '^Electrabel.*' )
        if pat.match( entry['message'] ) is not None:
            return 'Bills:Electricity'

        pat = re.compile( '^AWW.*' )
        if pat.match( entry['message'] ) is not None:
            return 'Bills:Water & Sewage'

        pat = re.compile( '^Belgacom.*' )
        if pat.match( entry['message'] ) is not None:
            return 'Bills:Telephone'
        # ---------------------------------------------------------------------

    return None
# ===============================================================================