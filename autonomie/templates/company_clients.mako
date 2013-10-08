<%doc>
 * Copyright (C) 2012-2013 Croissance Commune
 * Authors:
       * Arezki Feth <f.a@majerti.fr>;
       * Miotte Julien <j.m@majerti.fr>;
       * Pettier Gabriel;
       * TJEBBES Gaston <g.t@majerti.fr>

 This file is part of Autonomie : Progiciel de gestion de CAE.

    Autonomie is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Autonomie is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Autonomie.  If not, see <http://www.gnu.org/licenses/>.
</%doc>

<%inherit file="base.mako"></%inherit>
<%namespace file="/base/pager.mako" import="pager"/>
<%namespace file="/base/pager.mako" import="sortable"/>
<%namespace file="/base/utils.mako" import="searchform"/>
<%namespace file="/base/utils.mako" import="table_btn"/>
<%block name='content'>
<table class="table table-striped table-condensed table-hover">
    <thead>
        <tr>
            <th>${sortable("Code", "code")}</th>
            <th>${sortable("Entreprise", "name")}</th>
            <th>${sortable("Nom du contact principal", "contactLastName")}</th>
            <th style="text-align:center">Actions</th>
        </tr>
    </thead>
    <tbody>
        % if records:
            % for client in records:
                <tr class='tableelement' id="${client.id}">
                    <td onclick="document.location='${request.route_path("client", id=client.id)}'" class="rowlink" >${client.code}</td>
                    <td onclick="document.location='${request.route_path("client", id=client.id)}'" class="rowlink" >${client.name}</td>
                    <td onclick="document.location='${request.route_path("client", id=client.id)}'" class="rowlink" >${client.contactLastName} ${client.contactFirstName}</td>
                    <td style="text-align:right">
                        ${table_btn(request.route_path("client", id=client.id), u"Voir/Éditer", u"Voir/Éditer ce client", icon=u"icon-pencil")}
                    </td>
                </tr>
            % endfor
        % else:
            <tr>
                <td colspan='6'>
                    Aucun client n'a été référencé pour l'instant
                </td>
            </tr>
        % endif
    </tbody>
</table>
${pager(records)}
</%block>
