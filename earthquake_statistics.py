import statistics as stat
# User defined Package
import mystats

def read_txt(filename):
    txt_list = []
    with open(filename, "r") as f:
        txt_data = f.readlines()
        for line in txt_data:
            txt_list.append(line.strip('\n').split('\t'))
        return txt_list

filename = "Earthquake data for students.txt"

def compute_statistics():
    txt_list = read_txt(filename)
    txt_list.pop(0)
    mag_list = []
    for item in txt_list:
        mag_list.append(float(item[4]))
    # print("MagList is:", mag_list)
    print("Min of Magnitude is:", min(mag_list))
    print("Max of Magnitude is:", max(mag_list))
    print("Mean of Magnitude is:", stat.mean(mag_list))
    print("Median of Magnitude is:", stat.median(mag_list))
    print("Range of Magnitude is:", max(mag_list) - min(mag_list))
    print("Mode of Magnitude is:", stat.mode(mag_list))
    print("Standard Deviation of Magnitude is:", stat.stdev(mag_list))
    print("Mystats Median of Magnitude is:", mystats.getMedian(mag_list))
    print("Mystats Standard Deviation of Magnitude is:", mystats.getStdev(mag_list, stat.mean(mag_list)))
    number_of_earthquakes(mag_list, max(mag_list))


# Can you add a few lines in your code file in order to report # of earthquakes in mag of (0,1), [1, 2.5),[2.5, 4.5), [4.5,) respectively? note: '(' indicates not including, ']' indicates including. e.g. [1,2.5) means >=1 and <2.5).

def number_of_earthquakes(quakes, mag_max):
    range1, range2, range3, range4 = 0, 0, 0, 0
    for quake in quakes:
        if quake > 0 and quake < 1:
            range1 += 1
        elif quake >= 1 and quake < 2.5:
            range2 += 1
        elif quake >= 2.5 and quake < 4.5:
            range3 += 1
        elif quake >= 4.5 and quake < mag_max:
            range4 += 1
    print("No. of Earthquakes in mag (0,1) is:", range1)
    print("No. of Earthquakes in mag [1, 2.5) is:", range2)
    print("No. of Earthquakes in mag [2.5, 4.5) is:", range3)
    print("No. of Earthquakes in mag [4.5,) is:", range4)


compute_statistics()