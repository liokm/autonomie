# -*- coding: utf-8 -*-
# * File Name : static.py
#
# * Copyright (C) 2012 Gaston TJEBBES <g.t@majerti.fr>
# * Company : Majerti ( http://www.majerti.fr )
#
#   This software is distributed under GPLV3
#   License: http://www.gnu.org/licenses/gpl-3.0.txt
#
# * Creation Date : 28-01-2013
# * Last Modified :
#
# * Project : Autonomie
#
"""
    Custom views for dynamic static datas
"""
import os

from pkg_resources import resource_filename

from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

def make_root_static_view(filename, ctype):
    """
        Return a static view rendering given file with headers set to the ctyp
        Content-Type
    """
    fpath = resource_filename("autonomie", os.path.join("static", filename))
    file_datas = open(fpath).read()
    file_response =  Response(content_type=ctype, body=file_datas)
    def static_view(context, request):
        return file_response
    return static_view


def includeme(config):
    config.add_route('favicon.ico', '/favicon.ico')
    config.add_route('robots.txt', '/robots.txt')
    config.add_view(make_root_static_view("robots.txt", 'text/plain'),
                        route_name="robots.txt",
                        permission=NO_PERMISSION_REQUIRED)
    config.add_view(make_root_static_view("favicon.ico", "image/x-icon"),
                        route_name="favicon.ico",
                        permission=NO_PERMISSION_REQUIRED)
