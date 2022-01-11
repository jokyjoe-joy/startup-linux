from decimal import DefaultContext
import cv2
import random
from binascii import b2a_hex
import os
import statistics
import time
import logging
from win10toast import ToastNotifier
import face_recognition
from deprecated import deprecated

# Global settings
DIRECTORY_FOR_DEPENDENCIES = os.path.dirname(os.path.abspath(__file__))
CAMERA_IMG_TEMPLATE_PATH = "%s\\camera_imgs" % DIRECTORY_FOR_DEPENDENCIES
# This many templates will be used for checking each frame.
AMOUNT_OF_TEMPLATES_TO_CHECK = 2
AMOUNT_OF_IMAGES_FOR_NEW_FACE = 50
AMOUNT_OF_FRAMES_TO_RECORD = 5
CONFIG_FILE_PATH = "%s\\config\\camera.cfg" % DIRECTORY_FOR_DEPENDENCIES
RECORDINGS_PATH = "%s\\recordings" % DIRECTORY_FOR_DEPENDENCIES

# Initializing some variables
IMAGE_TEMPLATE_FILES = []
CURRENT_FACE_NAME = ""

CASC_PATH = "%s\\haarcascades\\haarcascade_frontalface_default.xml" % DIRECTORY_FOR_DEPENDENCIES
faceCascade = cv2.CascadeClassifier(CASC_PATH)
toaster = ToastNotifier()

def GetRandomHex(length):
    return str(b2a_hex(os.urandom(int(length / 2)))).replace("b'",'').replace("'",'')

def SetFace(faceName):
    logging.info("Setting current face to '%s'.", faceName)
    if not os.path.isdir("%s\\%s" % (CAMERA_IMG_TEMPLATE_PATH, faceName)):
        logging.info("Couldn't set face as the given face doesn't exist.")
        return
    global IMAGE_TEMPLATE_FILES
    IMAGE_TEMPLATE_FILES = [f for f in os.listdir("%s\\%s" % (CAMERA_IMG_TEMPLATE_PATH, faceName)) if os.path.isfile(os.path.join("%s\\%s" % (CAMERA_IMG_TEMPLATE_PATH, faceName), f))]
    global CURRENT_FACE_NAME
    CURRENT_FACE_NAME = faceName

@deprecated
def DetectFace(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    #for (x, y, w, h) in faces:
    #    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)    
    
    # Crop image to face.
    if len(faces) == 1: face = faces[0]
    elif len(faces) > 1: face = random.choice(faces)
    else: return frame # TODO: no faces detected
    
    (x, y, w, h) = face
    frame = frame[y:y+h, x:x+w]
    
    return frame

"""
Returns a correlation between the given frame and a random image from the current face's imageset.
"""
@deprecated
def CheckFrame(frame):
    # Select new templates
    IMAGE_TEMPLATES = []
    for i in range(0,AMOUNT_OF_TEMPLATES_TO_CHECK):
        filename = "%s\\%s\\%s" % (CAMERA_IMG_TEMPLATE_PATH, CURRENT_FACE_NAME, random.choice(IMAGE_TEMPLATE_FILES))
        IMAGE_TEMPLATES.append(cv2.imread(filename))

    # Go through each template and get an average correlation to them.
    corr = 0
    for template in IMAGE_TEMPLATES:
        corr += cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)[0][0]
    corr /= len(IMAGE_TEMPLATES)
    return corr

"""
Returns the modified frame and a bool, whether the given frame and random images from the current face's imageset is a match.
Only returns true if all template images return a match with the given frame.
Returns "MULTIPLE" if there are multiple faces detected in the given frame.
Returns "NOFACE" if there are no faces detected in the given frame.
"""
def CompareFrameToTemplates(frame):
    # Select 2 new templates
    imageTemplateEncodings = []
    for i in range(0,AMOUNT_OF_TEMPLATES_TO_CHECK):
        filename = "%s\\%s\\%s" % (CAMERA_IMG_TEMPLATE_PATH, CURRENT_FACE_NAME, random.choice(IMAGE_TEMPLATE_FILES))
        imageTemplate = face_recognition.load_image_file(filename)
        try:
            # Sometimes a template doesn't work properly, thus no faces are detected on it.
            imageTemplateEncoding = face_recognition.face_encodings(imageTemplate)[0]
        except IndexError:
            continue
        imageTemplateEncodings.append(imageTemplateEncoding)
    
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    
    # If there are multiple or no faces, return error.
    if len(face_locations) > 1: return (frame, "MULTIPLE")
    if len(face_locations) < 1: return (frame, "NOFACE")
    
    face_encoding = face_recognition.face_encodings(rgb_small_frame, face_locations)[0]
    matches = face_recognition.compare_faces(imageTemplateEncodings, face_encoding)
    
    (top, right, bottom, left) = face_locations[0]
    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
    top *= 4
    right *= 4
    bottom *= 4
    left *= 4
    # Draw a box around the face
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Only returning True if all templates are similar enough.
    return (frame, all(matches))

