#!/usr/bin/env python3

import PySimpleGUI as sg
import os.path
from pathlib import Path, PurePosixPath

def pathResolver(infiles, outfile):
    infilesList = infiles.split(';')
    for element in infilesList:
        element = Path(element).absolute()
    outfile = Path(outfile).absolute()
    return [infilesList, outfile]

def process(infiles, outfile):
    pass
    print(infiles, outfile)

# ---------------

def main():
    layout = [
        [
            sg.Text("Select input file(s):", size=(15, 1)),
            sg.In(size=(25, 1), enable_events=True, key="-FILE-"),
            sg.FilesBrowse(file_types = (
                            ('PDF, PNG or JPG/JPEG', '*.pdf *.png *.jpg *. jpeg'),
                            ('PDF', '*.pdf'),
                            ('PNG', '*.png'),
                            ('JPG', '*.jpg'),
                            ('JPEG', '*.jpeg'),),
                            size=(10, 1)),
        ],
        [
            sg.Text("Select output file:", size=(15, 1)),
            sg.In(size=(25, 1), enable_events=True, key="-OUTFILE-"),
            sg.FileSaveAs(file_types = (('Text Document', '*.txt'),), size=(10, 1)),
        ],
        [sg.Button("START PROCESSING")],
    ]

    window = sg.Window("Simple Gui OCR", layout)

    infiles = "";
    outfile = "";

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "-FILE-":
            infiles = values["-FILE-"]
            print(infiles)
        if event == "-OUTFILE-":
            outfile = values["-OUTFILE-"]
            print(outfile)
        if event == "START PROCESSING":
            print(infiles, outfile)
            if infiles == "" and outfile == "":
                sg.Popup('Please provide input file(s) and an output file!')
            elif infiles == "":
                sg.Popup('Please provide input file(s)!')
            elif outfile == "":
                sg.Popup('Please provide an output file!')
            else:
                print("hi")
                infiles, outfile = pathResolver(infiles, outfile)
                process(infiles, outfile)

    window.close()

if __name__ == '__main__':
    main()
