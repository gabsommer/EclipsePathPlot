import numpy as np
import pandas as pd
import math
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt


def clean_hull(lst: np.ndarray, tol: float = 1.5) -> np.ndarray:
    """
    Excludes outliers of the hull by checking if the points are within a certain distance from the average
    distance of the points to its nearest neighbor.

    Parameters
    ----------
    lst : np.ndarray
        A numpy array of shape (n, 2) where n is the number of points and 2 represents lon and lat coordinates.
    tol : int, optional
        Tolerance factor to determine if a point is an outlier based on (tol) times its distance to the nearest
        neighbors. The default is 5.
    """

    if lst.shape != (lst.shape[0], 2):
        raise ValueError(
            f"Input must be a numpy array of shape (n, 2) where n is the number of points (resolution of (pen)umbra), but shape is {lst.shape}"
        )
    if lst.shape[0] < 3:
        return lst  # Not enough points to form a hull, keep the original list
    ##First calculcate each distance to the nearest neighbor by looping through the elements of the numpy array
    lst_neighbor_right = np.roll(lst, -1)
    lst_neighbor_left = np.roll(lst, 1)
    #TODO Why np.linalg.norm ? This should be sum, no ?
    lst_distance_right = np.linalg.norm(lst - lst_neighbor_right, axis=1)
    lst_distance_left = np.linalg.norm(lst - lst_neighbor_left, axis=1)

    mean_distance = np.mean((lst_distance_right + lst_distance_left) * 0.5)

    for i in range(len(lst_distance_right)):
        if (
            lst_distance_right[i] > mean_distance * tol
            and lst_distance_left[i] > mean_distance * tol
        ):
            # If the distance to the two nearest neighbors is greater than the mean distance times the tolerance,
            np.delete(lst, i, axis=0)
            # we consider this point an outlier and remove it.

    # return the clean list
    return lst

def data_pd(absolutepath, plotpoints):
    """
    Reads data from a CSV file and reshapes it into a 3D numpy array.

    Parameters
    ----------
    absolutepath : str
        The absolute path to the CSV file containing the data.
    plotpoints : int
        The number of points to plot in each time step.
    """
    data = pd.read_csv(absolutepath, header=None)
    datanp = data.to_numpy()
    datanp = datanp.astype(float)
    datanp = np.expand_dims(datanp, axis=0)
    datanp = datanp.reshape(int((datanp.shape[1]) / plotpoints), plotpoints, 3)
    return datanp

def clean(input):
    """
    Deletes rows from a 2D numpy array where the first or second element is NaN.
    
    Parameters
    ----------
    input : np.ndarray
        A 2D numpy array where each row represents a point with at least two elements.
    """

    del_idx = np.empty((0), dtype=int)
    for k, row in enumerate(input):
        if math.isnan(row[0]) or math.isnan(row[1]):
            del_idx = np.append(del_idx, int(k))
    output = np.delete(input, del_idx, axis=0)
    return output

