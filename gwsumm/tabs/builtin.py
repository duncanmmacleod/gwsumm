# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2013)
#
# This file is part of GWSumm
#
# GWSumm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWSumm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWSumm.  If not, see <http://www.gnu.org/licenses/>

"""This module defines a number of `Tab` subclasses.
"""

from .core import (Tab, SummaryArchiveMixin)
from .registry import register_tab
from ..plot import get_plot
from ..utils import *
from ..config import *
from ..state import ALLSTATE
from .. import html

from gwsumm import version
__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'
__version__ = version.version

SummaryPlot = get_plot(None)
DataPlot = get_plot('data')


class ExternalTab(Tab):
    """A simple tab to link HTML from an external source

    Parameters
    ----------
    name : `str`
        name of this tab (required)
    url : `str`
        URL of the external content to be linked into this tab.
    index : `str`
        HTML file in which to write. By default each tab is written to
        an index.html file in its own directory. Use :attr:`~Tab.index`
        to find out the default index, if not given.
    shortname : `str`
        shorter name for this tab to use in the navigation bar. By
        default the regular name is used
    parent : :class:`~gwsumm.tabs.Tab`
        parent of this tab. This is used to position this tab in the
        navigation bar.
    children : `list`
        list of child :class:`Tabs <~gwsumm.tabs.Tab>` of this one. This
        is used to position this tab in the navigation bar.
    group : `str`
        name of containing group for this tab in the navigation bar
        dropdown menu. This is only relevant if this tab has a parent.
    path : `str`
        base output directory for this tab (should be the same directory
        for all tabs in this run).

    Configuration
    -------------

    """
    type = 'external'

    def __init__(self, name, url, error=True, success=None, **kwargs):
        """Initialise a new `ExternalTab`.
        """
        super(ExternalTab, self).__init__(name, **kwargs)
        self.url = url
        self.error = error
        self.success = success

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, link):
        self._url = link

    @classmethod
    def from_ini(cls, cp, section, *args, **kwargs):
        """Configure a new `ExternalTab` from a `ConfigParser` section

        Parameters
        ----------
        cp : :class:`~gwsumm.config.ConfigParser`
            configuration to parse.
        section : `str`
            name of section to read

        See Also
        --------
        Tab.from_ini :
            for documentation of the standard configuration
            options

        Notes
        -----
        On top of the standard configuration options, the `ExternalTab` can
        be configured with the ``url`` option, specifying the URL of the
        external content to be included:

        .. code-block:: ini

           [tab-external]
           name = External data
           type = external
           url = https://www.example.org/index.html


        """
        url = cp.get(section, 'url')
        if cp.has_option(section, 'error'):
            kwargs.setdefault(
                'error', re_quote.sub('', cp.get(section, 'error')))
        if cp.has_option(section, 'success'):
            kwargs.setdefault(
                'success', re_quote.sub('', cp.get(section, 'success')))
        return super(ExternalTab, cls).from_ini(cp, section, url, *args, **kwargs)

    def build_html_content(self, content):
        wrappedcontent = html.load(self.url, id_='content', error=self.error,
                                   success=self.success)
        return super(ExternalTab, self).build_html_content(wrappedcontent)

    def write_html(self, **kwargs):
        """Write the HTML page for this tab.

        See Also
        --------
        gwsumm.tabs.Tab.write_html : for details of all valid keyword
        arguments
        """
        if not kwargs.pop('writehtml', True):
            return
        link = html.markup.given_oneliner.a('click here to view the original',
                                            class_='reference',
                                            href=self.url.split()[0])
        kwargs.setdefault('footer', 'This page contains data from an external '
                                    'source, %s.' % link)
        return super(ExternalTab, self).write_html('', **kwargs)

register_tab(ExternalTab)


class ArchivedExternalTab(SummaryArchiveMixin, ExternalTab):
    """An archivable externally-linked tab.
    """
    type = 'archived-external'

    def __init__(self, name, url, start, end, mode=None, **kwargs):
        super(ArchivedExternalTab, self).__init__(name, url, **kwargs)
        self.span = (start, end)
        self.mode = mode

register_tab(ArchivedExternalTab)


