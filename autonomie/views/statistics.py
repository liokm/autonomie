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
import logging
import colander

from sqlalchemy import desc
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPClientError,
)
from colanderalchemy import SQLAlchemySchemaNode

from autonomie.statistics import inspect

from autonomie.resources import statistics_js
from autonomie.models.user import UserDatas
from autonomie.models.statistics import (
    StatisticSheet,
    StatisticEntry,
    CommonStatisticCriterion,
    OptListStatisticCriterion,
    DateStatisticCriterion,
)
from autonomie.utils import rest
from autonomie.views import (
    BaseView,
    DisableView,
)


CRITERION_MODELS = {
    "date": DateStatisticCriterion,
    "num": CommonStatisticCriterion,
    "opt_rel": OptListStatisticCriterion,
    "string": CommonStatisticCriterion
}

logger = logging.getLogger(__name__)


class StatisticSheetList(BaseView):
    """
    Listview of statistic sheets
    """
    title = u"Feuilles de statistiques"

    def __call__(self):
        statistics_js.need()
        sheets = StatisticSheet.query()
        sheets = sheets.order_by(desc(StatisticSheet.active)).all()

        submiturl = self.request.route_path(
            'statistics',
            _query=dict(action='add'),
        )

        return dict(sheets=sheets, title=self.title, submiturl=submiturl)


def statistic_sheet_add_edit_view(context, request):
    """
    View for adding editing statistics sheets
    """
    logger.info("Here we are")
    logger.info(request.POST)
    if 'title' in request.POST:
        schema = SQLAlchemySchemaNode(StatisticSheet, includes=('title',))

        try:
            appstruct = schema.deserialize(request.POST)
        except colander.Invalid:
            logger.exception(u"Erreur à la création de la feuille de \
statistiques")
        else:
            if context.__name__ == 'statistic_sheet':
                sheet = schema.objectify(appstruct, context)
                sheet = request.dbsession.merge(sheet)
            else:
                sheet = schema.objectify(appstruct)
                request.dbsession.add(sheet)
            request.dbsession.flush()
            url = request.route_path('statistic', id=sheet.id)
            return HTTPFound(url)
        logger.debug(u"Invalid datas have been passed")
        raise HTTPClientError()
    logger.debug(u"Missing datas in the request")
    raise HTTPClientError()


def statistic_sheet_view(context, request):
    """
    Statistic sheet view
    """
    statistics_js.need()
    loadurl = request.route_path(
        'statistic',
        id=context.id,
        _query=dict(action='options'),
    )
    contexturl = request.current_route_path()
    return dict(
        title=u"Feuille de statistiques",
        loadurl=loadurl,
        contexturl=contexturl,
    )


def statistic_form_options(context, request):
    """
    Returns datas used to build the statistic form page
    """
    inspector = inspect.StatisticInspector(UserDatas)

    return dict(
        columns=inspector.get_json_columns(),
        sheet_edit_url=request.route_path(
            'statistic',
            id=context.id,
            _query=dict(action='edit')
        ),
        entry_root_url=request.route_path(
            'statistic_entries',
            id=context.id,
        ),
    )


class StatisticDisableView(DisableView):
    enable_msg = u"La feuille de statistiques a été activée"
    disable_msg = u"La feuille de statistiques a été désactivée"
    redirect_route = "statistics"


class RestStatisticSheet(BaseView):
    """
    Json rest api for statistic sheet handling
    """

    @property
    def schema(self):
        return SQLAlchemySchemaNode(
            StatisticSheet,
            includes=('title',)
        )

    def get(self):
        return {
            'sheet': self.context,
            'entries': self.context.entries
        }

    def put(self):
        submitted = self.request.json_body
        logger.debug(u"Submitting %s" % submitted)

        try:
            attributes = self.schema.deserialize(submitted)
        except colander.Invalid, err:
            logger.exception("  - Erreur")
            logger.exception(submitted)
            raise rest.RestError(err.asdict(), 400)
        logger.debug(attributes)
        sheet = self.schema.objectify(attributes, self.context)
        sheet = self.request.dbsession.merge(sheet)
        return sheet


class RestStatisticEntry(BaseView):
    """
    Json rest api for statistic entries handling
    """
    @property
    def schema(self):
        return SQLAlchemySchemaNode(
            StatisticEntry,
            includes=('title', 'description',),
        )

    def get(self):
        """
        Return the entry matching the context
        """
        return self.context

    def collection_get(self):
        """
        Return the list of entries
        context is the parent sheet
        """
        return self.context.entries

    def post(self):
        """
        Entry add view

        context is the parent sheet
        """
        submitted = self.request.json_body
        logger.debug(u"Submitting %s" % submitted)

        try:
            attributes = self.schema.deserialize(submitted)
        except colander.Invalid, err:
            logger.exception("  - Erreur")
            logger.exception(submitted)
            raise rest.RestError(err.asdict(), 400)

        logger.debug(attributes)
        entry = self.schema.objectify(attributes)
        entry.sheet = self.context
        self.request.dbsession.add(entry)
        self.request.dbsession.flush()
        logger.debug(entry)
        return entry

    def put(self):
        """
        edit a given entry

        context is the current entry
        """
        submitted = self.request.json_body
        logger.debug(u"Submitting %s" % submitted)

        try:
            attributes = self.schema.deserialize(submitted)
        except colander.Invalid, err:
            logger.exception("  - Erreur")
            logger.exception(submitted)
            raise rest.RestError(err.asdict(), 400)

        logger.debug(attributes)
        entry = self.schema.objectify(attributes, self.context)
        entry = self.request.dbsession.merge(entry)
        return entry

    def delete(self):
        """
        Delete the given entry
        """
        self.request.dbsession.delete(self.context)
        return {}


