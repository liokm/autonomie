# -*- coding: utf-8 -*-
# * Copyright (C) 2012-2014 Croissance Commune
# * Authors:
#       * Arezki Feth <f.a@majerti.fr>;
#       * Miotte Julien <j.m@majerti.fr>;
#       * TJEBBES Gaston <g.t@majerti.fr>
#
# This file is part of Autonomie : Progiciel de gestion de CAE.
#
#    Autonomie is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Autonomie is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
import pytest
import cStringIO as StringIO
csv_string = """Nom;Email 1;PRénom;Unknown
Arthur;b.arthur;Bienaimé;Datas
"""

def get_buffer():
    return StringIO.StringIO(csv_string)

@pytest.fixture
def csv_datas():
    import csv
    f = csv.DictReader(
        get_buffer(),
        quotechar='"',
        delimiter=';',
    )
    return f

@pytest.fixture
def association_handler():
    from autonomie.csv_import import CsvImportAssociator
    from autonomie.models.user import UserDatas
    return CsvImportAssociator(UserDatas)

@pytest.fixture
def userdata(dbsession):
    from autonomie.models.user import UserDatas
    u = UserDatas(
        coordonnees_firstname="firstname",
        coordonnees_lastname="lastname",
        coordonnees_email1="mail@mail.com",
    )
    dbsession.add(u)
    dbsession.flush()
    return u


def test_guess_association_dict(csv_datas, association_handler):
    res = association_handler.guess_association_dict(csv_datas.fieldnames)
    assert res[u'PRénom'] == 'coordonnees_firstname'
    assert res[u'Nom'] == 'coordonnees_lastname'
    assert res[u'Unknown'] is None

    # Test field exclusion
    from autonomie.csv_import import CsvImportAssociator
    from autonomie.models.user import UserDatas
    associator = CsvImportAssociator(
        UserDatas, excludes=('coordonnees_lastname',))
    res = associator.guess_association_dict(
        csv_datas.fieldnames,
    )
    assert res['Nom'] == 'name'


def test_collect_kwargs(association_handler):
    association_dict = {'a': 'A match', 'b': None}

    association_handler.set_association_dict(association_dict)

    line = {'a': 'A data', 'b': 'B data', 'c': 'C data'}
    kwargs, trashed = association_handler.collect_args(line)

    assert kwargs == {'A match': 'A data'}
    assert trashed == {'b': 'B data', 'c': 'C data'}


def test_import_line(dbsession, csv_datas, association_handler):
    from autonomie.csv_import import CsvImporter
    from autonomie.models.user import UserDatas


    association_dict = {
        'PRénom': 'coordonnees_firstname',
        'Nom': 'coordonnees_lastname',
        'Email 1': 'coordonnees_email1',
    }
    association_handler.set_association_dict(association_dict)

    line = csv_datas.next()
    importer = CsvImporter(UserDatas, get_buffer(), association_handler)
    res, msg = importer.import_line(line.copy())

    assert res.coordonnees_firstname == u'Bienaimé'
    assert res.coordonnees_lastname == u'Arthur'
    assert sorted(importer.unhandled_datas[0].keys()) == sorted(['id', 'Unknown'])
    assert importer.in_error_fields == []

    # We pop a mandatory argument
    association_dict.pop('Nom')
    association_handler.set_association_dict(association_dict)
    importer = CsvImporter(UserDatas, get_buffer(), association_handler)
    res, msg = importer.import_line(line.copy())

    assert res is None
    assert importer.in_error_fields == [line]


def test_update_line(association_handler, userdata):
    from autonomie.csv_import import CsvImporter
    from autonomie.models.user import UserDatas

    association_dict = {
        'firstname': 'coordonnees_firstname',
        'email': 'coordonnees_email2',
    }
    association_handler.set_association_dict(association_dict)

    importer = CsvImporter(
        UserDatas,
        get_buffer(),
        association_handler,
        action="update"
    )
    new_datas = {'id': str(userdata.id), 'firstname': u"Jane", 'email': "g@p.fr"}
    res, msg = importer.import_line(new_datas)

    assert res.coordonnees_lastname == u'lastname'
    assert res.coordonnees_firstname == u'firstname'
    assert res.coordonnees_email2 == 'g@p.fr'


def test_override_line(association_handler, userdata):
    from autonomie.csv_import import CsvImporter
    from autonomie.models.user import UserDatas

    association_dict = {
        'firstname': 'coordonnees_firstname',
        'email': 'coordonnees_email2',
    }
    association_handler.set_association_dict(association_dict)

    importer = CsvImporter(
        UserDatas,
        get_buffer(),
        association_handler,
        action="override"
    )
    new_datas = {'id': str(userdata.id), 'firstname': u"Jane", 'email': "g@p.fr"}
    res, msg = importer.import_line(new_datas)

    assert res.coordonnees_lastname == u'lastname'
    assert res.coordonnees_firstname == u'Jane'
    assert res.coordonnees_email2 == 'g@p.fr'


def test_identification_key(association_handler, userdata):
    """
    Test if we use another key than "id" to identify the duplicate entries
    """
    from autonomie.csv_import import CsvImporter
    from autonomie.models.user import UserDatas

    association_dict = {
        'firstname': 'coordonnees_firstname',
        'email': "coordonnees_email1",
        'test': 'coordonnees_emergency_name',
    }
    association_handler.set_association_dict(association_dict)

    importer = CsvImporter(
        UserDatas,
        get_buffer(),
        association_handler,
        action="update",
        id_key="coordonnees_email1",
    )
    # Ici on utilise le même mail
    new_datas = {
        'email': "mail@mail.com",
        'test': u"Emergency Contact"
    }
    res, msg = importer.import_line(new_datas)
    assert res.coordonnees_lastname == u'lastname'
    assert res.coordonnees_emergency_name == u"Emergency Contact"