class PlotTab(Tab):
    """A simple tab to layout some figures in the #main div.

    Parameters
    ----------
    name : `str`
        name of this tab (required)
    plots : `list`, optional
        list of plots to display on this tab. More plots can be added
        at any time via :meth:`PlotTab.add_plot`
    layout : `int`, `list`, optional
        the number of plots to display in each row, or a list of numbers
        to define each row individually. If the number of plots defined
        by the layout is less than the total number of plots, the layout
        for the final row will be repeated as necessary.

        For example ``layout=[1, 2, 3]`` will display a single plot on
        the top row, two plots on the second, and 3 plots on each row
        thereafter.
    foreword : `~gwsumm.html.markup.page`, `str`, optional
        content to include in the #main HTML before the plots
    afterword : `~gwsumm.html.markup.page`, `str`, optional
        content to include in the #main HTML after the plots
    index : `str`, optional
        HTML file in which to write. By default each tab is written to
        an index.html file in its own directory. Use :attr:`~Tab.index`
        to find out the default index, if not given.
    shortname : `str`, optional
        shorter name for this tab to use in the navigation bar. By
        default the regular name is used
    parent : :class:`~gwsumm.tabs.Tab`, optional
        parent of this tab. This is used to position this tab in the
        navigation bar.
    children : `list`, optional
        list of child :class:`Tabs <~gwsumm.tabs.Tab>` of this one. This
        is used to position this tab in the navigation bar.
    group : `str`, optional
        name of containing group for this tab in the navigation bar
        dropdown menu. This is only relevant if this tab has a parent.
    path : `str`, optional,
        base output directory for this tab (should be the same directory
        for all tabs in this run).
    """
    type = 'plots'

    def __init__(self, name, plots=list(), layout=None, foreword=None,
                 afterword=None, **kwargs):
        """Initialise a new :class:`PlotTab`.
        """
        super(PlotTab, self).__init__(name, **kwargs)
        self.plots = []
        for p in plots:
            self.add_plot(p)
        self.layout = layout
        self.foreword = foreword
        self.afterword = afterword

    @property
    def layout(self):
        """List of how many plots to display on each row in the output.

        By default this is ``1`` if the tab contains only 1 or 3 plots,
        or ``2`` if otherwise.
        The final number given in the list will be repeated as necessary.

        :type: `list` of `ints <int>`
        """
        return self._layout

    @layout.setter
    def layout(self, l):
        if isinstance(l, (str, unicode)):
            l = eval(l)
        self._layout = l

    @property
    def foreword(self):
        """HTML content to be included before the plots
        """
        return self._pre

    @foreword.setter
    def foreword(self, content):
        if isinstance(content, html.markup.page) or content is None:
            self._pre = content
        else:
            self._pre = html.markup.page()
            if not str(content).startswith('<'):
                self._pre.p(str(content))
            else:
                self._pre.add(str(content))

    @property
    def afterword(self):
        """HTML content to be included after the plots
        """
        return self._post

    @afterword.setter
    def afterword(self, content):
        if isinstance(content, html.markup.page) or content is None:
            self._post = content
        else:
            self._post = html.markup.page()
            if not str(content).startswith('<'):
                self._post.p(str(content))
            else:
                self._post.add(str(content))

    @classmethod
    def from_ini(cls, cp, section, *args, **kwargs):
        """Define a new tab from a :class:`~gwsumm.config.GWConfigParser`

        Parameters
        ----------
        cp : :class:`~ConfigParser.GWConfigParser`
            customised configuration parser containing given section
        section : `str`
            name of section to parse

        Returns
        -------
        tab : `PlotTab`
            a new tab defined from the configuration
        """
        cp = GWSummConfigParser.from_configparser(cp)

        kwargs.setdefault('path', '')

        # get layout
        if cp.has_option(section, 'layout'):
            try:
                layout = eval(cp.get(section, 'layout'))
            except NameError:
                raise ValueError("Cannot parse 'layout' for '%s' tab. Layout "
                                 "should be given as a comma-separated list "
                                 "of integers")
            if isinstance(layout, int):
                layout = [layout]
            for l in layout:
                if isinstance(l, (tuple, list)):
                    l = l[0]
                if l > 12:
                    raise ValueError("Cannot print more than 12 plots in a "
                                     "single row. The chosen layout value for "
                                     "each row must be a divisor of 12 to fit "
                                     "the Bootstrap scaffolding. For details "
                                     "see http://getbootstrap.com/2.3.2/"
                                     "scaffolding.html")
        else:
            layout = None
        kwargs.setdefault('layout', layout)

        # get plots
        try:
            kwargs.setdefault(
                'plots', zip(*sorted([(int(opt), url) for (opt, url) in
                                      cp.nditems(section) if opt.isdigit()],
                                     key=lambda a: a[0]))[1])
        except IndexError:
            pass

        # get content
        try:
            kwargs.setdefault('foreword', cp.get(section, 'foreword'))
        except NoOptionError:
            pass
        try:
            kwargs.setdefault('afterword', cp.get(section, 'afterword'))
        except NoOptionError:
            pass

        # build and return tab
        return super(PlotTab, cls).from_ini(cp, section, *args, **kwargs)

    def add_plot(self, plot):
        """Add a plot to this tab.

        Parameters
        ----------
        plot : `str`, :class:`~gwsumm.plot.SummaryPlot`
            either the URL of a plot to embed, or a formatted `SummaryPlot`
            object.
        """
        if isinstance(plot, str):
            plot = SummaryPlot(href=plot)
            plot.new = False
        if not isinstance(plot, SummaryPlot):
            raise TypeError("Cannot append plot of type %r" % type(plot))
        self.plots.append(plot)

    def scaffold_plots(self, plots=None, state=None, layout=None,
                       aclass='fancybox plot', **fancyboxargs):
        """Build a grid of plots using bootstrap's scaffolding.

        Returns
        -------
        page : :class:`~gwsumm.html.markup.page`
            formatted markup with grid of plots
        """
        page = html.markup.page()
        page.div(class_='scaffold well')

        if plots is None:
            if state:
                plots = [p for p in self.plots if not isinstance(p, DataPlot) or
                         p.state in [state, None]]
            else:
                plots = self.plots

        # get layout
        if layout is None:
            if self.layout:
                layout = list(self.layout)
            else:
                layout = len(plots) == 1 and [1] or [2]
        for i, l in enumerate(layout):
            if isinstance(l, (list, tuple)):
                layout[i] = l
            elif isinstance(l, int):
                layout[i] = (l, None)
            else:
                raise ValueError("Cannot parse layout element '%s'." % l)
        while sum(zip(*layout)[0]) < len(plots):
            layout.append(layout[-1])
        l = i = 0
        fancyboxargs.setdefault('data-fancybox-group', 1)

        for j, plot in enumerate(plots):
            # start new row
            if i == 0:
                page.div(class_='row')
            # determine relative size
            if layout[l][1]:
                colwidth = 12 // int(layout[l][1])
                remainder = 12 - colwidth * layout[l][0]
                if remainder % 2:
                    raise ValueError("Cannot center column of width %d in a "
                                     "12-column format" % colwidth)
                else:
                    offset = remainder / 2
                page.div(class_='col-md-%d col-md-offset-%d'
                                % (colwidth, offset))
            else:
                colwidth = 12 // int(layout[l][0])
                page.div(class_='col-md-%d' % colwidth)
            if plot.src.endswith('svg'):
                fbkw = fancyboxargs.copy()
                fbkw['data-fancybox-type'] = 'iframe'
                page.a(href='%s?iframe' % plot.href.replace('.svg', '.html'),
                       class_=aclass, **fbkw)
            else:
                page.a(href=plot.href, class_=aclass, **fancyboxargs)
            if plot.src.endswith('.pdf'):
                page.img(src=plot.src.replace('.pdf', '.png'))
            else:
                page.img(src=plot.src)
            page.a.close()
            page.div.close()
            # detect end of row
            if (i + 1) == layout[l][0]:
                i = 0
                l += 1
                page.div.close()
            # detect last plot
            elif j == (len(plots) - 1):
                page.div.close()
                break
            # or move to next column
            else:
                i += 1

        page.div.close()
        return page

    def build_html_content(self, content):
        page = html.markup.page()
        if self.foreword:
            page.add(str(self.foreword))
        if content:
            page.add(str(content))
        page.add(str(self.scaffold_plots()))
        if self.afterword:
            page.add(str(self.afterword))
        return Tab.build_html_content(str(page))

    def write_html(self, foreword=None, afterword=None, **kwargs):
        """Write the HTML page for this tab.

        Parameters
        ----------
        foreword : `str`, :class:`~gwsumm.html.markup.page`, optional
            content to place above the plot grid, defaults to
            :attr:`PlotTab.foreword`
        afterword : `str`, :class:`~gwsumm.html.markup.page`, optional
            content to place below the plot grid, defaults to
            :attr:`PlotTab.afterword`
        **kwargs
            other keyword arguments to be passed through
            :meth:`~Tab.write_html`

        See Also
        --------
        gwsumm.tabs.Tab.write_html : for details of all valid unnamed
                                     keyword arguments
        """
        if not kwargs.pop('writehtml', True):
            return
        if foreword is not None:
            self.foreword = foreword
        if afterword is not None:
            self.afterword = self.afterword
        return super(PlotTab, self).write_html(None, **kwargs)

