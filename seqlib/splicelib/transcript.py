
class Transcript:

    def __init__(self, **kwargs):
        self.feature_ID = kwargs['feature_ID'] 
        self.gene_name = kwargs['gene_name'] 
        self.gene_ID = kwargs['gene_ID'] 
        self.g_start = kwargs['g_start'] 
        self.g_end = kwargs['g_end'] 
        self.exons = kwargs['exons']
        self.strand = kwargs['strand']
    
    def print_out(self):
        print self.feature_ID
        print "\t", self.gene_name
        print "\t", self.gene_ID 
        print "\t", self.g_start
        print "\t", self.g_end
        print "\t", self.exons
        print "\t", self.strand
    
    def get_all_3pSS(self, seq):

        for i in xrange(len(self.exons)-1):
            e1_e = self.exons[i][1]
            e2_s = self.exons[i+1][0]
            
            if self.strand == 1:
                alts = np.array([m.start() for m in re.finditer("AG",seq[e1_e:e2_s])])
            else:
                alts = np.array([m.start() for m in re.finditer("CT",seq[e1_e:e2_s])])
            return alts 
    
    def get_splice_junctions(self, _3p_to_5p, _5p_to_3p, _exon_3p_to_5p, _exon_5p_to_3p):
        """
        side effect - modifies passed in dicts
        5p_to_3p and 3p_to_5p are strand specific defaultdicts
                          ___
         ---->         5'/   \ 3' 
         |         -----/     \-----
                   ___
                3'/   \ 5'      <----
            -----/     \-----        |
        """
       
        for i in xrange(len(self.exons)-1):

            e1_s, e1_e = self.exons[i]
            e2_s, e2_e = self.exons[i+1]
            assert e1_s < e1_e and e2_s < e2_e
                
            if self.strand == 1:
                if not e2_s in _5p_to_3p[e1_e]:
                    _5p_to_3p[e1_e].append(e2_s)
                    _3p_to_5p[e2_s].append(e1_e)
                if not e1_e in _exon_5p_to_3p[e1_s]:
                    _exon_5p_to_3p[e1_s].append(e1_e)
                    _exon_3p_to_5p[e1_e].append(e1_s)
                #ret.append(tuple([seq[e1_e:e1_e+2],seq[e2_s-2:e2_s]]))
            else:
                if not e1_e in _5p_to_3p[e2_s]:
                    _5p_to_3p[e2_s].append(e1_e)
                    _3p_to_5p[e1_e].append(e2_s)
                if not e1_s in _exon_5p_to_3p[e1_e]:
                    _exon_5p_to_3p[e1_e].append(e1_s)
                    _exon_3p_to_5p[e1_s].append(e1_e)

                #ret.append(tuple([revcomp(seq[e2_s-2:e2_s]), revcomp(seq[e1_e:e1_e+2])])) 
        e1_s, e1_e = self.exons[-1]
        if self.strand == 1:
            _exon_5p_to_3p[e1_s].append(e1_e)
            _exon_3p_to_5p[e1_e].append(e1_s)
        else:
            _exon_5p_to_3p[e1_e].append(e1_s)
            _exon_3p_to_5p[e1_s].append(e1_e)
        
    @classmethod
    def init_from_feature(cls, feature):
        """
        assuming that all exons are orders s<e
        """
        kwargs = {
                  'feature_ID': feature.id,
                  'gene_name': feature.qualifiers['gene_name'][0],
                  'gene_ID': feature.qualifiers['geneID'][0],
                  'strand': feature.strand,
                  'g_start': feature.location.start.position,
                  'g_end': feature.location.end.position,
                  'exons':[[s.location.start.position,
                            s.location.end.position] for s in feature.sub_features]
                  }
                  
        return cls(**kwargs)


def fetch_trascripts(GFF_parser, limit_info={}):
    """
    NOT IMPLEMENTED
    limit_info={"gff_id": ["13"]}
    """

    GFF_parser = GFF.GFFParser()
    for rec in GFF_parser.parse_in_parts(open(o.fn_gff), limit_info=limit_info):
    #iterate over chromosomes
        contig_seq = fa.get_sequence(rec.id)
        
        D_to_A, A_to_D = get_donor_acceptor_pairs(rec)
        for feature in rec.features:
            if feature.type in ["mRNA", "transcript"]:
                t = transcript.init_from_feature(feature)
                alt_ss = t.get_all_3pSS(contig_seq)
                print alt_ss
