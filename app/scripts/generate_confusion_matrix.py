import seaborn as sn
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import cm

matplotlib.use('svg')

plt.ioff()
array = [[18/ (18 + 10 + 1), 10/ (18 + 10 + 1), 1/ (18 + 10 + 1)],
         [4/ (4 + 92 + 7), 92/ (4 + 92 + 7), 7/ (4 + 92 + 7)],
         [1/ (1 + 24 + 93), 24/ (1 + 24 + 93), 93/ (1 + 24 + 93)]]


df_cm = pd.DataFrame(array, index = ["neg", "neu", "pos"],
                  columns = ["neg", "neu", "pos"])
sn.heatmap(df_cm, annot=True, cmap=cm.get_cmap('Blues'), )
plt.xlabel('Predicted', fontsize = 15) # x-axis label with fontsize 15
plt.ylabel('Actual', fontsize = 15) # y-axis label with fontsize 15
plt.savefig('./scripts/conf_matrix.png')


