from py_wake.examples.data.hornsrev1 import Hornsrev1Site, V80
from py_wake import NOJ
import pandas as pd
from minio import Minio
import os
import io

# Setting up access to the Minio Object Storage bucket containing the input file
client = Minio("windfall.hlrs.de", "access_key", "secret_key")
bucket_name = "meridional"
object_name = "input.csv"
object = client.get_object(bucket_name, object_name)

# Read the remote input file 
input = pd.read_csv(io.BytesIO(object.read()))

x = input["x"].values
y = input["y"].values

windTurbines = V80()
site = Hornsrev1Site()
noj = NOJ(site, windTurbines)

simulation_result = noj(x, y)
result = simulation_result.aep()

df_result = result.to_dataframe(name="AEP (GWh)").reset_index()
print(df_result)

# Optionally upload the results to minio
file_to_upload = "df_result.csv"
df_result.to_csv(file_to_upload, index=False)

file_size = os.path.getsize(file_to_upload)
with open(file_to_upload, "rb") as file_data:
    client.put_object(bucket_name, file_to_upload, file_data, length=file_size)
    print(f"{file_to_upload} uploaded")
