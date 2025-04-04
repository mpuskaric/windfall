from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80, wt_x, wt_y, wt16_x, wt16_y
from py_wake import NOJ
import matplotlib.pyplot as plt
import pandas as pd
from minio import Minio
import os
import glob

windTurbines = V80()
site = Hornsrev1Site()
noj = NOJ(site,windTurbines)

simulationResult = noj(wt16_x,wt16_y)
result = simulationResult.aep()
df_result = result.to_dataframe(name="AEP (GWh)").reset_index()
df_result.to_csv("AEP_result.csv", index=False)

print ("Total AEP: %f GWh"%simulationResult.aep().sum())

plt.figure()
aep = simulationResult.aep()
windTurbines.plot(wt16_x,wt16_y)
c = plt.scatter(wt16_x, wt16_y, c=aep.sum(['wd','ws']))
plt.colorbar(c, label='AEP [GWh]')
plt.title('AEP of each turbine')
plt.xlabel('x [m]')
plt.ylabel('[m]')
plt.savefig('AEP_of_each_turbine.png')

plt.figure()
aep.sum(['wt','wd']).plot()
plt.xlabel("Wind speed [m/s]")
plt.ylabel("AEP [GWh]")
plt.title('AEP vs wind speed')
plt.savefig('AEP_vs_wind_speed.png')

plt.figure()
aep.sum(['wt','ws']).plot()
plt.xlabel("Wind direction [deg]")
plt.ylabel("AEP [GWh]")
plt.title('AEP vs wind direction')
plt.savefig('AEP_vs_wind_direction.png')

wind_speed = 10
wind_direction = 270

plt.figure()
flow_map = simulationResult.flow_map(ws=wind_speed, wd=wind_direction)
plt.figure(figsize=(18,10))
flow_map.plot_wake_map()
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('Wake map for' + f' {wind_speed} m/s and {wind_direction} deg')
plt.savefig('AEP_wake_map.png')

# Upload data to minio
client = Minio("windfall.hlrs.de", "access_key", "secret_key")
bucket_name = "meridional"
files_to_upload = glob.glob("AEP_*")

for file_path in files_to_upload:
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file_data:
        client.put_object(bucket_name, file_path, file_data, length=file_size)
    print(f"{file_path} uploaded")

print("Finished uploading")
