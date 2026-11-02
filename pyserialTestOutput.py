import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('ServoAngleTest.csv')

# extract raw data from csv
x = np.array(df['PulseWidth'].to_list())
y = np.array(df['Angle'].to_list())

# polyfit
z = np.polyfit(x, y, 1)
y_fit = z[1] + x * z[0]
print(z)
# calculate rmse
rmse = np.sqrt(np.mean((y_fit - y) ** 2))
print(rmse)

# draw graphs
plt.plot(x, y, '.', x, y_fit, '-')
plt.show()