register_tab(PlotTab)


class ArchivedPlotTab(SummaryArchiveMixin, PlotTab):

    """An archivable tab with multiple plots to be laid out in a scaffold.
    """
    type = 'archived-plots'

    def __init__(self, name, start, end, mode=None, plots=list(), **kwargs):
        super(ArchivedPlotTab, self).__init__(name, plots=plots, **kwargs)
        self.span = (start, end)
        self.mode = mode

register_tab(ArchivedPlotTab)


class StateTab(PlotTab):
    """Tab with multiple content pages defined via 'states'

    Each state is printed to its own HTML file which is loaded via
    javascript upon request into the #main div of the index for the tab.

    Parameters
    ----------
    name : `str`
        name of this tab (required)
    states : `list`
        a list of states for this tab. Each state can take any form,
        but must be castable to a `str` in order to be printed.
    plots : `list`
        list of plots to display on this tab. More plots can be added
        at any time via :meth:`PlotTab.add_plot`
    layout : `int`, `list`
        the number of plots to display in each row, or a list of numbers
        to define each row individually. If the number of plots defined
        by the layout is less than the total number of plots, the layout
        for the final row will be repeated as necessary.

        For example ``layout=[1, 2, 3]`` will display a single plot on
        the top row, two plots on the second, and 3 plots on each row
        thereafter.
    index : `str`
        HTML file in which to write. By default each tab is written to
        an index.html file in its own directory. Use :attr:`~Tab.index`
        to find out the default index, if not given.
    shortname : `str`
        shorter name for this tab to use in the navigation bar. By
        default the regular name is used
    parent : :class:`~gwsumm.tabs.Tab`
        parent of this tab. This is used to position this tab in the
        navigation bar.
    children : `list`
        list of child :class:`Tabs <~gwsumm.tabs.Tab>` of this one. This
        is used to position this tab in the navigation bar.
    group : `str`
        name of containing group for this tab in the navigation bar
        dropdown menu. This is only relevant if this tab has a parent.
    path : `str`
        base output directory for this tab (should be the same directory
        for all tabs in this run).
    """
    type = 'state'

    def __init__(self, name, states=list(), **kwargs):
        """Initialise a new `Tab`.
        """
        super(StateTab, self).__init__(name, **kwargs)
        # process states
        if not isinstance(states, (tuple, list)):
            states = [states]
        self.states = states

    # -------------------------------------------
    # StateTab properties

    @property
    def states(self):
        """The set of :class:`states <gwsumm.state.SummaryState>` over
        whos times this tab's data will be processed.

        The set of states will be linked in the given order with a switch
        on the far-right of the HTML navigation bar.
        """
        return self._states

    @states.setter
    def states(self, statelist):
        self._states = []
        for state in statelist:
            self.add_state(state)

    def add_state(self, state):
        """Add a `SummaryState` to this `StateTab`.

        Parameters
        ----------
        state : `str`, :class:`~gwsumm.state.SummaryState`
            either the name of a state, or a `SummaryState`.
        register : `bool`, default: `False`
            automatically register all new states
        """
        self._states.append(state)

    @property
    def frames(self):
        # write page for each state
        statelinks = []
        outdir = os.path.split(self.index)[0]
        for i, state in enumerate(self.states):
            statelinks.append(os.path.join(
                outdir, '%s.html' % re_cchar.sub('_', str(state).lower())))
        return statelinks

    # -------------------------------------------
    # StateTab methods

    @classmethod
    def from_ini(cls, cp, section, *args, **kwargs):
        # parse states and retrieve their definitions
        if cp.has_option(section, 'states'):
            # states listed individually
            kwargs.setdefault(
                'states', [re_quote.sub('', s).strip() for s in
                           cp.get(section, 'states').split(',')])
        else:
            # otherwise use 'all' state - full span with no gaps
            kwargs.setdefault('states', ['All'])
        # parse core Tab information
        return super(StateTab, cls).from_ini(cp, section, *args, **kwargs)

    # ------------------------------------------------------------------------
    # HTML methods

    def build_html_navbar(self, brand=None, ifo=None, ifomap=dict(),
                          tabs=list()):
        """Build the navigation bar for this `Tab`.

        The navigation bar will consist of a switch for this page linked
        to other interferometer servers, followed by the navbar brand,
        then the full dropdown-based navigation menus configured for the
        given ``tabs`` and their descendents.

        Parameters
        ----------
        brand : `str`, :class:`~gwsumm.html.markup.page`
            content for navbar-brand
        ifo : `str`, optional
            prefix for this IFO.
        ifomap : `dict`, optional
            `dict` of (ifo, {base url}) pairs to map to summary pages for
            other IFOs.

        tabs : `list`, optional
            list of parent tabs (each with a list of children) to include
            in the navigation bar.

        Returns
        -------
        page : `~gwsumm.html.markup.page`
            a markup page containing the navigation bar.
        """
        # ---- construct brand
        brand_ = html.markup.page()

        # build state switch
        if len(self.states) > 1 or str(self.states[0]) != ALLSTATE:
            brand_.add(str(html.state_switcher(
                zip(self.states, self.frames), 0)))
        # build interferometer cross-links
        if ifo is not None:
            brand_.add(str(html.base_map_dropdown(ifo, id_='ifos', **ifomap)))
            class_ = 'navbar navbar-fixed-top navbar-ifo'
        else:
            class_ = 'navbar navbar-fixed-top'
        # build HTML brand
        if isinstance(brand, html.markup.page):
            brand_.add(str(brand))
        elif brand:
            brand_.div(str(brand), class_='navbar-brand')

        # combine and return
        return html.navbar(self._build_nav_links(tabs), brand=brand_,
                           class_=class_,
                           dropdown_class=['hidden-xs visible-lg', 'hidden-lg'])

    @staticmethod
    def build_html_content(frame):
        """Build the #main div for this tab.

        In this construction, the <div id="id\_"> is empty, with a
        javascript hook to load the given frame into the div when ready.
        """
        wrappedcontent = html.load(frame, id_='content')
        return Tab.build_html_content(str(wrappedcontent))

    def write_state_html(self, state, pre=None, post=None, plots=True):
        """Write the frame HTML for the specific state of this tab

        Parameters
        ----------
        state : `~gwsumm.state.SummaryState`
            `SummaryState` over which to generate inner HTML
        """
        # build page
        page = html.markup.page()
        if pre:
            page.add(str(pre))
        if plots:
            page.add(str(self.scaffold_plots(state=state)))
        if post:
            page.add(str(post))
        # write to file
        idx = self.states.index(state)
        with open(self.frames[idx], 'w') as fobj:
            fobj.write(str(page))
        return self.frames[idx]

    def write_html(self, title=None, subtitle=None, tabs=list(), ifo=None,
                   ifomap=dict(), brand=None, css=html.CSS, js=html.JS,
                   about=None, footer=None, **inargs):
        """Write the HTML page for this state Tab.

        Parameters
        ----------
        maincontent : `str`, :class:`~gwsumm.html.markup.page`
            simple string content, or a structured `page` of markup to
            embed as the content of the #main div.
        title : `str`, optional, default: {parent.name}
            level 1 heading for this `Tab`.
        subtitle : `str`, optional, default: {self.name}
            level 2 heading for this `Tab`.
        tabs: `list`, optional
            list of top-level tabs (with children) to populate navbar
        ifo : `str`, optional
            prefix for this IFO.
        ifomap : `dict`, optional
            `dict` of (ifo, {base url}) pairs to map to summary pages for
            other IFOs.
        brand : `str`, :class:`~gwsumm.html.markup.page`, optional
            non-menu content for navigation bar, defaults to calendar
        css : `list`, optional
            list of resolvable URLs for CSS files. See `gwsumm.html.CSS` for
            the default list.
        js : `list`, optional
            list of resolvable URLs for javascript files. See
            `gwumm.html.JS` for the default list.
        about : `str`, optional
            href for the 'About' page
        footer : `str`, `~gwsumm.html.markup.page`
            user-defined content for the footer (placed below everything else)
        **inargs
            other keyword arguments to pass to the
            :meth:`~Tab.build_inner_html` method
        """
        return super(PlotTab, self).write_html(
            self.frames[0], title=title, subtitle=subtitle, tabs=tabs, ifo=ifo,
            ifomap=ifomap, brand=brand, css=css, js=js, about=about,
            footer=footer, **inargs)

