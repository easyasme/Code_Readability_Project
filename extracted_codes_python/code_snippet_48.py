#!/usr/bin/env python
# coding: utf-8

# In[43]:


import numpy as np
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt


# In[44]:


from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
plt.rcParams['figure.figsize'] = (16, 9)
plt.style.use('ggplot')
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score


# In[45]:


data = pd.read_csv("./hotel_bookings.csv")
data.shape


# In[46]:


data.head()


# In[47]:


data.describe()


# In[48]:


data.drop(['hotel'],1).hist()
plt.show()


# In[51]:


filtered_data = data[(data['is_canceled'] == 0) & (data['adults'] >= 2)]
 
colores=['orange','blue']
tamanios=[30,60]
 
f1 = filtered_data['is_canceled'].values
f2 = filtered_data['adults'].values
 

asignar=[]
for index, row in filtered_data.iterrows():
    if(row['is_canceled']==0):
        asignar.append(colores[0])
    else:
        asignar.append(colores[1])
    
plt.scatter(f1, f2, c=asignar, s=tamanios[0])

plt.show()


# In[52]:


dataX =filtered_data[['is_canceled']]
X_train = np.array(dataX)
y_train = filtered_data['adults'].values
 

regr = linear_model.LinearRegression()
 

regr.fit(X_train, y_train)
 

y_pred = regr.predict(X_train)
 

print('Coefficients: \n', regr.coef_)

print('Independent term: \n', regr.intercept_)

print("Mean squared error: %.2f" % mean_squared_error(y_train, y_pred))

print('Variance score: %.2f' % r2_score(y_train, y_pred))


# In[53]:


y_Dosmil = regr.predict([[2000]])
print(int(y_Dosmil))


# In[54]:


x = np.arange(-11,11)
y = 5.69765366*x + 11200.303223074163
plt.plot(x,y)


# In[ ]:




