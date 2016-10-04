__author__ = 'skh'

import logging
import sys
import time

from gtrackcore.track.core.TrackView import TrackView
from gtrackcore.track.format.TrackFormat import TrackFormatReq
from gtrackcore.track.format.TrackFormat import TrackFormat

from gtrackcore.track_operations.operations.Operator import Operator
from gtrackcore.track_operations.TrackContents import TrackContents
from gtrackcore.track_operations.RawOperationContent import RawOperationContent
from gtrackcore.track_operations.utils.TrackHandling import \
    createTrackContentFromFile
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.track_operations.utils.TrackHandling import \
    createRawResultTrackView

from gtrackcore.track_operations.operations.Merge import Merge

from gtrackcore.track_operations.raw_operations.Expand import expand

class Expand(Operator):
    """
    Extends all of the segments in a track a given number of BP.
    """

    def __init__(self, *args, **kwargs):
        assert args[0] is not None
        self._kwargs = kwargs
        self._options = {'debug': False,
                         'allowOverlap': False,
                         'resultAllowOverlaps': False,
                         'both': None,
                         'start': None,
                         'end': None,
                         'useFraction': False,
                         'useStrands': True,
                         'treatMissingAsNegative': False
                         }
        # Save the tracks
        self._tracks = args[0]
        self._trackFormat = self._tracks.trackFormat

        # Core properties
        self._numTracks = 1
        self._resultIsTrack = True

        # Input need to be a none dense track
        self._trackRequirements = [TrackFormatReq(dense=False)]

        # TrackResultReq is always a segment type
        self._resultTrackRequirements = self._createTrackFormatReq()

        super(self.__class__, self).__init__(*args, **kwargs)

    def _createTrackFormatReq(self):
        """
        Creates the correct TrackFormatReq according to what kind of data we
        are filtering out.
        :return:
        """

        tr = self._trackFormat

        valued = tr.isValued()
        weighted = tr.isWeighted()
        if valued:
            valued = tr._val
        if weighted:
            weighted = tr._weights
        req = TrackFormatReq(dense=False, interval=True, linked=tr.isLinked(),
                             weights=weighted, val=valued,
                             strand=tr.hasStrand(),
                             allowOverlaps=self._resultAllowOverlaps)
        return req

    def _calculate(self, region, tv):

        # Remove RawOperationsContent
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = None

        if self._useStrands:
            strands = tv.strandsAsNumpyArray()
            if strands is None or strands.size == 0:
                # Track has no strand information, ignoring strands.
                strands = None
                self._useStrand = False

        # Get genome size.
        regionSize = len(region)

        ret = expand(regionSize, starts=starts, ends=ends, strands=strands,
                     start=self._start, end=self._end, both=self._both,
                     useFraction=self._useFraction,
                     useStrands=self._useStrands,
                     treatMissingAsNegative=self._treatMissingAsNegative,
                     debug=self._debug)

        # Returns start, ends, strands, index
        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4
            return createRawResultTrackView(ret[3], region, tv,
                                            self._resultAllowOverlap,
                                            newStarts=ret[0], newEnds=ret[1],
                                            newStrands=ret[2],
                                            trackFormatReq=self.resultTrackRequirements)
        else:
            return None

    def preCalculation(self, track):
        return track

    def postCalculation(self, track):
        if not self._resultAllowOverlap:
            # Overlap not allowed in the result. Using merge to remove it
            m = Merge(track, both=True, mergeValues=True,
                      useStrands=self._useStrands,
                      mergeLinks=True, allowOverlap=False)
            res = m.calculate()
            return res
        else:
            return track

    @classmethod
    def createSubParser(cls, subparsers):
        """
        Creates a subparser. Used by GTool
        :param subparsers:
        :return: None
        """
        parser = subparsers.add_parser('slop', help='Extends segments in a '
                                                    'track a nr of BP.')
        parser.add_argument('track', help='File path of track')
        parser.add_argument('genome', help='File path of Genome definition')
        parser.add_argument('-b', type=int, dest='both')
        parser.add_argument('-s', type=int, dest='start')
        parser.add_argument('-e', type=int, dest='end')
        parser.add_argument('--allowOverlap', action='store_true',
                            help="Allow overlap in the resulting track")
        parser.set_defaults(which='Slop')

    def printResult(self):
        pass