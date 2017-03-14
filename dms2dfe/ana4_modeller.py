#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igb.in>
# This program is distributed under General Public License v. 3.  

import sys
from os.path import exists,splitext,basename,dirname
from os import makedirs
from glob import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') # no Xwindows
from multiprocessing import Pool
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)
warnings.simplefilter(action = "ignore", category = DeprecationWarning)
# import logging
from dms2dfe.lib.io_strs import get_logger
logging=get_logger()
# logging.basicConfig(filename="dms2dfe_%s.log" % (make_pathable_string(str(datetime.datetime.now()))),level=logging.DEBUG)
from dms2dfe import configure
from dms2dfe.lib.io_dfs import set_index
from dms2dfe.lib.io_ml import data_fit2ml,get_cols_del,make_data_combo,data_combo2ml

def main(prj_dh,test=False):
    """
    This modules trains a Random Forest classifier with given data in `data_fit` format.
    
    This plots the results in following visualisations.
    
    .. code-block:: text
    
        ROC plots
        Relative importances of features
    
    :param prj_dh: path to project directory.
    """    
    logging.info("start")

    if not exists(prj_dh) :
        logging.error("Could not find '%s'" % prj_dh)
        sys.exit()
    configure.main(prj_dh)
    from dms2dfe.tmp import info
    cores=int(info.cores)
    if hasattr(info, 'mut_type'):
        mut_type=info.mut_type
    else:
        mut_type='single'    
    if hasattr(info, 'ml_input'):
        if info.ml_input=='FC':
            ml_input='FCA_norm'
        elif info.ml_input=='Fi':
            ml_input='FiA'
    else:
        ml_input='FCA_norm'    
    
    global prj_dh_global,data_feats,ml_input_global
    prj_dh_global=prj_dh
    ml_input_global=ml_input
    type_form="aas"
    if not exists("%s/plots/%s" % (prj_dh,type_form)):
        makedirs("%s/plots/%s" % (prj_dh,type_form))
    if not exists("%s/data_ml/%s" % (prj_dh,type_form)):
        makedirs("%s/data_ml/%s" % (prj_dh,type_form))
    data_feats=pd.read_csv("%s/data_feats/aas/data_feats_all" % (prj_dh))
    for col in get_cols_del(data_feats):
        del data_feats[col]
        
    if mut_type=='single':
        data_fit_keys = ["data_fit/%s/%s" % (type_form,basename(fh)) \
                         for fh in glob("%s/data_fit/aas/*" % prj_dh) \
                         if (not "inferred" in basename(fh)) and ("_WRT_" in basename(fh))]
        data_fit_keys = np.unique(data_fit_keys)

        if len(data_fit_keys)!=0:
            if test:
                pooled_io_ml(data_fit_keys[0])
                # for data_fit_key in data_fit_keys:
                #     pooled_io_ml(data_fit_key)
            else:
                pool_io_ml=Pool(processes=int(cores)) 
                pool_io_ml.map(pooled_io_ml,data_fit_keys)
                pool_io_ml.close(); pool_io_ml.join()
        else:
            logging.info("already processed")
    elif mut_type=='double':
        data_feats=set_index(data_feats,'mutids')
        data_fit_dh='data_fit_dm'
        data_fit_keys = ["%s/%s/%s" % (data_fit_dh,type_form,basename(fh)) \
                         for fh in glob("%s/%s/aas/*" % (prj_dh,data_fit_dh)) \
                         if (not "inferred" in basename(fh)) and ("_WRT_" in basename(fh))]
        data_fit_keys = np.unique(data_fit_keys)
        ycol=ml_input
        Xcols=data_feats.columns
        if len(data_fit_keys)!=0:
            for data_fit_key in data_fit_keys:
                data_fit_dm_fh='%s/%s' % (prj_dh,data_fit_key)
                data_combo_fh='%s/data_ml/aas/%s.combo' % (prj_dh,basename(data_fit_dm_fh))
                force=False
                if not exists(data_combo_fh) or force:
                    data_fit_dm=pd.read_csv(data_fit_dm_fh).set_index('mutids')
                    data_combo=make_data_combo(data_fit_dm,data_feats,ycol,Xcols)
                    if not exists(dirname(data_combo_fh)):
                        makedirs(dirname(data_combo_fh))
                    data_combo.to_csv(data_combo_fh)
                else:
                    data_combo=pd.read_csv(data_combo_fh).set_index('mutids')
                data_combo2ml(data_combo,basename(data_fit_dm_fh),dirname(data_combo_fh),dirname(data_combo_fh),
                            ycoln=ycol,col_idx='mutids',ml_type='cls',
                            middle_percentile_skipped=0.1,force=False,)
                
    logging.shutdown()

def pooled_io_ml(data_fit_key):
    """
    This module makes use of muti threading to speed up `dms2dfe.lib.io_ml.data_fit2ml`.     
    
    :param data_fit_key: in the form <data_fit>/<aas/cds>/<name of file>.
    """
    data_fit2ml(data_fit_key,prj_dh_global,data_feats,
               data_fit_col=ml_input_global,data_fit_col_alt=ml_input_global)
    
if __name__ == '__main__':
    if len(sys.argv)==3:
        if sys.argv[2]=='test':
            test=True
        else:
            test=False
    else:
        test=False
    main(sys.argv[1],test=test)