class RestStatisticCriterion(BaseView):
    """
    Api rest pour la gestion des critères statistiques
    """
    def schema(self, model_type):
        model = CRITERION_MODELS.get(model_type)
        return SQLAlchemySchemaNode(
            model,
            excludes=('type_', 'type'),
        )

    def collection_get(self):
        return self.context.criteria

    def post(self):
        submitted = self.request.json_body
        logger.debug(u"Submitting %s" % submitted)

        model_type = submitted['type']
        schema = self.schema(model_type)

        try:
            attributes = schema.deserialize(submitted)
        except colander.Invalid, err:
            logger.exception("  - Erreur")
            logger.exception(submitted)
            raise rest.RestError(err.asdict(), 400)

        logger.debug(attributes)
        criterion = self.schema.objectify(attributes)
        criterion.entry = self.context
        self.request.dbsession.add(criterion)
        self.request.dbsession.flush()
        logger.debug(criterion)
        return criterion

    def get(self):
        return self.context

    def put(self):
        submitted = self.request.json_body
        logger.debug(u"Submitting %s" % submitted)

        model_type = submitted['type']
        schema = self.schema(model_type)

        try:
            attributes = schema.deserialize(submitted)
        except colander.Invalid, err:
            logger.exception("  - Erreur")
            logger.exception(submitted)
            raise rest.RestError(err.asdict(), 400)

        logger.debug(attributes)
        criterion = self.schema.objectify(attributes, self.context)
        self.request.dbsession.merge(criterion)
        return criterion

    def delete(self):
        """
        Delete the given entry
        """
        self.request.dbsession.delete(self.context)
        return {}


def includeme(config):
    """
    Include views in the app's configuration
    """
    # Routes for statistic sheet view/add/edit/delete
    config.add_route(
        'statistics',
        '/statistics',
    )

    config.add_route(
        'statistic',
        '/statistics/{id:\d+}',
        traverse='/statistics/{id}',
    )

    config.add_route(
        'statistic_entries',
        '/statistics/{id}/entries',
        traverse='/statistics/{id}',
    )
    config.add_route(
        'statistic_entry',
        '/statistics/{id}/entries/{eid:\d+}',
        traverse='/statistic_entries/{eid}',
    )
    config.add_route(
        "statistic_criteria",
        "/statistics/{id}/entries/{eid:\d+}/criteria",
        traverse='/statistic_entries/{eid}',
    )
    config.add_route(
        "statistic_criterion",
        "/statistics/{id}/entries/{eid:\d+}/criteria/{cid:\d+}",
        traverse='/statistic_criteria/{cid}',
    )

    config.add_view(
        StatisticSheetList,
        route_name='statistics',
        renderer="statistics/list.mako",
        permission='manage',
    )

    config.add_view(
        statistic_sheet_add_edit_view,
        route_name="statistics",
        request_param="action=add",
        permission='manage',
    )
    config.add_view(
        statistic_sheet_add_edit_view,
        route_name="statistic",
        request_param="action=edit",
        permission='manage',
    )

    config.add_view(
        statistic_form_options,
        route_name='statistic',
        renderer='json',
        xhr=True,
        request_method='GET',
        request_param="action=options",
        permission='manage',
    )

    config.add_view(
        statistic_sheet_view,
        route_name='statistic',
        renderer='statistics/edit.mako',
    )

    config.add_view(
        StatisticDisableView,
        route_name="statistic",
        request_param="action=disable",
        permission='manage',
    )

    for attr in ('put', 'get'):
        config.add_view(
            RestStatisticSheet,
            attr=attr,
            route_name='statistic',
            request_method=attr.upper(),
            permission='manage',
            renderer='json',
            xhr=True,
        )

    for attr in ('put', 'get', 'delete'):
        config.add_view(
            RestStatisticEntry,
            attr=attr,
            route_name='statistic_entry',
            request_method=attr.upper(),
            permission='manage',
            renderer='json',
            xhr=True,
        )
        config.add_view(
            RestStatisticCriterion,
            attr=attr,
            route_name='statistic_criterion',
            request_method=attr.upper(),
            permission='manage',
            renderer='json',
            xhr=True,
        )

    for attr in ('post', 'collection_get'):
        config.add_view(
            RestStatisticEntry,
            attr=attr,
            route_name='statistic_entries',
            request_method=attr.upper(),
            permission='manage',
            renderer='json',
            xhr=True,
        )
        config.add_view(
            RestStatisticCriterion,
            attr=attr,
            route_name='statistic_criteria',
            request_method=attr.upper(),
            permission='manage',
            renderer='json',
            xhr=True,
        )
