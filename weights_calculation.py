import pandas as pd
import numpy as np

col_names = ["date", "tflag", "theta", "terr", "rflag", 
             "rho", "reflag", "rerr", "mflag1", "mag1", 
             "m1eflag", "m1err", "mflag2", "mag2", "m2eflag", 
             "m2err", "filter", "fflag", "tel", "teflag", 
             "nn", "ref", "tech", "codes", "de_note"]
col_specs = [(7,17),(18,19),(19,26),(27,33),(34,35),
             (35,44),(45,46),(46,53),(54,55),(55,61),
             (61,62),(62,67),(68,69),(69,75),(75,76),
             (76,81),(82,90),(90,91),(92,97),(97,98),
             (99,101),(102,110),(111,113),(114,116),(116,117)]

micrometry_tech_codes = ["M", "Ma", "Mb", "Mc", "Md", "Mr"]
speckle_tech_codes = ["S", "Sa", "Sb", "Sc", "Si", "Sp", "Ss", "St", "Su"]
tech_code_weights = {"J":1.0, "Zp":1.0, "C":1.0, "Ce":1.0, "Cl":1.0, "Cu":1.0, "Ig":1.0, "Hh":1.0, "Ht":1.0}

#update the file path for your local copy
df = pd.read_fwf("wds_historical_file.txt", colspecs=col_specs, names=col_names, header=None, skiprows=11)

df = df[pd.to_numeric(df["date"], errors="coerce").notna()]
df = df.reset_index(drop=True)

#exclude any outliers here (update the date value and ref value)
df = df[~((df["date"] == 1896.69) & (df["ref"] == "L__1896a"))]
df = df.reset_index(drop=True)

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

df["date"] = pd.to_numeric(df["date"], errors="coerce")
df["tel"] = pd.to_numeric(df["tel"], errors="coerce")
df["nn"] = pd.to_numeric(df["nn"], errors="coerce")
df["sqrt_n"] = np.sqrt(pd.to_numeric(df["nn"], errors="coerce"))
df["rho"] = pd.to_numeric(df["rho"], errors="coerce")


df["w_quality"] = 1.0
for i in range(len(df)):
    if df["tflag"][i] == ":" or df["rflag"][i] == ":":
        df.loc[i, "w_quality"] = 0.5
    else:
        df.loc[i, "w_quality"] = 1.0


def calculate_w_technique(technique, aperture, date):
    if technique in speckle_tech_codes:
        if aperture >= 2.5:
            return 10.0
        elif aperture >= 1.5:
            return 7.5
        else:
            return 5.0 #note: only large aperture (>=2.5m) speckle weight of 10.0 was explicitly stated in Hartkopf et al. (2001), so smaller speckle weights are approximations
    elif technique in micrometry_tech_codes:
        if date < 1830:
            return 0.01
        elif date < 1850:
            return 0.05
        else:
            return 0.1
    else:
        return tech_code_weights.get(technique, 1.0)

df["w_technique"] = 1.0
for i in range(len(df)):
    df.loc[i, "w_technique"] = calculate_w_technique(df.loc[i, "tech"], df.loc[i, "tel"], df.loc[i, "date"])


arcsec_per_radian = (3600 * 180) / np.pi

def calculate_w_separation(rho, aperture, wavelength):
    if pd.isna(rho) or pd.isna(aperture):
        return np.nan
    rayleigh_limit = 1.22 * (wavelength * 0.000000001 / aperture) * arcsec_per_radian
    rayleighs = rho / rayleigh_limit
    if rayleighs >= 10.0:
        return 1.0
    else:
        return rayleighs / 10.0

def get_wavelength(filter_value):
    if pd.isna(filter_value):
        return 550.0
    else:
        return float(str(filter_value).split()[0])

df["wavelength"] = 550.0

for i in range(len(df)):
    df.loc[i, "wavelength"] = get_wavelength(df.loc[i, "filter"])

df["w_separation"] = 1.0

for i in range(len(df)):
    df.loc[i, "w_separation"] = calculate_w_separation(df.loc[i, "rho"], df.loc[i, "tel"], df.loc[i, "wavelength"])

df["W"] = df["w_technique"] * df["w_separation"] * df["sqrt_n"] * df["w_quality"]

print(df[['date', 'tech', 'w_technique', 'w_separation', 'sqrt_n', 'w_quality', 'W']])


for t in df["tech"].unique():
    tech_rows = df[df["tech"] == t]
    mean_w = np.nanmean(tech_rows["W"])
    std_w = np.nanstd(tech_rows["W"])
    count = tech_rows["W"].count()
    print(str(t) + ", mean weight: " + str(round(mean_w, 4)) + ", standard deviation: " + str(round(std_w, 4)) + ", count: " + str(count))

df.to_csv("wds_observation_weights.csv")
