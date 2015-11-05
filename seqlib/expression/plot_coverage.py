import argparse
from gtf_to_genes import *
import numpy as np
import scipy.stats as scp_stats
import pandas as pd

import pysam_ext.pysam_ext as pysam_ext
from coveragedata import CoverageData

import logging
import pysam
import pdb
import math
import time


def get_polygon(d, s, e, height=1):
    w = height/2.0
    dicts = [d.copy() for i in range(4)]
    dicts[0].update({"x":s,
                     "y":-w})
    dicts[1].update({"x":s,
                     "y":w})
    dicts[2].update({"x":e,
                     "y":w})
    dicts[3].update({"x":e,
                     "y":-w})
    return dicts

def get_gene_model(cvg_obj):
    
    outrows = []
    for i,e in enumerate(cvg_obj.UTR_5p_exons):
        s,e = e[0], e[1]
        outrows.extend(get_polygon({"type":"UTR_5p", "id":"UTR_5p_%d"%i}, s,e))
        
    for i,e in enumerate(cvg_obj.UTR_3p_exons):
        s,e = e[0], e[1]
        outrows.extend(get_polygon({"type":"UTR_3p", "id":"UTR_3p_%d"%i}, s,e))

    for i,e in enumerate(cvg_obj.coding_exons):
        s,e = e[0], e[1]
        outrows.extend(get_polygon({"type":"CDS", "id":"CDS_%d"%i}, s,e, height=2))
         
        outrows.extend(get_polygon({"type":"gene_body", "id":"gene_body"}, cvg_obj.g.beg, cvg_obj.g.end, height=.1))
    
    return outrows
    
    
if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--fn_gtf_index", required=True)
    
    parser.add_argument("--fn_bams", required=True, nargs="+")
    parser.add_argument("--samples", required=True, nargs="+")
    parser.add_argument("--celltypes", required=True, nargs="+")
    parser.add_argument("--times", required=True, nargs="+")

    parser.add_argument("--fn_out_cvg", required=True)
    parser.add_argument("--fn_out_gene_model", required=True)
    parser.add_argument("--gene", required=True, default=None)
    parser.add_argument("--gtf_ID", required=True)

    parser.add_argument("--fn_logfile", default="/dev/null")

    o = parser.parse_args()

    logger = logging.getLogger(o.fn_logfile)
    
    bamfiles = {}
    times = {}
    celltypes = {}
    for i, sample in enumerate(o.samples):
        bamfiles[sample] = pysam.AlignmentFile(o.fn_bams[i], 'rb')
        times[sample] = o.times[i]
        celltypes[sample] = o.celltypes[i]
        
    species_id, gtf_path, genes = get_indexed_genes_for_identifier(o.fn_gtf_index,
                                                                   logger, 
                                                                   o.gtf_ID)
    
    g_obj = None
    for g in genes['protein_coding']:
        if o.gene in g.names:
            g_obj = g
            break
    
    assert g_obj!=None, "gene name {name} not found".format(o.gene)
    
    bp_cov_tables = []
    for sample in o.samples:
        cvg_obj = CoverageData(g_obj)
        bp_cvg_rows = cvg_obj.get_cvg(bamfiles[sample])
        bp_cvg_rows = cvg_obj.get_bp_cvg_dicts()
        T = pd.DataFrame(bp_cvg_rows)
        T['sample'] = sample
        T['time'] = times[sample]
        T['celltype'] = celltypes[sample]
        bp_cov_tables.append(T)
    
    T = pd.concat(bp_cov_tables)
    T.to_csv(o.fn_out_cvg, index=False, sep="\t")
    
    gene_model_rows = get_gene_model(cvg_obj)
    T_g = pd.DataFrame(gene_model_rows)
    T_g.to_csv(o.fn_out_gene_model, sep="\t", index=False)
     

