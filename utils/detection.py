import queue
import numpy as np
import os


from collections import Counter
 
def find_mode(nums):
    num_count = Counter(nums)  # 统计元素出现的次数
    mode = num_count.most_common(1)  # 找到出现次数最多的元素
    return mode[0][0]  # 返回众数


class LoadData:
    def __init__(self, path=None):
        if path is None:
            self.path = "./data/"
        else:
            self.path = path
        self.files = []
        self.file_index = 0
    def load(self, path=None, subdir=None):
        if path is None:
            self.path = "./data/"
        else:
            self.path = path
        if subdir is None:
            for record_time in os.listdir(self.path):
                for frame in os.listdir(self.path+record_time):
                    self.files.append(record_time+'/'+frame)
        else:
            for frame in os.listdir(self.path+subdir):
                    self.files.append(subdir+'/'+frame)
    def get(self):
        try:
            frame = np.load(self.path+self.files[self.file_index])
            self.file_index += 1
        except IndexError:
            print("Run out of data")
            return None
        return frame

    def forward(self, frames):
        if self.file_index + frames <= len(self.files):
            self.file_index += frames
        else:
            self.file_index = len(self.files)-1

    def rewind(self, frames):
        if self.file_index > frames:
            self.file_index -= frames
        else:
            self.file_index = 0

    def src(self):
        return self.path+self.files[self.file_index]

class HumanDetector:
    def __init__(self, empty_map=None):
        self.time_window = queue.Queue(75)
        self.last_frame = None
        self.action_map = np.zeros((62,80))
        self.change_map = np.zeros((62,80))
        self.enhanced_change = None
        if empty_map is None:
            self.empty_map = np.zeros((62,80))
            self.time_count = 0
        else:
            self.empty_map = empty_map
            self.time_count = 5000
        pass
    def detect(self, frame):
        # print(frame)
        if self.time_window.empty():
            self.last_frame = frame
            self.time_window.put(frame)
            return False
        changed = frame - self.last_frame
        # print(changed)
        for index, value in np.ndenumerate(changed):
            if value >= 2:
                self.action_map[index] = 75
            else:
                self.action_map[index] = self.action_map[index] - 1 if self.action_map[index] > 0 else 0
        print(np.sum(self.action_map>0))        
        self.last_frame = frame
        if self.time_window.full():
            self.time_window.get()
        self.time_window.put(frame)
        if np.sum(self.action_map>0) > 1000:
            return True

    def long_detect(self, frame):
        if self.time_count == 0:
            self.empty_map = frame
            self.time_count += 1
            return False
        else:
            changed = frame - self.empty_map
            self.change_map = changed
            self.enhance()
            if self.time_count < 5000:
                self.time_count += 1000
            else:
                self.time_count += 1
            self.empty_map = (self.time_count - 1)/self.time_count * self.empty_map + frame / self.time_count
            print(np.sum(changed>=2))
            if np.sum(changed>=2) > 120:
                return True
            else:
                return False
            
    def enhance(self):
        self.enhanced_change = np.zeros((62,80))
        mode = find_mode(self.empty_map.flatten())
        for i in range(len(self.change_map)):
            for j in range(len(self.change_map[i])):
                if self.change_map[i][j] > 2 and self.empty_map[i][j] > mode:
                    self.change_map[i][j] += self.empty_map[i][j]
                


            
    def output(self):
        np.save('empty_map.npy', self.empty_map)


class GMMdetector:
    def __init__(self):
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        self.fgbg = cv2.createBackgroundSubtractorMOG2()

    def detect(frame):
        fgmask = fgbg.apply(filtered_frame_resized)
        pass
