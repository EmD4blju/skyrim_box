from sqlmodel import Session, create_engine, select
from models import User, Item, Comment

DATABASE_URL = "postgresql+psycopg2://skyrim_user:skyrim_password@localhost:5432/skyrim_db"
engine = create_engine(DATABASE_URL)

def populate_data():
    with Session(engine) as session:
        # Check if items already exist
        existing_items = session.exec(select(Item)).first()
        if existing_items:
            print("Data already exists. Skipping population.")
            return

        print("Populating database with Skyrim sample data...")

        # Create Users
        user1 = User(username="Dragonborn")
        user2 = User(username="Lydia")
        
        session.add(user1)
        session.add(user2)
        
        # Create Items
        item1 = Item(
            name="Iron Sword", 
            description="A standard iron sword. Reliable, but dulls quickly."
        )
        item2 = Item(
            name="Sweetroll", 
            description="A pastry, sweet and delicious. Often stolen."
        )
        item3 = Item(
            name="Wabbajack", 
            description="A Daedric artifact of Sheogorath that casts unpredictable spells."
        )
        
        session.add(item1)
        session.add(item2)
        session.add(item3)
        
        # Commit to get the IDs for our objects
        session.commit()
        
        # Refresh to ensure we have the IDs loaded in the objects
        session.refresh(user1)
        session.refresh(user2)
        session.refresh(item1)
        session.refresh(item2)
        session.refresh(item3)

        # Create Comments
        comment1 = Comment(content="I used this at lower levels, very reliable.", user_id=user1.id, item_id=item1.id)
        comment2 = Comment(content="Let me guess, someone stole yours?", user_id=user2.id, item_id=item2.id)
        comment3 = Comment(content="CHEESE FOR EVERYONE!", user_id=user1.id, item_id=item3.id)

        session.add(comment1)
        session.add(comment2)
        session.add(comment3)
        
        session.commit()

        print("Database successfully populated!")

if __name__ == "__main__":
    populate_data()
