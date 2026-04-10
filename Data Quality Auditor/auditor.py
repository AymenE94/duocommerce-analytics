import pandas as pd
from pydantic import BaseModel, ValidationError
from ConfigDAC import DatabaseConfig
import json
import warnings
warnings.filterwarnings('ignore')

class GenericAuditor:
    def __init__(self, table_name: str, model_class: BaseModel):
        self.table_name = table_name
        self.model = model_class
        self.conn = DatabaseConfig.get_connection()
    
    def run_quick_audit(self, sample_size=1000):
       
        query = f"SELECT * FROM {self.table_name} LIMIT {sample_size}"
        print(f"🔍 Requête exécutée : {repr(query)}")
        df = pd.read_sql(query, self.conn)
        df = pd.read_sql(f"SELECT * FROM {self.table_name} LIMIT {sample_size}", self.conn)
        errors = []

        for _, row in df.iterrows():
            try:
                self.model(**row.to_dict())
            except ValidationError as e:
                errors.append({"row": row.to_dict(), "erorrs": e.erorrs()})
        
        print(f"📊 {self.table_name}: {len(df)-len(errors)}/{len(df)} lignes valides")
        return errors
    
    def close(self):
        if hasattr(self,'engine'):
            self.engine.dispose()
        elif hasattr(self, 'conn'):
            self.conn.close()