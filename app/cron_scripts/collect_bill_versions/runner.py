from tasks.congress_api_tasks import get_versions

def run():
    versions = ['as', 'ash', 'ath', 'ats', 'cdh', 'cds', 'cph', 'cps', 'eah', 'eas', 'eh', 'eph', 'enr', 'es',
                    'fah', 'fph', 'fps', 'hdh', 'hds', 'ih', 'iph', 'ips', 'is', 'lth', 'lts', 'oph', 'ops', 'pav',
                    'pch', 'pcs', 'pp', 'pap', 'pwah', 'rah', 'ras', 'rch' 'rcs', 'rdh', 'reah', 'res', 'renr', 'rfh',
                    'rfs', 'rh','rih', 'ris', 'rs', 'rth', 'rts', 'sas', 'sc']
    doc_classes = ['hconres', 'hjres', 'hr', 'hres', 's', 'sconres', 'sjres', 'sres']
    
    for version in versions:
        for doc_class in doc_classes:
            get_versions.apply_async((117, version, doc_class, 0,))
        