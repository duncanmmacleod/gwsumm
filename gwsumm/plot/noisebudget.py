# -*- coding: utf-8 -*-
# Copyright (C) Duncan Macleod (2017)
#
# This file is part of GWSumm.
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
# along with GWSumm.  If not, see <http://www.gnu.org/licenses/>.

"""Extensions to the spectrum plot for noise budgets
"""

from __future__ import division

import re

import numpy

from gwpy.plotter import FrequencySeriesPlot
from gwpy.plotter.tex import label_to_latex
from gwpy.segments import SegmentList

from ..data import get_spectrum
from .registry import (get_plot, register_plot)

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


class NoiseBudgetPlot(get_plot('spectrum')):
    """Plot of a noise budget ASD
    """
    type = 'noise-budget'
    data = 'spectrum'
    defaults = {'logx': True,
                'logy': True,
                'format': 'asd',
                'sum-label': 'Sum of noises',
                'sum-linestyle': '--',
                'sum-color': 'black'}

    def parse_sum_params(self, **defaults):
        sumargs = defaults.copy()
        for key in self.pargs.keys():
            if re.match('sum[-_]', key):
                sumargs[key[4:]] = self.pargs.pop(key)
        return sumargs

    def _draw(self):
        """Load all data, and generate this `SpectrumDataPlot`
        """
        plot = self.plot = FrequencySeriesPlot(
            figsize=self.pargs.pop('figsize', [12, 6]))
        ax = plot.gca()
        ax.grid(b=True, axis='both', which='both')

        if self.state:
            self.pargs.setdefault(
                'suptitle',
                '[%s-%s, state: %s]' % (self.span[0], self.span[1],
                                        label_to_latex(str(self.state))))
        suptitle = self.pargs.pop('suptitle', None)
        if suptitle:
            plot.suptitle(suptitle, y=0.993, va='top')

        # get spectrum format: 'amplitude' or 'power'
        sdform = self.pargs.pop('format')

        # parse plotting arguments
        plotargs = self.parse_plot_kwargs()
        legendargs = self.parse_legend_kwargs()

        # add data
        sumdata = []
        for i, (channel, pargs) in enumerate(zip(self.channels, plotargs)):
            if self.state and not self.all_data:
                valid = self.state
            else:
                valid = SegmentList([self.span])

            data = get_spectrum(str(channel), valid, query=False,
                                format=sdform, method=None)[0]
            if i:
                sumdata.append(data)

            # anticipate log problems
            if self.pargs['logx']:
                data = data[1:]
            if self.pargs['logy']:
                data.value[data.value == 0] = 1e-100

            pargs.setdefault('zorder', -i)
            ax.plot_frequencyseries(data, **pargs)

        # assert all noise terms have the same resolution
        if any([x.dx != sumdata[0].dx for x in sumdata]):
            raise RuntimeError("Noise components have different resolutions, "
                               "cannot construct sum of noises")
        # reshape noises if required
        n = max(x.size for x in sumdata)
        for i, d in enumerate(sumdata):
            if d.size < n:
                sumdata[i] = numpy.require(d, requirements=['O'])
                sumdata[i].resize((n,))

        # plot sum of noises
        sumargs = self.parse_sum_params()
        sum_ = sumdata[0] ** 2
        for d in sumdata[1:]:
            sum_ += d ** 2
        sum_ **= (1/2.)
        ax.plot_frequencyseries(sum_, zorder=1, **sumargs)
        ax.lines.insert(1, ax.lines.pop(-1))

        self.apply_parameters(ax, **self.pargs)
        plot.add_legend(ax=ax, **legendargs)
        plot.add_colorbar(ax=ax, visible=False)

        return self.finalize()

register_plot(NoiseBudgetPlot)


class RelativeNoiseBudgetPlot(get_plot('spectrum')):
    """Spectrum plot for a `SummaryTab`
    """
    type = 'noise-budget-ratio'
    data = 'spectrum'
    defaults = {'logx': True,
                'logy': True,
                'format': 'asd'}

    def _draw(self):
        """Load all data, and generate this `SpectrumDataPlot`
        """
        plot = self.plot = FrequencySeriesPlot(
            figsize=self.pargs.pop('figsize', [12, 6]))
        ax = plot.gca()
        ax.grid(b=True, axis='both', which='both')

        if self.state:
            self.pargs.setdefault(
                'suptitle',
                '[%s-%s, state: %s]' % (self.span[0], self.span[1],
                                        label_to_latex(str(self.state))))
        suptitle = self.pargs.pop('suptitle', None)
        if suptitle:
            plot.suptitle(suptitle, y=0.993, va='top')

        # get spectrum format: 'amplitude' or 'power'
        sdform = self.pargs.pop('format')

        # parse plotting arguments
        plotargs = self.parse_plot_kwargs()[0]

        # add data
        sumdata = []
        for i, channel in enumerate(self.channels):
            if self.state and not self.all_data:
                valid = self.state
            else:
                valid = SegmentList([self.span])

            data = get_spectrum(str(channel), valid, query=False,
                                format=sdform, method=None)[0]
            if i:
                sumdata.append(data)
            else:
                target = data

        # assert all noise terms have the same resolution
        if any([x.dx != target.dx for x in sumdata]):
            raise RuntimeError("Noise components have different resolutions, "
                               "cannot construct sum of noises")
        # reshape noises if required
        n = target.size
        for i, d in enumerate(sumdata):
            if d.size < n:
                sumdata[i] = numpy.require(d, requirements=['O'])
                sumdata[i].resize((n,))

        # calculate sum of noises
        sum_ = sumdata[0] ** 2
        for d in sumdata[1:]:
            sum_ += d ** 2
        sum_ **= (1/2.)

        # plot ratio of h(t) to sum of noises
        relative = sum_ / target
        ax.plot_frequencyseries(relative, **plotargs)

        # finalize plot
        self.apply_parameters(ax, **self.pargs)
        plot.add_colorbar(ax=ax, visible=False)

        return self.finalize()

register_plot(RelativeNoiseBudgetPlot)