def lon_lat_split(path: str, type: str, delimiter: str = ",", delta: int = 24*3600, clean: bool = False) -> None:
    """
    Function to read a .dat file and split each input file such that each 
    eclipse hast its own file .

    Parameters
    ----------
    path : str
        The path to the .dat file to be read.
    type : str
        The type of eclipse data to be processed, either "umbra" or "penumbra".
        Raises ValueError if the type is not one of these.
    delimiter : str, optional
        The delimiter used to split the lines in the file. Default is tab (",").
    delta : int, optional
        The minimum time difference in seconds to consider it a new eclipse. Default is 24 hours (24*3600 seconds).
    clean : bool, optional
        If True, cleans the data by removing rows with NaN values. Default is False.
    """

    if type != "umbra" and type != "penumbra":
        raise ValueError("Type must be either 'umbra' or 'penumbra'")
    #Here we just get the initdate from the config file we need that later in the function
    config = {}
    with open("../main.conf", "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):  #Ignore empty lines and comments
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = float(value.strip())
    init_year = int(config["init_year"])
    init_month = int(config["init_month"])
    init_day = int(config["init_day"])
    init_hour = int(config["init_hour"])
    init_minute = int(config["init_min"])
    init_second = int(config["init_second"])
    init_date = datetime(
    init_year, init_month, init_day, init_hour, init_minute, init_second
    )

    

    #Now we open the actual file that we want to split
    if not path.endswith(".dat"):
        raise ValueError("The file must be a .dat file")
    f = open(path, "r")
    if f == None:
        raise ValueError("The file does not exist or cannot be opened")
    
    #List with each line in the file
    #lines = f.readlines()
    lines = np.loadtxt(path, delimiter=delimiter, dtype=str, comments=None)
    linelistbefore = np.char.strip(lines[0])
    #lineslistbefore = np.char.split(linelistbefore, delimiter)
    #linelistbefore = lines[0].strip().split(delimiter)

    eclipse_count = 0
    splitidxbefore = 0

    for idx,line in enumerate(lines):
        #We skip the first line, as it is used for comparison
        if idx == 0:
            continue
        #Here from every line we remove the newline character and split the line into a list of strings
        #linelist = line.strip().split(delimiter)
        linelist = np.char.strip(line)
        #linelist = np.char.split(linelist, delimiter)

        
        
        if abs(int(linelist[-1]) - int(linelistbefore[-1])) >= delta:
            #Here is what happens when we found a jump in time, meaning a new eclipse begins
            #We write the lines up until this index into new file
            splitidx = idx
            #Lets first get the date from the found splitidx:
            date = init_date + timedelta(seconds=int(linelistbefore[-1]))
            datestr = date.strftime("%Y%m%d")


            with open("../data/split/" + datestr + "lonlat_" + type + ".dat", "w") as fsplit:
                linestowrite = lines[splitidxbefore:splitidx]
                #If option clean is set to True, we clean the data along the way
                #Since we are iterating through the lines anyway
                if clean:
                    deleteidx = np.array([], dtype=int)
                    for kidx,k in enumerate(linestowrite):
                        # Example: Remove lines where any element is "nan", "NaN", or "NAN"
                        if any(val.lower() == "nan" for val in np.array(k, dtype=str)):
                            deleteidx = np.append(deleteidx, kidx)
                    #now we remove the lines with NaN values:
                    linestowrite = np.delete(linestowrite, deleteidx, axis=0)
                    #linestowrite = [itemlist for iidx, itemlist in enumerate(linestowrite) if iidx not in deleteidx_set]

                
                
                np.savetxt(fsplit, linestowrite, fmt="%s", delimiter=delimiter)
            splitidxbefore = idx
            eclipse_count += 1 

        #When done we set the linelistbefore which is used as comparison for the next iteration
        linelistbefore = linelist

    #After that is down one last eclipse remains.
    #The contents after that last split are not yet written to a file, so we
    #use splitidx to write the last file and if clean is set to True we again remove
    #NaN values from the data:
    linestowrite = lines[splitidx:]

    if clean:
        deleteidx = np.array([], dtype=int)
        for kidx,k in enumerate(linestowrite):
            # Example: Remove lines where any element is "nan", "NaN", or "NAN"
            if any(val.lower() == "nan" for val in np.array(k, dtype=str)):
                deleteidx = np.append(deleteidx, kidx)
        #now we remove the lines with NaN values:
        linestowrite = np.delete(linestowrite, deleteidx, axis=0)
        
    #splitidx is exactly the last index of the eclipse before the last one, so
    #we have to add one to it to get the date for the last eclipse -> lines[splitidx+1]....
    lastdateline = np.char.strip(lines[splitidx+1])
    date = init_date + timedelta(seconds=int(lastdateline[-1]))
    datestr = date.strftime("%Y%m%d")

    with open("../data/split/" + datestr + "lonlat_" + type + ".dat", "w") as fsplit:
        np.savetxt(fsplit, linestowrite, fmt="%s", delimiter=delimiter)

def get_eclipses(path: str, type: str = "umbra") -> list:
    """
    Function return a list of paths and therefore a list of elcipses.

    Parameters
    ----------
    path : str
        The path to the directory containing all split eclipse files
    type : str
        The type of eclipse data to be processed, either "umbra" or "penumbra".
        Raises ValueError if the type is not one of these.
    """
    if type != "umbra" and type != "penumbra":
        raise ValueError("Type must be either 'umbra' or 'penumbra'")
    if not os.path.exists(path):
        raise ValueError("The file does not exist or cannot be opened")
    if not os.path.isdir(path):
        raise ValueError(f"{path} is not a directory")
    eclipses = []
    for filename in os.listdir(path):
        eclipsestring = filename[:8]
        if eclipsestring not in eclipses:
            eclipses.append(filename[:8])
    return eclipses

def clean_hull2(input: np.ndarray,tol: float = 2) -> np.ndarray:
    """
    Excludes outliers of the hull by checking if the points are within a certain distance from the average
    distance of the points to its nearest neighbor.

    Parameters
    ----------
    lst : np.ndarray
        A numpy array of shape (n, 2) where n is the number of points and 2 represents lon and lat coordinates.
    tol : int, optional
        Tolerance factor to determine if a point is an outlier based on (tol) times its distance to the nearest
        neighbors. The default is 5.
    """
    input_left = np.roll(input,1, axis = 0)
    input_right = np.roll(input,-1, axis = 0)

    input_normdiff_left = np.linalg.norm(input - input_left, axis = 1)
    input_normdiff_right = np.linalg.norm(input - input_right, axis = 1)
    input_meandiff = (input_normdiff_left + input_normdiff_right)*0.5
   
    if input_meandiff.shape[0] < 3:
        return input
    mean_diff = np.nanmean(input_meandiff)
    killist = []
    for idx,i in enumerate(input_meandiff):
        if i > mean_diff * tol or np.isnan(i) == True:
            killist.append(idx)

    input_clean = np.delete(input, killist, axis = 0)
    return input_clean

def orthodrome(p1: np.ndarray | list[float], p2: np.ndarray | list[float], res: int = 20) -> np.ndarray:
    """
    Given two points p1 and p2, returns list of (lon,lat)-points on an orthodrome connecting the points p1,p2

    Parameters
    ----------
    p1 : np.ndarray
        A numpy array of shape (2,) representing the first point (lon, lat).
    p2 : np.ndarray
        A numpy array of shape (2,) representing the second point (lon, lat).
    res : int, optional
        The number of points to generate along the orthodrome. Default is 20.
    """
    print("Not implemented")
    p1 = np.radians(p1)
    p2 = np.radians(p2)
    #Transform points into cartesian coordinates on unit sphere
    r1 = np.array([math.cos(p1[1])*math.cos(p1[0]), math.cos(p1[1])*math.sin(p1[0]), math.sin(p1[1])],dtype=float)
    r2 = np.array([math.cos(p2[1])*math.cos(p2[0]), math.cos(p2[1])*math.sin(p2[0]), math.sin(p2[1])],dtype=float)
    #Create [res] vectors in a list that point to chord of great circle between p1,p2
    k=np.linspace(0,1,res).reshape(res,1)
    Ik = r1+ k*(r2-r1)
    ik = Ik / np.linalg.norm(Ik, axis = 1, keepdims=True)
    #now the iks need to be transofrmed into lons and lats again
    lonslats = np.zeros(shape=(res,2))
    print(r1,r2)
    for i in range(res):
        x = ik[i,0]
        y = ik[i,1]
        z = ik[i,2]
        if x < 0 and y > 0:
            lonslats[i,0] = math.degrees(math.atan(y/x)+math.pi)
        if x < 0 and y < 0:
            lonslats[i,0] = math.degrees(math.atan(y/x)-math.pi)
        if x > 0 and y < 0:
            lonslats[i,0] = math.degrees(math.atan(y/x))
        else:
            lonslats[i,0] = math.degrees(math.atan(y/x))
        lonslats[i,1] = math.degrees(math.asin(z))
    return(lonslats)