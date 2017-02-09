import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

#mu, sigma = 100, 15
#x = mu + sigma * np.random.randn(10000)
filename = "/home/kanayama/ETL_sample/images/ETL1/0/ETL1_1_1002_0.png"
img = np.array(Image.open(filename))
x = img.flatten()

fig = plt.figure()
ax = fig.add_subplot(1,1,1)

ax.hist(x, bins=256)
ax.set_title(filename)
ax.set_xlabel('gray value')
ax.set_ylabel('freq')
plt.savefig('test.png')
