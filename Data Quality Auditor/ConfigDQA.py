import os
from dotenv import load_dotenv


load_dotenv()


class DatabaseConfig:
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT'))
    DB_NAME = os.getenv('DB_NAME')

    @classmethod
    def get_connection_string(cls):
        return f"postgresql+psycopg2:// {cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"


    @classmethod
    def get_engine(cls):
        from sqlalchemy import create_engine
        return create_engine(cls.get_connection_string())
    
   
   
    @classmethod
    def get_connection(cls):
        import psycopg2 
        return psycopg2.connect(
            host=cls.DB_HOST,
            port=cls.DB_PORT,
            dbname=cls.DB_NAME,
            user=cls.DB_USER,
            password=cls.DB_PASSWORD
        )
    

if __name__ == "__main__":
    try:
        conn = DatabaseConfig.get_connection()
        print("✅ Connexion PostgreSQL réussie !")
        conn.close()
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
