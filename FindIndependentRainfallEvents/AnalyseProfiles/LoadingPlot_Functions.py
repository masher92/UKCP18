import seaborn as sns


def plot_boxplot(data, ax):
    sns.boxplot(ax=ax, data=data, x='Loading_profile_molly',
            y='D50',  dodge=True) 
    
    
def plot_boxplot_by_season(data, ax):
    sns.boxplot(ax=ax, data=data, x='Loading_profile_molly',
            y='D50',  hue='season', dodge=True)       
