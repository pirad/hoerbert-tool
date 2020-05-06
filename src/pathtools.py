import datetime
import pathlib
import natsort
import typing
import sox
from . import resources


def __tree_insertWarning(treedata, dirname):
    treedata.Insert(
        str(dirname),
        str(dirname) + "//Error//",
        "Too much elements, please select a better folder",
        values=[],
    )  # icon warning


def __tree_insertDir(treedata, parentkey, dir):
    treedata.Insert(
        parentkey, str(dir), dir.name, values=[], icon=resources.folder_icon,
    )


def __tree_insertFile(treedata, parentkey, file):
    treedata.Insert(
        parentkey, str(file), file.name, values=[], icon=resources.file_icon,
    )


def __tree_insert(treedata, parentkey, current):
    if current.is_dir():
        __tree_insertDir(treedata, parentkey, current)
        return [current]
    else:
        __tree_insertFile(treedata, parentkey, current)
        return []


def fillTreeData(rootPath: pathlib.Path, treedata):
    remainingDirs = [rootPath]
    rootDir = True
    while remainingDirs:
        dirname = remainingDirs.pop(0)
        parentkey = str(dirname)
        if rootDir:
            parentkey = ""
            rootDir = False
        if len(treedata.tree_dict) > 3000:
            __tree_insertWarning(treedata, dirname)
        else:
            for f in natsort.natsorted(dirname.iterdir()):
                remainingDirs += __tree_insert(treedata, parentkey, f)
    return treedata


def ___identifyCommonBeginning(listOfPaths):
    currentMatch = listOfPaths[0]
    for new in listOfPaths[1:]:
        for i in range(len(currentMatch)):
            if new[i] != currentMatch[i]:
                currentMatch = currentMatch[: i - 1]
                break
    return currentMatch


StringList = typing.List[str]

playTimeCache = {}


def playTime(file: str):
    def __readPlayTime(file):

        return datetime.timedelta(seconds=int(sox.file_info.duration(file)))

    if file not in playTimeCache:
        if len(playTimeCache) > 3000:
            playTimeCache.clear()
        playTimeCache[file] = __readPlayTime(file)
    return playTimeCache[file]


def __formatTime(time: datetime.timedelta):
    return str(time).ljust(9)


def __shortenPaths(listOfPaths: StringList):
    if len(listOfPaths) > 1:
        commonBeginning = ___identifyCommonBeginning(listOfPaths)
        result = []
        for entry in listOfPaths:
            result.append(entry[len(commonBeginning) + 1 :])
        return result
    elif len(listOfPaths) == 1:
        return [pathlib.Path(listOfPaths[0]).name]
    else:
        return []


def formatSelectionForView(listOfPaths: StringList):
    shortened = __shortenPaths(listOfPaths)
    return [
        __formatTime(playTime(listOfPaths[i])) + "   |   " + shortened[i]
        for i in range(len(listOfPaths))
    ]
