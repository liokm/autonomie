# -*- coding: utf-8 -*-
# * File Name : project.py
#
# * Copyright (C) 2010 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 29-03-2012
# * Last Modified :
#
# * Project : Autonomie
#
"""
    Project views
"""
import logging
from colorsys import hsv_to_rgb
from random import uniform

from sqlalchemy import or_
from webhelpers.html.builder import HTML
from deform import ValidationFailure
from deform import Form

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import has_permission

from autonomie.models.model import Project
from autonomie.models.model import Phase
from autonomie.models.model import Client
from autonomie.utils.widgets import ViewLink
from autonomie.utils.widgets import ToggleLink
from autonomie.utils.widgets import ItemActionLink
from autonomie.utils.widgets import StaticWidget
from autonomie.utils.widgets import PopUp
from autonomie.utils.widgets import SearchForm
from autonomie.utils.views import submit_btn
from autonomie.utils.forms import merge_session_with_post
from autonomie.views.forms import ProjectSchema
from .base import ListView

log = logging.getLogger(__name__)


def rgb_to_hex(rgb):
    """
        return an hexadecimal version of the rgb tuple
        for css rendering
    """
    return '#%02x%02x%02x' % rgb


def get_color():
    """
        return a random color
    """
    h = uniform(0.1, 0.8)
    s = uniform(0.8, 1)
    v = uniform(0.8, 1)
    return rgb_to_hex(tuple(255 * c for c in hsv_to_rgb(h, s, v)))


def build_client_value(client):
    """
        return the tuple for building client select
    """
    if client:
        return (client.id, client.name)
    else:
        return (u" - ", u"Sélectionnez")


def build_client_values(clients):
    """
        Build human understandable client labels
        allowing efficient discrimination
    """
    return [build_client_value(client)
                            for client in clients]


def get_project_form(clients, default_client=None, edit=False):
    """
        Returns the project add/edit form
    """
    choices = build_client_values(clients)
    default = build_client_value(default_client)
    schema = ProjectSchema().bind(edit=edit, choices=choices, default=default)
    form = Form(schema, buttons=(submit_btn,))
    return form


