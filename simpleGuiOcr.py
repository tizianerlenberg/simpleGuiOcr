#!/usr/bin/env python3

import PySimpleGUI as sg
import os
from pathlib import Path, PurePosixPath
from googletrans import Translator
import sys
import subprocess as sp
import random
import shutil
import threading
import PyPDF2

INSTALLPATH = Path(os.path.realpath(__file__)).absolute().parent
POPPLERPATH = (INSTALLPATH / 'misc' / 'poppler' / 'Library' / 'bin' / 'pdftoppm.exe').absolute()
TESSERACTPATH = (INSTALLPATH / 'misc' / 'Tesseract' / 'tesseract.exe').absolute()
TMPDIR = (Path(os.path.expanduser('~')) / 'AppData' / 'Local' / 'Temp').absolute()
STOPPED = False
COUNTER = 0
MAX_COUNTER = 100000
NUMBER_IMGS = 0
OPERATION = 'Waiting...'
TODELETE = ''

def setNumberImgs(infiles):
    global INSTALLPATH
    global POPPLERPATH
    global TESSERACTPATH
    global TMPDIR
    global STOPPED
    global COUNTER
    global MAX_COUNTER
    global NUMBER_IMGS
    
    global NUMBER_IMGS
    for filepath in infiles:
        if not (filepath.suffix == '.pdf'):
            NUMBER_IMGS = NUMBER_IMGS + 1
        else:
            with open(filepath, 'rb') as file:
                readpdf = PyPDF2.PdfFileReader(file)
                NUMBER_IMGS = NUMBER_IMGS + readpdf.numPages
            
def increaseCounter(inc=1):
    global INSTALLPATH
    global POPPLERPATH
    global TESSERACTPATH
    global TMPDIR
    global STOPPED
    global COUNTER
    global MAX_COUNTER
    global NUMBER_IMGS

    newCounter = COUNTER + int((MAX_COUNTER / NUMBER_IMGS)*inc)

    if newCounter >= MAX_COUNTER:
        return
    COUNTER = newCounter

def pathResolver(infiles, outfile):
    global INSTALLPATH
    global POPPLERPATH
    global TESSERACTPATH
    global TMPDIR
    global STOPPED
    global COUNTER
    global MAX_COUNTER
    global NUMBER_IMGS
    
    infilesList = infiles.split(';')
    infilesList2=[]
    for i, element in enumerate(infilesList):
        infilesList2.append(Path(element).absolute())
    outfile = Path(outfile).absolute()
    infilesList2.sort()
    return [infilesList2, outfile]

def truncateOp(text):
    if len(text) >= 25:
        return text[:22] + '...'
    else:
        return text

def doOcr(filePath, iLang, oLang, trans=False):
    global INSTALLPATH
    global POPPLERPATH
    global TESSERACTPATH
    global TMPDIR
    global STOPPED
    global COUNTER
    global MAX_COUNTER
    global NUMBER_IMGS
    global OPERATION
    global TODELETE
    
    tsseractLang=''
    if iLang == 'English':
        tesseractLang = 'eng'
    elif iLang == 'German':
        tesseractLang = 'deu'

    OPERATION = f'Processing "{truncateOp(filePath.name)}"'
    if not (filePath.suffix == '.pdf'):
        cmd = f'"{TESSERACTPATH}" -l "{tesseractLang}" "{filePath}" stdout'
        sess = sp.Popen(cmd,
                        shell=True,
                        stdout=sp.PIPE,
                        stderr=sp.PIPE)
        rc = sess.wait()
        out,err=sess.communicate()
        if trans:
            result = doTranslate(out.decode(), iLang, oLang)
            increaseCounter()
            return result
        else:
            result = out.decode()
            increaseCounter()
            return result
    else:
        result = ''
        
        tmpFile = TMPDIR / Path('simpleguiocr_' + str(int(random.random() * 10000000000000000)))
        os.makedirs(tmpFile)
        TODELETE = tmpFile
        tmpFileTemplate = tmpFile / 'img'
        pdfPageCount = 0

        with open(filePath, 'rb') as file:
            readpdf = PyPDF2.PdfFileReader(file)
            pdfPageCount = readpdf.numPages

        for i in range(pdfPageCount):
            OPERATION = f'Processing "{truncateOp(filePath.name)}", part 1, page {i+1}'
            cmd = f'"{POPPLERPATH}" -singlefile -f {i + 1} -r 72 -jpeg -jpegopt quality=90 "{filePath}" "{tmpFileTemplate}_{i}"'
            sp.check_call(cmd, shell=True)
            increaseCounter(0.2)
            if not threading.main_thread().is_alive():
                break

        listFiles = os.listdir(tmpFile)

        for i, img in enumerate(listFiles):
            OPERATION = f'Processing "{truncateOp(filePath.name)}", part 2, page {i+1}'
            imgPath = tmpFile / img
            cmd = f'"{TESSERACTPATH}" -l "{tesseractLang}" "{imgPath}" stdout'
            sess = sp.Popen(cmd,
                            shell=True,
                            stdout=sp.PIPE,
                            stderr=sp.PIPE)
            rc = sess.wait()
            out,err=sess.communicate()
            result = result + f'    ---------------- Page {i+1} ----------------\n\n'
            if trans:
                result = result + doTranslate(out.decode(), iLang, oLang) + '\n\n'
                increaseCounter(0.8)
            else:
                result = result + out.decode() + '\n\n'
                increaseCounter(0.8)
            if not threading.main_thread().is_alive():
                break
        
        shutil.rmtree(tmpFile)
        TODELETE = ''
        
        return result

