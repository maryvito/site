from parsers import hh, superjob, config
from models import Resume, Keywords, db_session


# hh.py
def parse_resume_hh(db_session):
    hh.parse_resumes(db_session)

def parse_resume_superjob(db_session):
    superjob.parse_resumes(db_session)



if __name__ == "__main__":
    # parse_resume_hh(db_session)
    parse_resume_superjob(db_session)

# run_parser.py


# db_session = create_session()

# db_session.add(Keywords(...))