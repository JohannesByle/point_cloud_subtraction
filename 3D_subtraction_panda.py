import laspy
import pandas as pd
from datetime import datetime
import numpy as np
import pickle


# Average all x,y,z values in a .las file to a given step size
def get_avg(path, step):
    file = laspy.file.File(path, mode="r")
    df = pd.DataFrame({"x": file.x, "y": file.y, "z": file.z})
    df = df.div(step)
    df = df.round()
    df = df.mul(step)
    return df


# Convert pandas dataframe into a .las file
def generate_las(df, name):
    hdr = laspy.header.Header()
    outfile = laspy.file.File(name, mode="w", header=hdr)
    xmin = np.floor(np.min(df.get("x")))
    ymin = np.floor(np.min(df.get("y")))
    zmin = np.floor(np.min(df.get("z")))
    outfile.header.offset = [xmin, ymin, zmin]
    outfile.header.scale = [0.001, 0.001, 0.001]
    outfile.x = df.get("x")
    outfile.y = df.get("y")
    outfile.z = df.get("z")
    outfile.intensity = df.get("intensity")
    outfile.close()


# path_1 = r"D:\Productivity\Lidar\test_data\97_merge19_7_22.las"
# path_2 = r"D:\Productivity\Lidar\test_data\97_merge19_7_23.las"
path_1 = r"output.las"
path_2 = r"output_2.las"
step = 0.03

print("Destroying Detail, Grid 1")
start_time = datetime.now()
df_1 = get_avg(path_1, step)
df_1 = df_1.drop_duplicates()
print("Destroying Detail, Grid 2")
df_2 = get_avg(path_2, step)
df_2 = df_2.drop_duplicates()
print("Processing Subtracted Grid")
df_subtracted = pd.concat([df_1, df_2], ignore_index=True).drop_duplicates(keep=False)
df_subtracted = pd.merge(df_subtracted, df_2, how="inner")
df_1 = None
df_2 = None
print("Restoring Detail")
df_avg = get_avg(path_2, step)
file = laspy.file.File(path_2, mode="r")
df_final = pd.DataFrame({"x_final": file.x, "y_final": file.y, "z_final": file.z, "intensity": file.intensity,
                         "x": df_avg.get("x"), "y": df_avg.get("y"), "z": df_avg.get("z")})
df_avg = None
df = pd.merge(df_subtracted, df_final, how='inner', on=['x', 'y', 'z'])
df = pd.DataFrame({"x": df.get("x_final"), "y": df.get("y_final"), "z": df.get("z_final"),
                   "intensity": df.get("intensity")})
generate_las(df, "Subtracted_Grid.las")
print("Total time:"+str(datetime.now()-start_time))

