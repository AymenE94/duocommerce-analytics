
from auditor import GenericAuditor
from models import RFMRecord

auditeur = GenericAuditor("rfm_segments", RFMRecord)

erreurs= auditeur.run_quick_audit()

if erreurs:
    print(f"\n 📋 Détail des {len(erreurs)} premières erreurs :")
    for err in erreurs[:5]:
        print(f"  -Client {err['row_id']} : {err['errors']}")


auditeur.close()