def doTranslate(toTrans, iLang, oLang):
    global INSTALLPATH
    global POPPLERPATH
    global TESSERACTPATH
    global TMPDIR
    global STOPPED
    global COUNTER
    global MAX_COUNTER
    global NUMBER_IMGS
    
    def convLang(lang):
        if lang == 'English':
            return 'en'
        elif lang == 'German':
            return 'de'
    try:
        translator = Translator()
        oText = translator.translate(toTrans, src=convLang(iLang), dest=convLang(oLang)).text
    except:
        return 'TRANSLATION FAILED, THIS IS THE ORIGINAL TEXT:\n' + toTrans
    
    return oText

def process(infiles, outfile, iLang, oLang):
    global INSTALLPATH
    global POPPLERPATH
    global TESSERACTPATH
    global TMPDIR
    global STOPPED
    global COUNTER
    global MAX_COUNTER
    global NUMBER_IMGS

    setNumberImgs(infiles)
    
    with open(outfile, 'w') as file:
        file.write('')
    
    for item in infiles:
        outText = f'==================== {item.name} ====================\n\n'
        
        if not (iLang == oLang):
            outText = outText + doOcr(item, iLang, oLang, trans=True)
        else:
            outText = outText + doOcr(item, iLang, oLang)
        outText = outText + '\n\n'
        with open(outfile, 'a', encoding="utf-8") as file:
            file.write(outText)
        if not threading.main_thread().is_alive():
            break
    STOPPED = True

def testThr():
    global COUNTER
    import time
    while True:
        time.sleep(1)
        COUNTER = COUNTER + 10

# ---------------

def main():
    global INSTALLPATH
    global POPPLERPATH
    global TESSERACTPATH
    global TMPDIR
    global STOPPED
    global COUNTER
    global MAX_COUNTER
    global NUMBER_IMGS
    global OPERATION
    global TODELETE
    
    layout = [
        [
            sg.Text("Select input file(s):", size=(17, 1)),
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
            sg.Text("Select output file:", size=(17, 1)),
            sg.In(size=(25, 1), enable_events=True, key="-OUTFILE-"),
            sg.FileSaveAs(file_types = (('Text Document', '*.txt'),), size=(10, 1)),
        ],
        [
            sg.Text("Select input language:", size=(17, 1)),
            sg.Combo(['English', 'German'], 
                     default_value='English', 
                     s=(23,22), 
                     enable_events=True, 
                     readonly=True, 
                     k='-ILANG-')
        ],
        [
            sg.Text("Select output language:", size=(17, 1)),
            sg.Combo(['English', 'German'], 
                     default_value='English', 
                     s=(23,22), 
                     enable_events=True, 
                     readonly=True, 
                     k='-OLANG-')
        ],
        [
            sg.Text(size=(50, 1), key='operation')
        ],
        [
            sg.ProgressBar(MAX_COUNTER, orientation='h', size=(33, 20), key='progressbar')
        ],
        [
            sg.Button("START PROCESSING"),
            sg.Button("CANCEL"),
        ],
    ]

    window = sg.Window("Simple Gui OCR", layout, icon='icon.ico')

    infiles = "";
    outfile = "";
    iLang = "English"
    oLang = "English"
    started = False
    thr = None
    op=''

    while True:
        event, values = window.read(timeout=10)
        window['progressbar'].UpdateBar(COUNTER)
        if op != OPERATION:
            op = OPERATION
            window['operation'].update(op)
        if event == "Exit" or event == sg.WIN_CLOSED or event == "CANCEL":
            window['operation'].update('CLOSING, PLEASE WAIT')
            sys.exit()
        if event == "-FILE-":
            infiles = values["-FILE-"]
        if event == "-OUTFILE-":
            outfile = values["-OUTFILE-"]
        if event == "-ILANG-":
            iLang = values["-ILANG-"]
        if event == "-OLANG-":
            oLang = values["-OLANG-"]
        if event == "START PROCESSING":
            if infiles == "" and outfile == "":
                sg.Popup('Please provide input file(s) and an output file!')
            elif infiles == "":
                sg.Popup('Please provide input file(s)!')
            elif outfile == "":
                sg.Popup('Please provide an output file!')
            else:
                if not started:
                    infilesP, outfileP = pathResolver(infiles, outfile)
                    thr = threading.Thread(target=process, args=(infilesP, outfileP, iLang, oLang,))
                    thr.start()
                    started = True
        if STOPPED:
            thr.join()
            sg.Popup(f'SUCCESS: Output was saved to {outfile}')
            sys.exit(0)
            

    window.close()

if __name__ == '__main__':
    main()
