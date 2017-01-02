#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``io_dfs``
================================
"""
from os.path import basename,exists
import pandas as pd
import numpy as np
from dms2dfe.lib.io_nums import is_numeric

def set_index(data,col_index):
    if col_index in data:
        data=data.reset_index().set_index(col_index)
        if 'index' in data:
            del data['index']
        return data
    elif data.index.name==col_index:
        return data


# dfs
def concat_cols(df1,df2,idx_col,df1_cols,df2_cols,
                df1_suffix,df2_suffix):
#     df1_cols=[ for col in df1_cols]
    df1=df1.set_index(idx_col)
    df2=df2.set_index(idx_col)    
    combo=pd.concat([df1.loc[:,df1_cols],df2.loc[:,df2_cols]],axis=1)
    # find common columns and rename them
    common_cols=[col for col in df1_cols if col in df2_cols]
    for col in common_cols:
        df1_cols[df1_cols.index(col)]="%s%s" % (col,df1_suffix)
        df2_cols[df2_cols.index(col)]="%s%s" % (col,df2_suffix)
    combo.columns=df1_cols+df2_cols
    combo.index.name=idx_col
    return combo

def get_colmin(data):
    data=data.T
    colmins=[]
    for col in data:
        colmins.append(data[col].idxmin())
    return colmins

def fhs2data_combo(fhs,cols,index,labels=None,col_sep=': '):
    if labels is None:
        labels=[basename(fh) for fh in fhs]
    for fhi,fh in enumerate(fhs):
        label=labels[fhi]
        data=pd.read_csv(fh).set_index(index)
        if fhi==0:
            data_combo=pd.DataFrame(index=data.index)
            for col in cols:
                data_combo.loc[:,'%s%s%s' % (label,col_sep,col)]=data.loc[:,col]
        else:
            for col in cols:
                data_combo.loc[:,'%s%s%s' % (label,col_sep,col)]=data.loc[:,col]
    return data_combo

def rename_cols(df,names,renames=None,prefix=None,suffix=None):
    if not prefix is None:
        renames=[ "%s%s" % (prefix,s) for s in names]
    if not suffix is None:    
        renames=[ "%s%s" % (s,suffix) for s in names]
    if not renames is None:
        for i,name in enumerate(names):
#             names=[renames[i] if s==names[i] else s for s in names]    
            rename=renames[i]    
            df.loc[:,rename]=df.loc[:,name]
        df=df.drop(names,axis=1)
        return df 


def debad(data_all,axis,condi="any",bad=0):
    """
    This removes rows with any np.nan value/s.  
    condi: usage cols,rows = 'all any'
    
    :param data_all: input dataframe.
    :param condi: conditions for deletion of rows ["any": if any element is nan ,default | "all" : if all elements are nan | "any|all<SPACE>any|all" : condition for columns<SPACE>rows] 
    :returns data_all: output dataframe.
    """
    import logging
    if not ((is_numeric(bad)) or (bad in ['nan','null'])):
        logging.error('bad not recognised: %s' % bad)        
    logging.info("denan: original: rows=%s cols=%s" % data_all.shape)

    if axis=='both':
        condi_cols=condi.split(' ')[0]
        condi_rows=condi.split(' ')[1]
    if axis=='rows' or axis==0:
        condi_rows=condi        
    if axis=='cols' or axis==1:
        condi_cols=condi
    if axis=='cols' or axis==1 or axis=='both':
        data_all_use=data_all.copy()
        keep_bool=[]
        for col in data_all_use:
            if condi_cols=="any":
                if (bad=='nan') or (bad=='null'):
                    keep_bool.append(all(~(pd.isnull(data_all_use.loc[:,col]))))
                else:
                    keep_bool.append(all(~(data_all_use.loc[:,col]==bad)))
            if condi_cols=="all":
                if (bad=='nan') or (bad=='null'):
                    keep_bool.append(any(~(pd.isnull(data_all_use.loc[:,col]))))
                else:
                    keep_bool.append(any(~(data_all_use.loc[:,col]==bad)))
        data_all=data_all.loc[:,keep_bool]
        logging.info("denan: cols:      rows=%s cols=%s" % data_all.shape)
    if axis=='rows' or axis==0 or axis=='both':
        data_all_use=data_all.copy()
        keep_bool=[]
        for rowi in range(len(data_all_use)):
            if condi_rows=="any":
                if (bad=='nan') or (bad=='null'):
                    keep_bool.append(all(~pd.isnull(data_all_use.iloc[rowi,:])))
                else:
                    keep_bool.append(all(~(data_all_use.iloc[rowi,:]==bad)))
            if condi_rows=="all":
                if (bad=='nan') or (bad=='null'):
                    keep_bool.append(any(~pd.isnull(data_all_use.iloc[rowi,:])))
                else:
                    keep_bool.append(any(~(data_all_use.iloc[rowi,:]==bad)))
        data_all=data_all.loc[keep_bool,:]
        logging.info("denan: rows:      rows=%s cols=%s" % data_all.shape)
    return data_all

def denan(data_all,axis,condi="any"):
    return debad(data_all,axis,condi="any",bad='nan')

def denanrows(data_all):
    return debad(data_all,axis=0,condi="any",bad='nan')

    # """
    # This removes rows with any np.nan value/s.  
    # condi: usage cols,rows = 'all any'
    
    # :param data_all: input dataframe.
    # :param condi: conditions for deletion of rows ["any": if any element is nan ,default | "all" : if all elements are nan | "any|all<SPACE>any|all" : condition for columns<SPACE>rows] 
    # :returns data_all: output dataframe.
    # """
    # import logging
    # logging.info("denan: original: rows=%s cols=%s" % data_all.shape)

    # if axis=='both':
    #     condi_cols=condi.split(' ')[0]
    #     condi_rows=condi.split(' ')[1]
    # if axis=='rows' or axis==0:
    #     condi_rows=condi        
    # if axis=='cols' or axis==1:
    #     condi_cols=condi
    # if axis=='cols' or axis==1 or axis=='both':
    #     data_all_use=data_all.copy()
    #     keep_bool=[]
    #     for col in data_all_use:
    #         if condi_cols=="any":
    #             keep_bool.append(all(~pd.isnull(data_all_use.loc[:,col])))
    #         if condi_cols=="all":
    #             keep_bool.append(any(~pd.isnull(data_all_use.loc[:,col])))
    #     data_all=data_all.loc[:,keep_bool]
    #     logging.info("denan: cols:      rows=%s cols=%s" % data_all.shape)
    # if axis=='rows' or axis==0 or axis=='both':
    #     data_all_use=data_all.copy()
    #     keep_bool=[]
    #     for rowi in range(len(data_all_use)):
    #         if condi_rows=="any":
    #             keep_bool.append(all(~pd.isnull(data_all_use.iloc[rowi,:])))
    #         if condi_rows=="all":
    #             keep_bool.append(any(~pd.isnull(data_all_use.iloc[rowi,:])))
    #     data_all=data_all.loc[keep_bool,:]
    #     logging.info("denan: rows:      rows=%s cols=%s" % data_all.shape)
    # return data_all
