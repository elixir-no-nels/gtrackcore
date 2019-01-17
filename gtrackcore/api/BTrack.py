from gtrackcore.extract.TrackExtractor import TrackExtractor
from gtrackcore.track_operations.Genome import Genome
from gtrackcore.core.Api import _convertTrackName
import os

from gtrackcore.track_operations.utils.TrackHandling import extractTrackFromGTrackCore
from gtrackcore.util.CommonFunctions import ensurePathExists
import shutil
from gtrackcore.preprocess.PreProcessTracksJob import PreProcessExternalTrackJob


class BTrack(object):
    def __init__(self, path, genomePath = ''):
        self._path = os.path.abspath(path)

        self._genome = Genome.createFromTabular(genomePath, os.path.basename(genomePath))
        self._trackContents = []

        newGenomePath = os.path.join(self._path, 'genomes', os.path.basename(genomePath))
        ensurePathExists(newGenomePath)
        shutil.copy(genomePath, newGenomePath)

    def createTrackIdentifier(self, trackName):
        trackIdentifier = ['__btrack__'] + [os.path.join(self._path, 'tracks', self._genome.name)] + trackName

        return trackIdentifier


    def importTrackFromFile(self, filePath, trackName=''):
        if not trackName:
            trackName = os.path.basename(filePath)
        trackName = _convertTrackName(trackName)
        print trackName

        trackIdentifier = self.createTrackIdentifier(trackName)
        PreProcessExternalTrackJob(self._genome, filePath, trackIdentifier, os.path.splitext(filePath)[1][1:]).process()

        trackContents = extractTrackFromGTrackCore(self._genome, trackIdentifier)

        self._trackContents.append(TrackContentsWrapper(trackIdentifier, trackContents))

        return trackContents

    def importTrack(self, trackContents, trackName):
        trackIdentifier = self.createTrackIdentifier(trackName)

        trackContents.save(trackIdentifier)
        self._trackContents.append(TrackContentsWrapper(trackIdentifier, trackContents))

    def exportTrackToFile(self, trackContents, path):
        for tc in self._trackContents:
            if tc.getTrackContents == trackContents:
                trackIdentifier = tc.getTrackId

        fileFormat = os.path.splitext(path)[1][1:]

        TrackExtractor.extractOneTrackManyRegsToOneFile(trackIdentifier, trackContents.regions, path,
                                                        fileSuffix=fileFormat, globalCoords=True)


class TrackContentsWrapper(object):
    def __init__(self, trackIdentifier, trackContents):
        self._trackIdentifier = trackIdentifier
        self._trackContents = trackContents

    def getTrackId(self):
        return self._trackIdentifier

    def getTrackName(self):
        trackName = self._trackIdentifier[2:]

    def getTrackContents(self):
        return self._trackContents

    #def exportTrackToFile(self, track, exportPath):


