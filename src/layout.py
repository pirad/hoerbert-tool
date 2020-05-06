import PySimpleGUI as PySimpleGUI
import pathlib

NUMROWSSELECTION = 33

def __createTree(treedata):
    return PySimpleGUI.Tree(
        data=treedata,
        headings=[],
        auto_size_columns=True,
        num_rows=NUMROWSSELECTION,
        col0_width=60,
        key="-TREE-",
        show_expanded=False,
        enable_events=True,
        # size=(500,600),
        # select_mode= PySimpleGUI.TABLE_SELECT_MODE_EXTENDED,
        select_mode=PySimpleGUI.TABLE_SELECT_MODE_BROWSE,
    )

def __copy_sourceColumn(treedata):
    sourceFolderSelection = PySimpleGUI.FolderBrowse(
        "Select Source Directory",
        key="-copy-to-dir-sourceDirSelected-",
        enable_events=True,
        initial_folder=pathlib.Path.home() / "Musik",
    )
    sourceFolderTree = __createTree(treedata)
    return [
        [sourceFolderSelection],
        [sourceFolderTree],
    ]


def __copy_buttomColumn():
    return [
        [PySimpleGUI.Button(" > ", key="-copy-to-dir-addSelection-")],
        [PySimpleGUI.Button(" < ", key="-copy-to-dir-removeSelection-")],
        [PySimpleGUI.Button(" Rand ", key="-copy-to-dir-randomizeSelection-")],
    ]

def __targetDirSelections():
    select_folder = [
        PySimpleGUI.Radio(
            text=str(x),
            group_id="-copyToDir-select-",
            key="-copyToDir-select-" + str(x),
            enable_events=True,
            default=(x == 0),
        )
        for x in range(9)
    ]
    select_TargetDevice = PySimpleGUI.FolderBrowse(
        "Select Directory of Hoerbert SD-Card",
        key="-sddir-selected-",
        enable_events=True,
    )
    return [
        PySimpleGUI.Frame(
            "",
            [
                [
                    PySimpleGUI.Column([select_folder]),
                    PySimpleGUI.Column(layout=[], size=(70, 0)),
                    PySimpleGUI.Column([[select_TargetDevice]]),
                ],
            ],
        )
    ]

def createWindow(status):
    select_files = [
        PySimpleGUI.Frame(
            "",
            [
                [
                    PySimpleGUI.Column(__copy_sourceColumn(status.treeData)),
                    PySimpleGUI.Column(__copy_buttomColumn()),
                    PySimpleGUI.Column(
                        [
                            [
                                PySimpleGUI.Button(
                                    "Delete",
                                    key="-copy-to-dir-deleteCurrentDir",
                                    disabled=True,
                                )
                            ],
                            [
                                PySimpleGUI.Listbox(
                                    values=status.currentSelectedFiles,
                                    key="-copy-to-dir-selection-",
                                    size=(170, NUMROWSSELECTION),
                                ),
                            ],
                        ]
                    ),
                ]
            ],
        )
    ]
    button = PySimpleGUI.Button("Copy", key="-copyToDir-Copy-", disabled=True)
    infoButton = PySimpleGUI.Button("Info", key="-info-")
    layout = [__targetDirSelections(), select_files, [button ], 
        [PySimpleGUI.Column([], size=(1500,0)), PySimpleGUI.Column([[infoButton]])]
    ]
    return PySimpleGUI.Window("Hoerbert-Tool", layout, size=(1600, 900))
