from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

rps = [2,10,20,30,50,75,100,150,200,500,1000]
all_rainfall = pd.DataFrame()
for rp in rps:
    rp_rainfalls = design_rainfall_by_rp[str(rp) + ' year rainfall (mm)']
    rp_rainfalls_t = rp_rainfalls.T  
    rp_rainfalls_t.rename(columns=rp_rainfalls_t.iloc[0], inplace = True)
    rp_rainfalls_t = rp_rainfalls_t[1:22]
    rp_rainfalls_t = rp_rainfalls_t.reset_index(drop = True)
    rp_rainfalls_t.columns = [str(col) + '_{}'.format(rp) for col in rp_rainfalls_t.columns]
    all_rainfall = pd.concat([all_rainfall, rp_rainfalls_t], axis=1)


all_rainfall = pd.concat([all_rainfall,catchments_info], axis =1)

####################################################################################
############## Cretaing PC from rainfall values
features = all_rainfall.columns[0:4224]
# Separating out the features
x = all_rainfall.loc[:, features].values
# Separating out the target
y = all_rainfall.loc[:,['SAAR']].values
# Standardizing the features
x = StandardScaler().fit_transform(x)


pca = PCA(n_components=2)
principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents
             , columns = ['principal component 1', 'principal component 2'])

finalDf = pd.concat([principalDf, all_rainfall[['SAAR']]], axis = 1)
finalDf = pd.concat([principalDf, all_rainfall[['Northing']]], axis = 1)
pca.explained_variance_ratio_

finalDf['SAAR_Cat'] = pd.cut(finalDf['SAAR'], bins=[600, 700, 800,900], labels=['low', 'medium', 'high'])


fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)
targets = ['low', 'medium', 'high']
colors = ['r', 'g', 'b']
# for target, color in zip(targets,colors):
#     indicesToKeep = finalDf['SAAR_Cat'] == target
#     ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1']
#                 , finalDf.loc[indicesToKeep, 'principal component 2']
#                 , c = color
#                 , s = 50)
ax.scatter(finalDf['principal component 1'], finalDf['principal component 2']
            , c = finalDf['Northing']
            , s = 50)
plt.colorbar()
ax.legend()
ax.grid()



sns.scatterplot(data=finalDf, x='principal component 1', y='principal component 2',
                     hue = 'Northing', s= 100,
                     palette = 'rainbow')



####################################################################################
############## Cretaing PC from catchment descriptors 

# Extract from catchments info dataframe the variables of interest
cols= ['name', 'AREA', 'ALTBAR', 'BFIHOST','DPSBAR', 'FARL', 'LDP',
       'PROPWET', 'SAAR','URBEXT2000', 'Easting','Northing']
catchments_info_filtered = catchments_info[cols]


features = catchments_info_filtered.columns[1:]
# Separating out the features
x = catchments_info_filtered.loc[:, features].values
# Standardizing the features
x = StandardScaler().fit_transform(x)


pca = PCA(n_components=3)
principalComponents = pca.fit_transform(x)
# principalDf = pd.DataFrame(data = principalComponents
#              , columns = ['principal component 1', 'principal component 2'])
# Eigenvalues 
pca.explained_variance_
pca.explained_variance_ratio_
pca.explained_variance_ratio_.sum()
loadings = pd.DataFrame(pca.components_.T, columns=['PC1', 'PC2', 'PC3'], index=features)
loadings
loadings = abs(loadings['PC1']).sort_values(ascending = False)

df.reindex(df.b.abs().sort_values().index)



finalDf = pd.concat([principalDf, all_rainfall[['SAAR', 'name']]], axis = 1)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax = sns.scatterplot(data=finalDf, x='principal component 1', y='principal component 2',
                style = 'name',  markers = catchment_markers_dict, hue = 'name', s= 100, 
                palette = my_pal)
ax.tick_params(axis='both', which='major')
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[1:], labels=labels[1:],bbox_to_anchor=(1., 1.05), fontsize = '8')

fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)
targets = ['low', 'medium', 'high']
colors = ['r', 'g', 'b']
# for target, color in zip(targets,colors):
#     indicesToKeep = finalDf['SAAR_Cat'] == target
#     ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1']
#                 , finalDf.loc[indicesToKeep, 'principal component 2']
#                 , c = color
#                 , s = 50)
ax.scatter(finalDf['principal component 1'], finalDf['principal component 2']
            , c = finalDf['SAAR']
            , s = 50)
plt.colorbar()
ax.legend()
ax.grid()






sns.scatterplot(data=finalDf, x='principal component 1', y='20.25_2',s= 100,
                     palette = 'rainbow')


spike_cols = [col for col in all_rainfall if col.startswith('8.25')]
print(spike_cols)
df_cols = all_rainfall[spike_cols]

finalDf = pd.concat([df_cols, principalDf[['principal component 1']]], axis = 1)

corrs = finalDf[finalDf.columns].corr()['principal component 1'][:]
            




# Normalise
for col in spike_cols:
    print(col)
    finalDf[col] = finalDf[col]/finalDf[col].max() 


fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1) 
for col in spike_cols[4:6]:
   ax.scatter(finalDf['principal component 1'], finalDf[col], s = 50) 



sns.scatterplot(data=finalDf, x='principal component 1', y='20.25_2',s= 100,
                     palette = 'rainbow')





sns.scatterplot(data=finalDf, x='principal component 1', y='principal component 2',
                     hue = 'Northing', s= 100,
                     palette = 'rainbow')