class ProjectView(ListView):
    """
        All the projects views are grouped in this class
    """
    columns = dict(code=Project.code,
                    name=Project.name,
                    client=Client.name)
    default_sort = 'name'

    def __init__(self, request):
        ListView.__init__(self, request)
        self._set_actionmenu()

    def _set_actionmenu(self):
        """
            Sets the action menu
        """
        self.actionmenu.add(ViewLink(u"Liste des projets", "edit",
                                     path="company_projects",
                                     id=self.context.get_company_id()))
        if self.context.__name__ == 'project':
            self.actionmenu.add(self._get_view_btn())
            self.actionmenu.add(self._get_edit_btn())
            if has_permission('edit', self.context, self.request):
                self.actionmenu.add(self._get_detail_btn())
                self.actionmenu.add(self._get_phase_btn())

    def redirect_to_clients(self, company):
        """
            Force project page to be redirected to client page
        """
        self.request.session.flash(u"Vous avez été redirigé vers la liste \
des clients", queue="main")
        self.request.session.flash(u"Vous devez créer des clients afin \
de créer de nouveaux projets", queue="main")
        raise HTTPFound(self.request.route_path("company_clients",
                                                id=company.id))

    @view_config(route_name='company_projects',
                 renderer='company_projects.mako',
                 request_method='GET',
                 permission='edit')
    def company_projects(self):
        """
            Return the list of projects
        """
        log.debug("Getting projects")
        company = self.request.context
        # If not client have been added, redirecting to clients page
        if not company.clients:
            self.redirect_to_clients(company)
        search, sort, direction, current_page, items_per_page = \
                                                self._get_pagination_args()

        archived = self.request.params.get('archived', '0')

        query = self._get_projects()
        if company:
            query = self._filter_company(query, company)
        query = self._filter_archived(query, archived)
        if search:
            query = self._filter_search(query, search)
        projects = self._sort(query, sort, direction).all()
        records = self._get_pagination(projects, current_page, items_per_page)

        ret_dict = dict(title=u"Liste des projets",
                        projects=records,
                        company=company,
                        action_menu=self.actionmenu,
                        item_actions=self._get_actions())

        if has_permission("add", self.context, self.request):
            popup = self._get_add_popup()
            ret_dict['popups'] = {popup.name: popup}
            self.actionmenu.add(popup.open_btn())
        self.actionmenu.add(self._get_archived_btn(archived))
        self.actionmenu.add(SearchForm(u"Projet ou nom du client"))
        return ret_dict

    def _get_projects(self):  # company, search, sort, direction, archived):
        """
            query projects against the database
        """
        return self.dbsession.query(Project).join(Project.client)

    @staticmethod
    def _filter_company(query, company):
        """
            add a filter for the company on the query
        """
        return query.filter(Project.company_id == company.id)

    @staticmethod
    def _filter_archived(query, archived):
        """
            add a filter to query only archived projects
        """
        if archived not in ("1", "0"):
            archived = "0"
        return query.filter(Project.archived == archived)

    @staticmethod
    def _filter_search(query, search):
        """
            filter the query on the searched argument
        """
        return query.filter(
            or_(Project.name.like("%" + search + "%"),
                Client.name.like("%" + search + "%"))
        )

    @view_config(route_name='company_projects',
                 renderer='project.mako',
                 request_method='POST',
                 permission='edit')
    @view_config(route_name='project',
                 renderer='project.mako',
                 request_param='action=edit',
                 permission='edit')
    def project(self):
        """
            Returns:
            * the company edit form
            or
            * the company add form when an error has occured
        """
        if self.request.context.__name__ == 'company':
            company = self.request.context
            project = Project()
            project.company_id = company.id
            edit = False
            default_client = None
            title = u"Ajout d'un nouveau projet"
        else:
            project = self.request.context
            company = project.company
            edit = True
            default_client = project.client
            title = u"Édition du projet : {0}".format(project.name)
        if not company.clients:
            self.redirect_to_clients(company)

        clients = company.clients
        form = get_project_form(clients,
                                default_client,
                                edit=edit)
        if 'submit' in self.request.params:
            # form POSTed
            datas = self.request.params.items()
            try:
                app_datas = form.validate(datas)
                log.debug(app_datas)
            except ValidationFailure, errform:
                html_form = errform.render()
            else:
                project = merge_session_with_post(project, app_datas)
                # The returned project is a persistent object
                project = self.dbsession.merge(project)
                self.dbsession.flush()
                if edit:
                    message = u"Le projet <b>{0}</b> a été édité avec \
succès".format(project.name)
                else:
                    default_phase = Phase()
                    default_phase.project = project
                    self.dbsession.merge(default_phase)
                    message = u"Le projet <b>{0}</b> a été ajouté avec \
succès".format(project.name)
                self.request.session.flash(message, queue='main')
                # Flusing the session launches sql queries
                return HTTPFound(self.request.route_path('project',
                                            id=project.id))
        else:
            html_form = form.render(project.appstruct())
        return dict(title=title,
                    project=project,
                    html_form=html_form,
                    company=company,
                    action_menu=self.actionmenu
                    )

    @view_config(route_name="project",
                 request_param="action=addphase",
                 permission='edit'
                )
    def add_phase(self):
        """
            Add a phase to the current project
        """
        project = self.request.context
        if not self.request.params.get('phase'):
            self.request.session.flash(u"Le nom de la phase est obligatoire",
                                                                queue='error')
            anchor = "showphase"
        else:
            phasename = self.request.params.get('phase')
            phase = Phase()
            phase.name = phasename
            phase.project_id = project.id
            self.dbsession.add(phase)
            self.request.session.flash(u"La phase {0} a bien été \
rajoutée".format(phasename), queue="main")
            anchor = ""
        return HTTPFound(self.request.route_path('project',
                                id=project.id,
                                _anchor=anchor))

    @view_config(route_name='project', renderer='project_view.mako',
            permission='view'
            )
    def project_view(self):
        """
            Company's project view
        """
        phases = self.context.phases
        for phase in phases:
            for estimation in phase.estimations:
                estimation.color = get_color()
        for phase in phases:
            for invoice in phase.invoices:
                if invoice.estimation:
                    invoice.color = invoice.estimation.color
                else:
                    invoice.color = get_color()
        for phase in phases:
            for cancelinvoice in phase.cancelinvoices:
                cancelinvoice.color = cancelinvoice.invoice.color

        return dict(title=u"Projet : {0}".format(self.context.name),
                    project=self.context,
                    action_menu=self.actionmenu,
                    company=self.context.company)

    @view_config(route_name="project",
                request_param="action=archive",
                permission='edit')
    def archive(self):
        """
            Archive the current project
        """
        project = self.request.context

        project.archived = 1
        self.dbsession.merge(project)
        self.request.session.flash(u"Le projet '{0}' a été archivé".format(
                                project.name), queue='main'
                                    )
        return HTTPFound(self.request.referer)

    @view_config(route_name="project",
                request_param="action=delete",
                permission='edit')
    def delete(self):
        """
            Delete the current project
        """
        project = self.request.context
        self.dbsession.delete(project)
        self.request.session.flash(u"Le projet '{0}' a bien été \
supprimé".format(project.name))
        return HTTPFound(self.request.referer)

    def _get_actions(self):
        """
            Return action buttons with permission handling
        """
        btns = []
        btns.append(ItemActionLink(u"Voir", "view", css='btn',
                path="project", icon="icon-search"))
        btns.append(ItemActionLink(u"Devis", "edit", css="btn",
            title=u"Nouveau devis",
            path="estimations", icon=("icon-file", )))
        btns.append(ItemActionLink(u"Facture", "edit", css="btn",
            title=u"Nouvelle facture",
            path="project_invoices", icon=("icon-file", )))
        if self.request.params.get('archived', '0') == '0':
            btns.append(ItemActionLink(u"Archiver", "edit", css="btn",
                   confirm=u'Êtes-vous sûr de vouloir archiver ce projet ?',
                                path="project",
                                title=u"Archiver le projet",
                                _query=dict(action="archive"),
                                icon="icon-book"))
        else:
            del_link = ItemActionLink(u"Supprimer", "edit", css="btn",
                   confirm=u'Êtes-vous sûr de vouloir supprimer ce projet ?',
                                      path="project",
                                      title=u"Supprimer le projet",
                                      _query=dict(action="delete"),
                                      icon="icon-trash")

            def is_deletable_perm(context, req):
                """
                    Return True if the current item (context) is deletable
                """
                return context.is_deletable()
            del_link.set_special_perm_func(is_deletable_perm)
            btns.append(del_link)
        return btns

    def _get_view_btn(self):
        """
            return the View button
        """
        return ViewLink(u"Voir", path="project", id=self.context.id)

    def _get_edit_btn(self):
        """
            return the Edit button
        """
        return ViewLink(u"Éditer",  path="project", id=self.context.id,
                                            _query=dict(action="edit"))

    @staticmethod
    def _get_detail_btn():
        """
            return the toggle button which show the details
        """
        return ToggleLink(u"Afficher les détails",
                          target="project-description")

    @staticmethod
    def _get_phase_btn():
        """
            return the toggle button for phase addition
        """
        return ToggleLink(u"Ajouter une phase", target="project-addphase",
                                                            css="addphase")

    def _get_archived_btn(self, archived):
        """
            return the show archived button
        """
        if archived == '0':
            url = self.request.current_route_path(_query=dict(archived="1"))
            link = HTML.a(u"Afficher les projets archivés",  href=url)
        else:
            url = self.request.current_route_path(_query=dict(archived="0"))
            link = HTML.a(u"Afficher les projets actifs", href=url)
        return StaticWidget(link)

    def _get_add_popup(self):
        """
            return a popup object for add project
        """
        form = get_project_form(clients=self.context.clients)
        return PopUp('add', u"Ajouter un projet", form.render())