register_tab(StateTab)


class ArchivedStateTab(SummaryArchiveMixin, StateTab):
    """An archivable tab with data in multiple states
    """
    type = 'archived-state'

    def __init__(self, name, start, end, mode=None, states=list(), **kwargs):
        super(ArchivedStateTab, self).__init__(name, states=states, **kwargs)
        self.span = (start, end)
        self.mode = mode

    @classmethod
    def from_ini(cls, config, section, start=None, end=None, **kwargs):
        config = GWSummConfigParser.from_configparser(config)
        if start is None:
            start = config.getint(section, 'gps-start-time')
        if end is None:
            end = config.getint(section, 'gps-end-time')
        return super(ArchivedStateTab, cls).from_ini(config, section, start,
                                                     end, **kwargs)

register_tab(ArchivedStateTab)


class AboutTab(SummaryArchiveMixin, Tab):
    type = 'about'

    def __init__(self, start, end, name='About', mode=None, **kwargs):
        super(AboutTab, self).__init__(name, **kwargs)
        self.span = (start, end)
        self.mode = mode

    def write_html(self, config=list(), **kwargs):
        return super(AboutTab, self).write_html(
            html.about_this_page(config=config), **kwargs)

register_tab(AboutTab)


class Error404Tab(SummaryArchiveMixin, Tab):
    type = '404'

    def __init__(self, start, end, name='404', mode=None, **kwargs):
        super(Error404Tab, self).__init__(name, **kwargs)
        self.span = (start, end)
        self.mode = mode

    def write_html(self, config=list(), top=None, **kwargs):
        if top is None:
            top = kwargs.get('base', self.path)
        kwargs.setdefault('title', '404: Page not found')
        page = html.markup.page()
        page.div(class_='alert alert-danger')
        page.p()
        page.strong("The page you are looking for doesn't exist")
        page.p.close()
        page.p("This could be because the times for which you are looking "
               "were never processed (or haven't even happened yet), or "
               "because no page exists for the specific data products you "
               "want. Either way, if you think this is in error, please "
               "contact <a class=\"alert-link\" "
               "href=\"mailto:detchar+code@ligo.org\">the DetChar group</a>.")
        page.p("Otherwise, you might be interested in one of the following:")
        page.div(style="padding-top: 10px;")
        page.a("Take me back", role="button", class_="btn btn-lg btn-info",
               title="Back", href="javascript:history.back()")
        page.a("Take me up one level", role="button",
               class_="btn btn-lg btn-warning", title="Up",
               href="javascript:linkUp()")
        page.a("Take me to the top level", role="button",
               class_="btn btn-lg btn-success", title="Top", href=top)
        page.div.close()
        page.div.close()
        page.script("""
  function linkUp() {
    var url = window.location.href;
    if (url.substr(-1) == '/') url = url.substr(0, url.length - 2);
    url = url.split('/');
    url.pop();
    window.location = url.join('/');
  }""", type="text/javascript")
        return super(Error404Tab, self).write_html(page, **kwargs)

register_tab(Error404Tab)
