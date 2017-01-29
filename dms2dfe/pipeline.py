#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
from os.path import exists,splitext
import logging
from dms2dfe import configure, ana0_fastq2dplx,ana0_fastq2sbam,ana0_getfeats,ana1_sam2mutmat,ana2_mutmat2fit,ana3_fit2comparison,ana4_modeller,ana4_plotter
    
# GET INPTS    
def main(prj_dh):
    """
    This runs all analysis steps in tandem.

    From bash command line,

    .. code-block:: text

        python path/to/dms2dfe/pipeline.py path/to/project_directory
        
    :param prj_dh: path to project directory.
    
    Outputs are created in `prj_dh` in directories such as `data_lbl` , `data_fit` , `data_comparison` etc. as described in :ref:`io`.

    Optionally, In addition to envoking `pipeline`, individual programs can be accessed separately as described in :ref:`programs` section.
    Also submodules can be accessed though an API, as described in :ref:`api` section.
    Also the scripts can be envoked through bash from locally downloaded `dms2dfe` folder.

    """
    logging.info("start")
    if exists(prj_dh) :
        configure.main(prj_dh,"deps")
        configure.main(prj_dh)          
        # run modules
        # ana0_getfeats.main(prj_dh)
        # ana0_fastq2dplx.main(prj_dh)
        # ana0_fastq2sbam.main(prj_dh)
        # ana1_sam2mutmat.main(prj_dh)
        ana2_mutmat2fit.main(prj_dh)
        ana4_modeller.main(prj_dh)
        # ana3_fit2comparison.main(prj_dh)
        # ana4_plotter.main(prj_dh)    

        logging.info("Location of output data: %s/plots/aas/data_comparison" % (prj_dh))
        logging.info("Location of output visualizations: %s/plots/aas/" % (prj_dh))
        logging.info("For information about file formats of outputs, refer to http://kc-lab.github.io/dms2dfe .")
        logging.shutdown()
    else:
        configure.main(prj_dh)                  
    # sys.exit()
if __name__ == '__main__':
    main(sys.argv[1])