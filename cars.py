# %%
import re
import pandas as pd
# %%
# Import Data
df = pd.read_csv('fullspecs.csv')
df = df.T
df.columns = df.iloc[0]
df = df.iloc[1:]
df = df.reset_index(drop=False).rename(columns={"index": "Vehicle"})
# %%
# Drop columns with gt X% NA values
df = df.loc[:, [col for col, val in df.isna().sum().items() if val/len(df) < .2]]
# %%
# Drop Electric Vehicles
df = df[~df['Engine Type'].str.contains("electric", case=False, na=False)]
# %%
# Keep subset of useful cols
cols_to_keep = [
    'Vehicle',
    'Passenger Doors',
    'EPA Class',
    'Body Style',
    'Drivetrain',

    'Engine',
    'Engine Type',
    'Displacement',
    'SAE Net Horsepower @ RPM',
    'SAE Net Torque @ RPM',

    'Transmission',
    'First Gear Ratio (:1)',
    'Second Gear Ratio (:1)',
    'Third Gear Ratio (:1)',
    'Fourth Gear Ratio (:1)',
    'Reverse Ratio (:1)',

    'Front Brake Rotor Diam x Thickness (in)',
    'Rear Brake Rotor Diam x Thickness (in)',
    'Turning Diameter - Curb to Curb (ft)',
    'Front Tire Size',
    'Rear Tire Size',
    'Front Wheel Size (in)',
    'Rear Wheel Size (in)',
    'Suspension Type - Front',
    'Suspension Type - Rear',
    'Fuel Tank Capacity, Approx (gal)',
    'EPA Fuel Economy Est - City (MPG)',
    'EPA Fuel Economy Est - Hwy (MPG)',
]
df = df[cols_to_keep]
# %%
# Extract engine displacement
def extract_displacement(s):
    try:
        search = re.search('(^\d{1,2}.\d{1,2})', s, re.IGNORECASE)
        if search:
            return search.group(1)
        else:
            print(f'no match for {s}')
            return None
    except:
        return None
df['displacement'] = df['Displacement'].apply(extract_displacement)
df = df.dropna(subset=['displacement'])
df.displacement = pd.to_numeric(df.displacement)
# %%
# extract engine type
def extract_engine_type(s):
    try:
        s = s.lower()
        # Repace flat with "f"
        s = s.replace("flat", "f")
        search = re.search('([v|i|f|w|h|l][-|" "]?\d{1,2})', s, re.IGNORECASE)
        if search:
            type = search.group(1)
            type = type.replace("h", "f")
            type = type.replace("l", 'i')
            type = type.replace("-", "").replace(" ","")
            return type
        else:
            return None
    except:
        return None
df['engine_type'] = df['Engine Type'].apply(extract_engine_type)
df = df.dropna(subset=['engine_type'])
# %%
# Extract engine cylinder count
def extract_cylinders(s):
    try:
        search = re.search('(\d{1,2})', s, re.IGNORECASE)
        if search:
            return search.group(1)
        else:
            return None
    except:
        return None

df['cylinders'] = df.engine_type.apply(extract_cylinders)
df = df.dropna(subset=['cylinders'])
df.cylinders = pd.to_numeric(df.cylinders)
# %%
# Extract engine configuration type, e.g. "V"
def extract_engine_config(s):
    try:
        search = re.search('(\D{1})', s, re.IGNORECASE)
        if search:
            return search.group(1)
        else:
            return None
    except:
        return None
df['engine_config'] = df.engine_type.apply(extract_engine_config)
df = df.dropna(subset=['engine_config'])
# %%
# Convert HP and TQ into numeric
def extract_power(s):
    try:
        search = re.search('(\d{1,4})', s, re.IGNORECASE)
        if search:
            return search.group(1)
        else:
            return None
    except:
        return None

df['hp'] = df['SAE Net Horsepower @ RPM'].apply(extract_power)
df['tq'] = df['SAE Net Torque @ RPM'].apply(extract_power)
df = df.dropna(subset=['hp', 'tq'])

df.hp = pd.to_numeric(df.hp)
df.tq = pd.to_numeric(df.tq)
# %%
# Save to CSV
df[['Vehicle', 'engine_type', 'engine_config', 'cylinders', 'displacement', 'hp', 'tq']].to_csv('engine.csv')
# %%
# %%
import plotly.express as px
# %%
e = pd.read_csv('engine.csv')
e = e.drop(columns=['Unnamed: 0'])
# %%
fig = px.scatter(e, x="displacement", y="hp", color="engine_config", trendline="ols")
fig.show()

results = px.get_trendline_results(fig)
results = results.iloc[0]["px_fit_results"].summary()
print(results)

'''
HP:
I: 45.6 + d * 81.8
V: 43.3 + d * 114.6
F: -157 + d * 142.4 

For a given d, V > I
'''
# %%
fig = px.scatter(e, x="displacement", y="tq", color="engine_config", trendline="ols")
fig.show()

results = px.get_trendline_results(fig)
results = results.iloc[0]["px_fit_results"].summary()
print(results)

'''
TQ:
I: 48.2  + d * 83.6
V: 57.2  + d * 67.8
F: -81.5 + d * 108.9

For a given d, V > I
'''
# %%
e['hp_cyl'] = e.hp / e.cylinders
# %%
px.histogram(e, y="hp_cyl", color="engine_config", marginal="box")
# %%
px.scatter(e, x='hp_cyl', y='hp', color='cylinders')
# %%
px.scatter(e, x='displacement', y='hp', trendline="ols")
# %%
e['d_c'] = e.displacement / e.cylinders
e['hp_d'] = e.hp / e.displacement
# %%
e[['Vehicle', 'hp_d', 'hp', 'displacement']].sort_values(by='hp_d', ascending=False)[:25]
# %%
e[['Vehicle', 'hp_d', 'hp', 'displacement']].sort_values(by='hp_d', ascending=True)[:25]
# %%
