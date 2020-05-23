import PySimpleGUI as PySimpleGUI
import datetime
import pathlib
import natsort
import random
from functools import partial
from . import pathtools
from . import targetDevice
from . import layout

CUTTRACKSLONGERTHAN = datetime.timedelta(seconds=280)


def createTreeData(rootPath: pathlib.Path):
    treedata = PySimpleGUI.TreeData()
    return pathtools.fillTreeData(rootPath, treedata)


class windowStatus:
    def __init__(self):
        self.currentSelectedFiles = []
        self.targetDevicePath = ""
        self.targetDirectory = ""
        self.currentSelectedTargetDirNumber = "0"
        self.SDCardContent = {}
        self.treeData = createTreeData(pathlib.Path.home() / "Musik")
        self.updateTreeData = False
        self.listOfCopyJobs = []

    def __str__(self):
        return (
            "Target: "
            + str(self.targetDirectory)
            + "; List: "
            + str(self.currentSelectedFiles)
        )

    def update_onEventCalled(self, event, values):
        self.treeSelection = values["-TREE-"]
        if event == "-sddir-selected-":
            sDDir = pathlib.Path(values["-sddir-selected-"])
            if targetDevice.checkSDDir(sDDir):
                self.targetDevicePath = sDDir
                self.SDCardContent = targetDevice.readSDCardContent(sDDir)
            else:
                PySimpleGUI.popup(
                    "Directory unvalid, the expected subdirectories do not exist.",
                    title="Error",
                )
        self.currentSelectedTargetDirNumber = [
            x
            for x in values.keys()
            if (values[x] == True and x.startswith("-copyToDir-select-"))
        ][0][-1]
        if self.targetDevicePath:
            self.targetDirectory = self.targetDevicePath / (
                self.currentSelectedTargetDirNumber
            )
        if event == "-copy-to-dir-addSelection-":
            self.__update_onAddSelection(values)
        if event == "-copy-to-dir-removeSelection-":
            self.__update_onRemoveSelection(values)
        if event == "-copy-to-dir-randomizeSelection-":
            self.__update_onRandomizeSelection()
        if event == "-copy-to-dir-deleteCurrentDir":
            if self.targetDevicePath:
                for f in self.targetDirectory.iterdir():
                    f.unlink()
                self.SDCardContent[self.currentSelectedTargetDirNumber] = {}
                self.currentSelectedFiles.clear()
        if event == "-copy-to-dir-sourceDirSelected-":
            self.treeData = createTreeData(
                pathlib.Path(values["-copy-to-dir-sourceDirSelected-"])
            )
            self.updateTreeData = True
        if event == "-copyToDir-Copy-":
            self.__startCopyProcess()
        if event == "-info-":
            PySimpleGUI.popup(
"""Written by Konrad Kaffka
I did this to learn something
Using python, PySimpleGUI, sox, and other free open source software
Folder Icon by https://www.iconfinder.com/andhikairfani
""",
                title="Hörbert Tool",
            )


    def readyForCopy(self):
        return (
            issubclass(type(self.targetDirectory), pathlib.Path)
            and self.currentSelectedFiles
        )

    def __startCopyProcess(self):
        createCopyInformation = partial(
            targetDevice.InformationForCopy,
            targetDirectory=self.targetDirectory,
            options={},
        )
        copyInformationList = list()
        i = 0
        for file in self.currentSelectedFiles:
            runTime = pathtools.playTime(file)
            cutInto = int(runTime / CUTTRACKSLONGERTHAN)
            if cutInto > 1:
                length = runTime / cutInto
                for j in range(cutInto):
                    copyInformationList.append(
                        createCopyInformation(
                            file=file,
                            index=i,
                            startsecond=(j * length).total_seconds(),
                            endsecond=((j + 1) * length).total_seconds(),
                        )
                    )
                    i += 1
            else:
                copyInformationList.append(createCopyInformation(file=file, index=i))
                i += 1
        self.listOfCopyJobs.append(targetDevice.startProcessing(copyInformationList))
        self.SDCardContent[self.currentSelectedTargetDirNumber] = {"*": "Copying"}
        self.currentSelectedFiles = []

    def __update_onRemoveSelection(self, values):
        for entry in values["-copy-to-dir-selection-"]:
            for file in self.currentSelectedFiles:
                if file.endswith(entry):
                    self.currentSelectedFiles.remove(file)
                    break

    def __update_onAddSelection(self, values):
        selectionToAdd = values["-TREE-"]
        if len(selectionToAdd) == 1 and pathlib.Path(selectionToAdd[0]).is_dir():
            for f in natsort.natsorted(pathlib.Path(selectionToAdd[0]).iterdir()):
                if f.is_file():
                    self.currentSelectedFiles.append(str(f))
        else:
            self.currentSelectedFiles += selectionToAdd

    def __update_onRandomizeSelection(self):
        random.shuffle(self.currentSelectedFiles)

    def __formatSelectedFilesForView(self):
        return pathtools.formatSelectionForView(self.currentSelectedFiles)

    def __createFilesToCopyList(self):
        if (
            self.targetDevicePath
            and self.currentSelectedTargetDirNumber in self.SDCardContent
        ):
            return (
                list(self.SDCardContent[self.currentSelectedTargetDirNumber].values())
                + ["---------------------------------"]
                + self.__formatSelectedFilesForView()
            )
        else:
            return self.__formatSelectedFilesForView()

    def __deletePossible(self):
        return (
            self.currentSelectedTargetDirNumber in self.SDCardContent
            and self.SDCardContent[self.currentSelectedTargetDirNumber]
        ) or self.currentSelectedFiles

    def updateWindow(self, window):
        window["-copy-to-dir-selection-"].update(values=self.__createFilesToCopyList())
        window["-copyToDir-Copy-"].update(disabled=not self.readyForCopy())
        window["-copy-to-dir-deleteCurrentDir"].update(
            disabled=not self.__deletePossible()
        )
        if self.treeSelection and pathlib.Path(self.treeSelection[0]).is_dir():
            window[
                "-copy-to-dir-sourceDirSelected-"
            ].InitialFolder = self.treeSelection[0]
        if self.updateTreeData:
            window["-TREE-"].update(self.treeData)
            self.updateTreeData = False


def __handleEvent(event, values, window, status):
    print(event, values)
    if event is None:
        return False
    status.update_onEventCalled(event, values)
    status.updateWindow(window)
    return True


def main():

    status = windowStatus()

    window = layout.createWindow(status)
    while True:
        event, values = window.read()
        if not __handleEvent(event, values, window, status):
            break

    for j in status.listOfCopyJobs:
        j.wait()
    window.close()
