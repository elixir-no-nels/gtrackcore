from gtrackcore.track.pytables.DatabaseTrackHandler import DatabaseTrackHandler
from gtrackcore.track.pytables.TrackColumnWrapper import TrackColumnWrapper

class TrackData(dict):
    def __init__(self, other=None):
        if other is not None:
            dict.__init__(self, other)
        else:
            dict.__init__(self)

class TrackSource:
    def __init__(self):
        self._chrInUse = None
        self._fileDict = {}

    def getTrackData(self, trackName, genome, chr, allowOverlaps, forceChrFolders=False):
        track_data = TrackData()

        db_handler = DatabaseTrackHandler(trackName, genome, allowOverlaps)
        db_handler.open(chr)
        column_names = db_handler.get_column_names()
        db_handler.close()

        for column in column_names:
            track_data[column] = TrackColumnWrapper(column, db_handler, chr)

        return track_data

