from __future__ import division
import datetime
from PIL import Image
from PyQt4 import QtCore
import LeonardoMethods
class Splinter(QtCore.QThread):
    progress = QtCore.pyqtSignal(str, int, datetime.datetime, bool, list)
    def __init__(self):
        super(Splinter,self).__init__()
        self.mutex = QtCore.QMutex()
        self.condition = QtCore.QWaitCondition()
        self.allow_run = False
        self.data = None
        self.parent_image_position = (0.5,0.5)
        self.icon_positioning = None
        self.icon_palette = "Black"
        self.allow_overlap = False
        self.background_image_path = None
        self.primary_attribute_relative_size = 0.10
        self.secondary_attribute_relative_size = 0.05
        self.output_location = None
        if not self.isRunning():
            self.start(QtCore.QThread.LowPriority)

    def run(self):
        while True:
            if self.allow_run:
                total = len(self.data)
                counter = 0
                start_time = datetime.datetime.now()
                images_list = []
                for row in self.data:
                    counter+=1
                    fsn = row["FSN"]
                    category = row["Category"]
                    primary_attribute_data = []
                    primary_attributes = []
                    secondary_attributes = []
                    for key in row.keys():
                        if "Primary USP" in key:
                            primary_attributes.append(key)
                        elif "Secondary USP" in key:
                            secondary_attributes.append(key)
                    primary_attributes_count = len(primary_attributes)/2
                    primary_attribute_data = [] 
                    #print primary_attributes_count
                    for i in range(int(primary_attributes_count)):
                        index = i+1
                        primary_attribute_data.append({"Attribute":row["Primary USP-%d Attribute"%index],"Description Text":row["Primary USP-%d Description Text"%index]})
                    secondary_attributes_count = len(secondary_attributes)/2
                    secondary_attribute_data = [] 
                    #print secondary_attributes_count
                    for i in range(int(secondary_attributes_count)):
                        index = i+1
                        secondary_attribute_data.append({"Attribute":row["Secondary USP-%d Attribute"%index],"Description Text":row["Secondary USP-%d Description Text"%index]})
                    image_name = LeonardoMethods.prepareAppImage(fsn, category, primary_attribute_data, secondary_attribute_data, self.parent_image_position, self.icon_positioning, self.icon_palette, self.allow_overlap, self.background_image_path, self.primary_attribute_relative_size, self.secondary_attribute_relative_size, self.bounding_box, self.output_location)
                    eta = LeonardoMethods.getETA(start_time, counter, total)
                    images_list.append(image_name)
                    if counter < total:
                        message = "Processing %d of %d FSNs." %(counter,total)
                        progress = int(counter/total*100)
                        completion_status = False
                    else:
                        message = "Completed."
                        progress = 100
                        completion_status = True
                    self.progress.emit(message, progress, eta, completion_status, images_list)
                print "Completed in %ss." %(datetime.datetime.now() - start_time)
                self.allow_run = False
#                self.deploy()
    
    def deploy(self):
        print "Doing shit."


    def __del__(self):
        self.mutex.lock()
        self.condition.wakeOne()
        self.mutex.unlock()
        self.wait()