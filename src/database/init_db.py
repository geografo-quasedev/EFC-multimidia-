from . import Base, engine

def init_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_database()