def CheckWebcam(showFrames=False):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened(): raise IOError("Cannot open webcam")
    
    # Initialize some variables
    correlations = []
    recordedFrames = []

    logging.info("Recording %i frames." % AMOUNT_OF_FRAMES_TO_RECORD)
    # Record frames and store them in memory, so the camera won't be opened for long.
    for i in range(0,AMOUNT_OF_FRAMES_TO_RECORD):
        _, frame = cap.read()
        recordedFrames.append(frame)

    cap.release()

    for frame in recordedFrames:
        frame, isMatched = CompareFrameToTemplates(frame)

        # Check for errors before setting it as a proper result.
        if (isMatched == "NOFACE"):
            #logging.info("No face has been found.") # TODO: this?
            pass
        elif (isMatched == "MULTIPLE"):
            #logging.info("Multiple faces have been found.") # TODO: this?
            pass
        elif (str(isMatched) != 'True' and str(isMatched) != 'False'):
            logging.error("Error. Frame checking didn't return a bool, it returned", isMatched)
        else:
            correlations.append(isMatched)

        if showFrames:
            cv2.imshow("Webcam", frame)
            cv2.waitKey(1)

    cv2.destroyAllWindows()

    try:
        result = statistics.mean(correlations)
    except statistics.StatisticsError: # In case no proper face was detected.
        result = 0
    return (recordedFrames, result)

"""
Takes images from the webcam and stores them in a dictionary called faceName.
"""
def CreateNewFace(faceName=GetRandomHex(20), setDefault=False):
    logging.info("Creating a new face called '%s'.", faceName)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened(): raise IOError("Cannot open webcam")
    
    os.mkdir("%s\\%s" % (CAMERA_IMG_TEMPLATE_PATH, faceName))
    
    imagesTaken = 0
    while imagesTaken < AMOUNT_OF_IMAGES_FOR_NEW_FACE:
        _, frame = cap.read()
        
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)

        # Only save file if a face has been detected.
        if len(face_locations) > 1 or len(face_locations) < 1: 
            continue

        frameName = GetRandomHex(12)
        fileName = "%s\\%s\\%s.jpg" % (CAMERA_IMG_TEMPLATE_PATH, faceName, frameName)
        cv2.imwrite(fileName, frame)
        imagesTaken += 1

    logging.info("A new face called '%s' has been created with %i images.", faceName, imagesTaken)

    if setDefault:
        # In case we want to use the new face immediately after creating it.
        SetFace(faceName)

        # Read config file and find where DEFAULT_FACE_NAME is.
        lines = open(CONFIG_FILE_PATH, 'r').readlines()
        lineToWrite = 0
        for i, line in enumerate(lines):
            if "DEFAULT_FACE_NAME" in line:
                lineToWrite = i
        
        # Change DEFAULT_FACE_NAME's value to the newly created face's name.
        lines[lineToWrite] = "DEFAULT_FACE_NAME=%s\n" % faceName 

        # Save the modified config file.
        out = open(CONFIG_FILE_PATH, 'w')
        out.writelines(lines)
        out.close()

def LoadSettings(configFile = CONFIG_FILE_PATH):
    logging.info("Loading settings from file '%s'", configFile)

    # Changing file path, in case it is not the default value.
    global CONFIG_FILE_PATH
    CONFIG_FILE_PATH = configFile
    # Read the file into a list of lines
    with open(configFile, 'r') as f:
        lines = f.read().split("\n")

        # Find each setting #TODO: There must be some better (and secure!) way to do this.
        for i, line in enumerate(lines):
            if "DEFAULT_FACE_NAME" in line:
                value = line.split('=')[1]
                logging.info("Found DEFAULT_FACE_NAME (%s) in config file." % value)
                if (value != ''):
                    SetFace(value)
                else:
                    logging.info("DEFAULT_FACE_NAME is empty in config file.")
            if "AMOUNT_OF_FRAMES_TO_RECORD" in line:
                value = line.split('=')[1]
                logging.info("Found AMOUNT_OF_FRAMES_TO_RECORD (%s) in config file." % value)
                if (value != ''):
                    global AMOUNT_OF_FRAMES_TO_RECORD
                    AMOUNT_OF_FRAMES_TO_RECORD = int(value)
                else:
                    logging.info("AMOUNT_OF_FRAMES_TO_RECORD is empty in config file.")
            if "AMOUNT_OF_IMAGES_FOR_NEW_FACE" in line:
                value = line.split('=')[1]
                logging.info("Found AMOUNT_OF_IMAGES_FOR_NEW_FACE (%s) in config file." % value)
                if (value != ''):
                    global AMOUNT_OF_IMAGES_FOR_NEW_FACE
                    AMOUNT_OF_IMAGES_FOR_NEW_FACE = int(value)
                else:
                    logging.info("AMOUNT_OF_IMAGES_FOR_NEW_FACE is empty in config file.")
            if "AMOUNT_OF_TEMPLATES_TO_CHECK" in line:
                value = line.split('=')[1]
                logging.info("Found AMOUNT_OF_TEMPLATES_TO_CHECK (%s) in config file." % value)
                if (value != ''):
                    global AMOUNT_OF_TEMPLATES_TO_CHECK
                    AMOUNT_OF_TEMPLATES_TO_CHECK = int(value)
                else:
                    logging.info("AMOUNT_OF_TEMPLATES_TO_CHECK is empty in config file.")
                
def _():
    LoadSettings()
    recordedFrames, result = CheckWebcam(showFrames=False)

    logging.info("The user is %i%% similar to the face '%s'.", result * 100, CURRENT_FACE_NAME)
    
    if ((result * 100) < 50):
        logging.info("Result was below 50%%, thus saving recorded frames to %s.", RECORDINGS_PATH)
        for frame in recordedFrames:
            filename = "%s\\%s.jpg" % (RECORDINGS_PATH, GetRandomHex(13))
            cv2.imwrite(filename, frame)
    
if __name__ == '__main__':
    SetFace("c7ed9009605aedc6e752")
    recordedFrames, result = CheckWebcam(showFrames=True)
    time.sleep(1)
    print(result * 100)
