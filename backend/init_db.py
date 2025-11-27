from core.db import Base, engine
from core.models import *

print("Creating tables in Cloud SQL...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")
