"""Script to verify the database migration was successful."""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from models import User

# Database URL from alembic.ini
DATABASE_URL = "your-database-url"


def verify_database_migration() -> None:
    """Verify that the database migration was successful."""
    print("Verifying database migration...")

    # Create engine
    engine = create_engine(DATABASE_URL)

    try:
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful!")

            # Check if users table exists
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'users'
            """))

            if result.fetchone():
                print("Users table exists!")
            else:
                print("Users table not found!")
                return

            # Check table structure
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))

            print("\nUsers table structure:")
            print("-" * 60)
            for row in result:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {row[3]}" if row[3] else ""
                print(f"  {row[0]:<15} {row[1]:<20} {nullable}{default}")

            # Check indexes
            result = conn.execute(text("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'users'
                ORDER BY indexname
            """))

            print("\nIndexes on users table:")
            print("-" * 60)
            for row in result:
                print(f"  {row[0]}: {row[1]}")

            # Check alembic version table
            result = conn.execute(text("""
                SELECT version_num
                FROM alembic_version
            """))

            version = result.fetchone()
            if version:
                print(f"\nCurrent migration version: {version[0]}")
            else:
                print("\nNo migration version found!")

    except Exception as e:
        print(f"Database verification failed: {e}")
        return

    # Test creating a sample user
    print("\nTesting User model...")
    session_factory = sessionmaker(bind=engine)

    try:
        with session_factory() as session:
            # Create a test user
            test_user = User(
                email="test@example.com",
                username="testuser",
                password_hash="hashed_password_here",
                first_name="Test",
                last_name="User"
            )

            session.add(test_user)
            session.commit()

            print(f"Created test user: {test_user}")

            # Query the user back
            queried_user = (
                session.query(User).filter_by(email="test@example.com").first()
            )
            if queried_user:
                print(f"Successfully queried user: {queried_user}")


    except Exception as e:
        print(f"User model test failed: {e}")
        return

    print("\nDatabase migration verification completed successfully!")


if __name__ == "__main__":
    verify_database_migration()
