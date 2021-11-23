import pandas as pd


data = pd.read_csv("Flight_Schedule_without_missing.csv")
data = data.drop(["dayOfWeek", "validFrom", "validTo"], axis=1)
data.drop(data[data["airline"] != "GoAir"].index, inplace=True)
data = data.dropna()
data = data.drop_duplicates(subset=["origin", "destination"], keep="last")
data.reset_index(drop=True, inplace=True)

arr = pd.to_datetime(data["scheduledArrivalTime"], format="%H:%M")
dep = pd.to_datetime(data["scheduledDepartureTime"], format="%H:%M")

diff = arr - dep
data["timeTaken"] = (diff.dt.components["hours"] * 60) + diff.dt.components["minutes"]

unique = pd.unique(data[["origin", "destination"]].values.ravel("K"))

def get_origins():
    return data["origin"].to_list()

def get_destinations():
    return data["destination"].to_list()