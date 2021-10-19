import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

files = os.listdir('by-type')
files.remove('.DS_Store')

#Results contains (year, type of course, count)
results=[]

#Need a list of years... for secret reasons.
years = ['2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']

for file in sorted(files):
    with open("by-type" + "/" + file, 'r') as f:
        for line in f:
            temp_a = int(line.split(',')[1])
            temp_b = int(line.split(',')[2])
            if temp_a > 0:
                results.append([file, "Technical", 1])
            elif temp_b > 0:
                results.append([file, "Non-Technical", 1])

#Now, let's make two plots

df = pd.DataFrame(columns=['year', 'type', 'count'])

for count,value in enumerate(results):
    item = results[count]
    df.loc[count] = (item[0], item[1], item[2])

total_tech = df.groupby(['year', 'type']).sum().reset_index()

plt.figure(figsize=(12,8))

splot=sns.barplot(x="year", y="count", hue="type", data=total_tech)
for p in splot.patches:
    splot.annotate(format(p.get_height(), '.0f'),
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha = 'center', va = 'center',
                xytext = (0, 5),
                textcoords = 'offset points')
plt.xlabel("Year", size=14)
plt.ylabel("Number of Classes by type", size=14)

plt.legend(loc='best')

plt.show()
