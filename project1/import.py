import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, name, author, year in reader:
        db.execute("INSERT INTO books (isbn, name, author, year) VALUES(:isbn, :name, :author, :year)",
                    {"isbn":isbn, "name":name, "author":author, "year":year})
        print(f"Added book {isbn} with name:{name}")
        db.commit()

if __name__ == "__main__":
    main()            