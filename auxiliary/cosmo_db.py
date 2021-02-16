import pandas as pd
import numpy as np
from ..theory.cosmology import Cosmology, CosmologyCustomH
from .configs import cosmo_database, camb_outputs_path
from .helper_functions import generate_cosmo_identifier

class CosmoDB(object):

    def __init__(self):
        dtype = {'ID':np.int, 'path_root':'str', 'logs_path':'str', 'hash_value':'str', 'ran_TF':bool, 'successful_TF':bool, 'h':np.float64, 'omegaCDM':np.float64, 'omegaB':np.float64, 'omega_axion':np.float64, 'm_axion':np.float64, 'n_s':np.float64, 'A_s':np.float64, 'read_H':bool}
        columns = ['ID', 'path_root', 'logs_path', 'hash_value', 'ran_TF', 'successful_TF', 'h', 'omegaCDM', 'omegaB', 'omega_axion', 'm_axion', 'n_s', 'A_s', 'read_H']
        try:
            self.load()
        except FileNotFoundError:
            dict = {}
            for c in columns:
                dict[c] = pd.Series([], dtype=dtype[c])
            self.__db = pd.DataFrame(dict)
            self.__db = self.__db.set_index('ID')

    def load(self):
        self.__db = pd.read_csv(cosmo_database)

    def save(self):
        self.__db.to_csv(cosmo_database)

    def add(self, cosmo):
        """

        :type cosmo: Cosmology
        """
        if np.any(generate_cosmo_identifier(cosmo) == self.__db['hash_value']):
            db_entry = self.__db.loc[generate_cosmo_identifier(cosmo) == self.__db['hash_value']].iloc[0]
        else:

            logs_path = camb_outputs_path+"logs/camb_log_ID={}.log".format(len(self.__db))
            output_path = camb_outputs_path+"camb_out_ID={}".format(len(self.__db))
            self.__db.loc[len(self.__db)] = {'path_root': output_path,'logs_path': logs_path, 'hash_value': generate_cosmo_identifier(cosmo), 'ran_TF': False, 'successful_TF': False, 'h': cosmo.h, 'omegaCDM': cosmo.omegaCDM, 'omegaB': cosmo.omegaB, 'omega_axion': cosmo.omega_axion, 'm_axion': cosmo.m_axion, 'n_s': cosmo.n_s, 'A_s': cosmo.A_s, 'read_H': (type(cosmo) == CosmologyCustomH) }
            db_entry = self.__db.iloc[-1]

        return db_entry.name, db_entry['ran_TF'], db_entry['successful_TF'], db_entry['path_root'], db_entry['logs_path']

    def set_run(self, ID, success):
        self.__db[ID]['ran_TF'] = True
        self.__db[ID]['successful_TF'] = success

    def set_run_by_cosmo(self, cosmo, success):
        id, ran_TF, success_TF, out_path, log_path = self.get_by_cosmo(cosmo)
        self.set_run(id, success)

    def get_by_id(self, ID, get_cosmo=False):
        try:
            db_entry = self.__db.loc[ID]
            if not get_cosmo:
                return db_entry.name, db_entry['ran_TF'], db_entry['successful_TF'], db_entry['path_root'], db_entry['logs_path']
            else:
                cosmo = Cosmology.generate(m_axion=db_entry['m_axion'], omega_axion=db_entry['omega_axion'], h=db_entry['h'], omega_cdm=db_entry['omegaCDM'], omega_b=db_entry['omegaB'], n_s=db_entry['n_s'], A_s=db_entry['A_s'], read_H_from_file=db_entry['read_H'])
                return cosmo, db_entry.name, db_entry['ran_TF'], db_entry['successful_TF'], db_entry['path_root'], db_entry['logs_path']
        except KeyError as ex:
            print(str(ex))
            return False

    def get_by_cosmo(self, cosmo):
        if np.any(generate_cosmo_identifier(cosmo) == self.__db['hash_value']):
            db_entry = self.__db.loc[generate_cosmo_identifier(cosmo) == self.__db['hash_value']].iloc[0]
            return db_entry.name, db_entry['ran_TF'], db_entry['successful_TF'], db_entry['path_root'], db_entry['logs_path']
        else:
            return False

    def get_by_idenifier(self, ident):
        if np.any(ident == self.__db['hash_value']):
            db_entry = self.__db.loc[ident == self.__db['hash_value']].iloc[0]
            return db_entry.name, db_entry['ran_TF'], db_entry['successful_TF'], db_entry['path_root'], db_entry['logs_path']
        else:
            return False


