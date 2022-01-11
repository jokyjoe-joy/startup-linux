#!/usr/bin/python3
"""
 
           .--.              .--.
          : (\ ". _......_ ." /) :
           '.    ` angry   `    .'
            /'   _   bear   _   `\
           /     0}      {0     \
          |       /      \       |
          |     /'        `\     |
           \   | .  .==.  . |   /
            '._ \.' \__/ './ _.'
            /  ``'._-''-_.'``  \
                    `--`
# # # Originally written by jokyjoe in 2021.
# # Ported to Linux by angrybear in 2022.
"""

import threading
import time
import logging
import sys
import os
import subprocess
#import ctypes # TODO: Apparently it is unused.
#from modules.finance_notify import _ as FinanceNotification
#from modules.camera import _ as CheckCamera
from modules.defi_check import _ as DefiCheck

# Global settings
# TODO: put these settings into a cfg file
# This is needed to be around >10, if the app is started on Windows startup,
# because e.g. win10toast notifications don't appear if Windows is not properly loaded.
TIME_TO_WAIT_BEFORE_START = 5
# Each function in this list will be started in a threading.Thread.
# The app doesn't wait for the thread to end, before starting the next one.
# If you are creating a new function / module, please pay attention to the following points:
# # # use the module 'logging' for logging, e.g.: logging.info()
# # # put all C++ dependencies in this file's CPP_DEPENDENCIES_PATH
FUNCTIONS_TO_START = [
    #FinanceNotification,
    #CheckCamera,
    DefiCheck,
]
# Used for logging, however modules can (and should) also use this.
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
CPP_DEPENDENCIES_PATH = os.path.dirname(os.path.abspath(__file__)) + '/modules/cpp'
APP_VERSION = "0.0.1"

# Logging settings
LOG_FORMAT = "%(asctime)s - %(levelname)s @ %(module)s: %(message)s"
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO, datefmt=DATE_FORMAT, filename='logs/startup.log', filemode='a')
def ErrorHandler(err_type, value, throwback):
    logging.error("Uncaught exception! Value: '%s'; Type: '%s'; Tb: '%s'", str(value), str(err_type), str(throwback))

# Install exception handler
# TODO: Exception handler doesn't work in imported modules.
sys.excepthook = ErrorHandler


def ShowHelp():
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    print("           .--.              .--.")
    print(r'          : (\ ". _......_ ." /) :')
    print("           '.    `         `    .'")
    print(r"            /'   _          _   `\      STARTUP v%s - by jokyjoe & angrybear" % APP_VERSION)
    print(r"           /     0}      {0     \       Modular cross-platform startup manager.")
    print(r"          |       /      \       |      Supports Python and C++ modules.")
    print(r"          |     /'        `\     |")
    print(r"           \   | .  .==.  . |   /")
    print(r"            '._ \.' \__/ './ _.'        Fortes fortuna adiuvat.")
    print("            /  ``'._-''-_.'``  \\")
    print("                    `--`")
    print("")
    print("Use --help or -h to see this list.")
    print("")
    print(" -d      --dev      Start the application with predefined development settings.")
    print(" -s      --start    Start the application with the defined settings in config.cfg.")

def BuildDependencies():
    for filename in os.listdir(CPP_DEPENDENCIES_PATH):
        # Should only compile .cpp files.
        if not filename.endswith(".cpp"): 
            continue

        filenameNoExtension = filename.split('.')[0]
        filenameNoExtensionPath = CPP_DEPENDENCIES_PATH + '/' + filenameNoExtension

        # Only compile if the .cpp has been modified since the last time compiling it.
        cppModifiedTime = os.path.getmtime("%s.cpp" % filenameNoExtensionPath)
        # TODO: Port this to Linux. WindowsError doesn't exist on it.
        dllModifiedTime = 0 # DEBUG.
        #try:
        #    dllModifiedTime = os.path.getmtime("%s.dll" % filenameNoExtensionPath)
        #except WindowsError:
        #    # dll not found
        #    dllModifiedTime = 0

        isCppSinceModified = (dllModifiedTime - cppModifiedTime) < 0
        if not isCppSinceModified: 
            continue
        logging.info("%s.cpp has been modified since last compilation.", filenameNoExtension)

        # Compiling with g++, first into .o
        compileCommand = "g++ -c -o %s.o %s.cpp" % (filenameNoExtensionPath, filenameNoExtensionPath)
        logging.info("Running '%s'", compileCommand)
        if subprocess.call(compileCommand, shell=True) == 0:
            logging.info("Successfully compiled %s.cpp to %s.o", filenameNoExtension, filenameNoExtension)
        else:
            logging.error("Failed compiling %s.cpp to %s.o", filenameNoExtension, filenameNoExtension)

        # Afterwards, compiling .o to .dll
        compileCommand = "g++ -static -shared -o %s.dll %s.o -lgdi32" % (filenameNoExtensionPath, filenameNoExtensionPath)
        logging.info("Running '%s'", compileCommand)
        if subprocess.call(compileCommand, shell=True) == 0:
            logging.info("Successfully compiled %s.o to %s.dll", filenameNoExtension, filenameNoExtension)
        else:
            logging.error("Failed compiling %s.o to %s.dll", filenameNoExtension, filenameNoExtension)
        
        # Delete the remaining .o
        os.remove("%s.o" % filenameNoExtensionPath)
        
    logging.info("Finished building all the dependencies.")

if __name__ == '__main__':
    # Parse arguments
    if not sys.argv[1:]: 
        ShowHelp()
        exit()
    for arg in sys.argv[1:]:
        if arg == "-h" or arg == "--help": 
            ShowHelp()
            exit()
        elif arg == "-d" or arg == "--dev":
            logging.info("App started in development mode.")
            TIME_TO_WAIT_BEFORE_START = 1
        elif arg == "-s" or arg == "--start":
            continue
        # TODO: Specify log file path.
        # TODO: Start app by clearing log.
        else:
            print("Wrong argument given: %s" % arg)
            exit()

    # Wait for OS to load up before starting each module.
    logging.info("Waiting %i seconds for the OS to load.", TIME_TO_WAIT_BEFORE_START)
    time.sleep(TIME_TO_WAIT_BEFORE_START)
    
    #BuildDependencies() # TODO: Port to linux, g++ fails to compile since <windows.h> throws error.

    # Starting each module (function)
    try:
        threads = list()
        for index, functionToStart in enumerate(FUNCTIONS_TO_START, start=1):
            x = threading.Thread(target=functionToStart)
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()
    except KeyboardInterrupt:
        # TODO: Stop threads upon KeyboardInterrupt.
        """logging.info("Received KeyboardInterrupt: stopping threads cleanly ...")
        for index, thread in enumerate(threads):
            if thread.is_alive():
                thread._stop()"""

        exit()

    logging.info("All startup functions have ended: exiting ...")
