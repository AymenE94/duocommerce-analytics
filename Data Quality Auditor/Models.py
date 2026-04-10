
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import date
from typing import Optional



class RFMRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id_client: int = Field(..., gt=0)
    nom: str = Field(..., min_length=1)
    segment: int = Field(..., ge=0, le=3)
    segment_nom: str
    recence: int = Field(..., ge=0)
    frequence: int = Field(..., ge=0)
    montant: float = Field(..., ge=0)




class DimClientsRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clients_id_original: int = Field(..., gt=0)
    email: Optional[EmailStr] = None
    date_inscription: date
    ville: str


    

class DimProduitsRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    produit_id_original: int  = Field(..., gt=0)
    prix: float = Field(...,gt=0)
    cout_production: float = Field(..., ge=0)


class FctCommandesRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id_client: int = Field(..., gt=0)
    id_produit: int = Field(..., gt=0)
    quantite: int = Field(..., gt=0)
    prix_unitaire: float = Field(...,ge=0)
    montant_total: float = Field(..., ge=0)
