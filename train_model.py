#!/usr/bin/python

import cv2
import numpy as np
import os
import sys

def read_images(path, sz=None):
    """Reads the images in a given folder, resizes images on the fly if size is given.

    Args:
        path: Path to a folder with subfolders representing the subjects (persons).
        sz: A tuple with the size Resizes

    Returns:
        A list [X,y]

            X: The images, which is a Python list of numpy arrays.
            y: The corresponding labels (the unique number of the subject, person) in a Python list.
    """
    c = 0
    X,y = [], []
    for dirname, dirnames, filenames in os.walk(path):
        for subdirname in dirnames:
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                try:
                    im = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                    # resize to given size (if given)
                    if (sz is not None):
                        im = cv2.resize(im, sz)
                    X.append(np.asarray(im, dtype=np.uint8))
                    y.append(c)
                except IOError, (errno, strerror):
                    print "I/O error({0}): {1}".format(errno, strerror)
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise
            c = c+1
    print "Len of X: %d, y: %d" % (len(X), len(y))
    return [X,y]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "USAGE: train_model.py </path/to/images>"
        sys.exit()
    # Now read in the image data. This must be a valid path!
    [X,y] = read_images(sys.argv[1], (42, 42))
    # Convert labels to 32bit integers. This is a workaround for 64bit machines,
    # because the labels will truncated else. This will be fixed in code as
    # soon as possible, so Python users don't need to know about this.
    # Thanks to Leo Dirac for reporting:
    y = np.asarray(y, dtype=np.int32)
    # Create the Eigenfaces model. We are going to use the default
    # parameters for this simple example, please read the documentation
    # for thresholding:
    model = cv2.createEigenFaceRecognizer()
    # Read
    # Learn the model. Remember our function returns Python lists,
    # so we use np.asarray to turn them into NumPy lists to make
    # the OpenCV wrapper happy:
    model.train(np.asarray(X), np.asarray(y))

    [p_label, p_confidence] = model.predict(np.asarray(X[1]))
    print "Predicted label = %d (confidence=%.2f)" % (p_label, p_confidence)
    model.save("model.xml")
