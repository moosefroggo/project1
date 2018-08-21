# Set up database
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os, csv
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    f.readline()
    for isbn, title, author, year in reader:
        year_int = int(year)
        db.execute("INSERT into BOOKS (isbn, title, author, year) VALUES(:isbn,:title,:author,:year)",
        {"isbn": isbn, "title": title, "author": author, "year": year_int})
        print(f"Added {title} to database")
    db.commit()

if __name__ == "__main__":
    main()