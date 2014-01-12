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
import re
from pprint import pprint
# ==============================================================================

CATEGORIES = {
    '^GB.*': 'Alimentation:Supermarché', # 'Food:Groceries',
    '^DOME\xc2\xa0BVBA$': 'Alimentation:Supermarché',
    '^DELH.*': 'Alimentation:Supermarché',
    '^LOUIS DELHAIZE.*': 'Alimentation:Supermarché',
    '^COLRUYT.*': 'Alimentation:Supermarché',
    '^VLEUGELS.*': 'Alimentation:Supermarché',
    '^BUERMANS.*': 'Alimentation:Supermarché',
    '^PAIN QUOTIDIEN$': 'Alimentation',
    '^EXPRESS GERMOIR$': 'Alimentation:Supermarché',
    '^SHOP N GO.*$': 'Alimentation:Supermarché',
    '^AUCHAN.*$': 'Alimentation:Supermarché',
    '^ALLIER DOYET$': 'Alimentation:Supermarché',
    '^E\.LECLERC.*$': 'Alimentation:Supermarché',
    '^CARREFOUR.*$': 'Alimentation:Supermarché',

    '^C.C. ALLOCATIONS FAM.*$': 'Allocations et Sécurité sociale:Allocations familiales',

    '^MUT\. ST MICHEL.*$': 'Allocations et Sécurité sociale:Remboursement de frais de santé',

    '^O\.N\.E\.M\..*$': 'Allocations et Sécurité sociale:Allocations interruption carriere',

    '^WANIMO$': 'Animaux',

    '^PARKING.*$': 'Automobile:Stationnement',

    '^DAC.*$': 'Automobile:Carburant',
    '^SA CHIRAULT DAC.*$': 'Automobile:Carburant',

    '^AUTOROUTE.*$': 'Automobile:Péage',
    '^COFIROUTE.*$': 'Automobile:Péage',
    '^SANEF.*$': 'Automobile:Péage',
    '^VIADUC.*$': 'Automobile:Péage',
    '^APRR.*$': 'Automobile:Péage',

    '^AMAZON EU.*$': 'Dons:Cadeaux',
    '^SEPTIEME TASSE\(LA\)$': 'Dons:Cadeaux',
    '^CONF\.DU TECH$': 'Dons:Cadeaux',
    '^IRSI CHOCOLATIER.*$': 'Dons:Cadeaux',

    '^GREENPEACE.*$': 'Dons:Caritatif',
    '^GAIA.*$': 'Dons:Caritatif',
    '^WWF.*$': 'Dons:Caritatif',
    '^HANDICAP INTERNATIONAL.*$': 'Dons:Caritatif',

    '^PH BAILLI LOUISE.*$': 'Santé:Pharmacie',
    '^PHARM.*$': 'Santé:Pharmacie',
    '^PH\.AELTERMAN.*$': 'Santé:Pharmacie',
    '^MULTIPHARMA.*$': 'Santé:Pharmacie',

    '^INSTITUT DE BIOLOGIE.*$': 'Santé:Analyses',

    '^QUICK.*$': 'Restaurant:Fast-food',
    '^MC ?DONALDS.*$': 'Restaurant:Fast-food',
    '^MC DONALD\'S.*$': 'Restaurant:Fast-food',
    '^SARL ORIBELULO$': 'Restaurant:Fast-food',

    '^PIZZA HUT.*$': 'Restaurant:Pizzeria',

    '^EXKI.*$': 'Restaurant:Autres restaurants',
    '^PANOS.*$': 'Restaurant:Autres restaurants',
    '^SUBWAY$': 'Restaurant:Autres restaurants',
    '^YAMA SUSHI$': 'Restaurant:Autres restaurants',
    '^BRASSERIE.*$': 'Restaurant:Autres restaurants',
    '^BRUSSELS GRILL.*$': 'Restaurant:Autres restaurants',
    '^RESTO.*$': 'Restaurant:Autres restaurants',
    '^L AMOUR FOU$': 'Restaurant:Autres restaurants',
    '^ETS NICOLAS$': 'Restaurant:Autres restaurants',
    '^PESCATORE$': 'Restaurant:Autres restaurants',
    '^SERVIBEL.*$': 'Restaurant:Autres restaurants',
    '^WWW\.2013\.RMLL\.INFO/FR$': 'Restaurant:Autres restaurants',
    '^QUARTIER LIBRE$': 'Restaurant:Autres restaurants',

    '^NMBS.*$': 'Transport:Train',
    '^SNCB\xc2\xa0NMBS.*$': 'Transport:Train',

    '^STIB.*$': 'Transport:Transports en commun',
    '^15404 GO BAILLI$': 'Transport:Transports en commun',

    '^H&M.*': 'Soins:Habillement',
    '^ZARA.*': 'Soins:Habillement',
    '^WE\xc2\xa0MEN.*': 'Soins:Habillement',
    '^BALTIC\xc2\xa0TEXTILE$': 'Soins:Habillement',
    '^EPISODE\xc2\xa0BELGIUM$': 'Soins:Habillement',
    '^COS.*$': 'Soins:Habillement',
    '^LA HALLE.*$': 'Soins:Habillement',
    '^GALERIA INNO.*$': 'Soins:Habillement',
    '^SARENZA.*$': 'Soins:Habillement',
    '^LA REDOUTE.*$': 'Soins:Habillement',

    '^SCHEDOM\xc2\xa0NV/SA.*': 'Frais généraux:Internet',
    '^schedom nv/sa.*': 'Frais généraux:Internet',
    '^Scarlet.*': 'Frais généraux:Internet',

    '^Belgacom.*$': 'Frais généraux:Téléphone',

    '^Proximus.*$': 'Frais généraux:Téléphone portable',

    '^LAMPIRIS.*$': 'Frais généraux:Electricité',
    '^Electrabel.*$': 'Frais généraux:Electricité',

    '^AWW.*$': 'Frais généraux:Eau',

    '^Onafhankelijk Ziekenfonds$': 'Assurance',
    '^ONAFHANKELIJK\xc2\xa0ZIEKENFONDS$': 'Assurance',

    '^GOOGLE.*$': 'Loisirs:Informatique',

    '^AZ MIDDELHEIM$': 'Santé:Hôpital',
    '^HOPITAUX.*$': 'Santé:Hôpital',
    '^H\.I\.S\..*$': 'Santé:Hôpital',
    '^HIS.*$': 'Santé:Hôpital',

    '^BELFIUS.*$': "Retrait d'espèces",
    '^BMPB.*$': "Retrait d'espèces",
    '^DEXIA.*$': "Retrait d'espèces",
    '^KBC.*$': "Retrait d'espèces",
    '^CBC.*$': "Retrait d'espèces",
    "^SELF'BANK MERCAT$": "Retrait d'espèces",
    "^WILRIJK BOUDEWIJ$": "Retrait d'espèces",
    "^ANTW . GROENPL.$": "Retrait d'espèces",
    "^BERCHEM GROTE ST$": "Retrait d'espèces",
    "^ELSENE NAAMSEPOO$": "Retrait d'espèces",

    '^FWO*$': "Revenus du travail:Salaire net",
    '^DDFIP*$': "Revenus du travail:Salaire net",

    '^IKEA.*$': "Maison:Ameublement",

    '^Sodexo Titres Services.*$': 'Maison:Personnel de maison',

    '^BRICO.*$': "Maison:Travaux",
    '^LEROY MERLIN.*$': "Maison:Travaux",

    '^EUREKAKIDS$': 'Loisirs:Jeux et jouets',
    '^EVEIL&amp;JEUX.*$': 'Loisirs:Jeux et jouets',
    '^LA GDE RECRE.*$': 'Loisirs:Jeux et jouets',
    '^GRANDE RECRE.*$': 'Loisirs:Jeux et jouets',

    '^WWW\.DREAMBABY\.BE$': 'Enfants:Equipement',

    '^DECATHLON.*$': 'Loisirs:Sport',
    '^Golazo Sports.*$': 'Loisirs:Sport',

    '^Belgique Loisirs.*$': 'Loisirs:Livres et Magazines',

    '^BUREAU DE RECETTE.*$': 'Taxes et impôts',

    '^S\.P\.F\. FINANCES.*$': 'Autres revenus:Crédits d\'impôts',

    '^PHOTOLINEA$': 'Autres dépenses:Photographie',
}

def get_category(entry):

    if entry['payee'] is not None:
        for pat, cat in CATEGORIES.iteritems():
            if re.compile(pat, re.IGNORECASE).match(entry['payee']) is not None:
                return cat

    if entry['message'] is not None:
        for pat, cat in CATEGORIES.iteritems():
            if re.compile(pat, re.IGNORECASE).match(entry['message']) is not None:
                return cat

    pprint(entry)
    print("="*50)

    return None