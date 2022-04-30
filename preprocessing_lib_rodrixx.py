import pandas as pd
import numpy as np

from sklearn.base import BaseEstimator, TransformerMixin

class DropPlayersMultiTeams(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def _check_rk_season(self, df, rk_season_pairs):
        return df.apply(lambda x: (x['Rk'], x['Season']) in rk_season_pairs, axis = 1)
        
    def fit(self, X, y = None):
        return self
    
    def transform(self, X, y = None):   
        df_tot = X[X['Tm'] == 'TOT']
        rk_season_pairs = list(zip(df_tot['Rk'], df_tot['Season']))
        df_tot_full = X[self._check_rk_season(X, rk_season_pairs)]
        drop_index = df_tot_full[df_tot_full['Tm'] != 'TOT'].index
        return X.drop(drop_index).reset_index(drop = True)

class DropColumns(BaseEstimator, TransformerMixin):
    def __init__(self, cols_to_drop):
        self.cols_to_drop = cols_to_drop
    
    def fit(self, X, y = None):
        return self
    
    def transform(self, X, y = None):
        return X.drop(columns = self.cols_to_drop)

class SetIndex(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y = None):
        return self
    
    def transform(self, X, y = None):
        return X.set_index(['Rk', 'Season'], drop = False)

class DropPlayers(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.players_list = []
    
    def fit(self, X, y = None):
        self.players_list_ = X[['Player']]
        return self
    
    def transform(self, X, y = None):
        return X.drop('Player', axis = 1)

class OutlierFilter(BaseEstimator, TransformerMixin):
    '''
    Clase que filtra los outliers utilizando np.quantile()
    Los cuantiles a filtrar así como las columnas a filtrar son los parámetros de la clase.
    '''
    
    def __init__(self, q, col_to_filter):
        self.q = q
        self.col_to_filter = col_to_filter
        
    def fit(self, X, y = None):
        return self
    
    def transform(self, X, y = None):
        '''
        El método considera outlier a aquel cliente que es outlier en todas las columnas que le pasas.
        Es decir: si tiene que filtrar importe y número de pedidos, sólo va a eliminar aquellos clientes
        que son outlier tanto en importe como número de pedidos. Si eres outlier en importe pero no en pedido
        no se te va a filtrar del dataset.
        '''
        
        # lista vacía
        criteria_list = []
        
        # agregamos a la lista los clientes que no son outliers
        for col in self.col_to_filter:
            criteria = (X[col] > np.quantile(X[col], q = self.q)) & (X[col] < np.quantile(X[col], q = 1 - self.q))
            criteria_list.append(criteria)
            
        # si hay más de 1 columna
        if len(self.col_to_filter) > 1:
            
            # creamos el criterio global: es decir outlier en todas las columnas
            global_criteria = criteria_list[0]
            
            for criteria in criteria_list[1:]:
                global_criteria = global_criteria & criteria
                
        else:
            global_criteria = criteria_list[0]
            
        # filtramos nuestra dataframe
        X = X[global_criteria]
        
        # guardamos el índice como parámetro de la clase porque en caso contrario lo perderíamos.
        self.index = X.index
        
        return X