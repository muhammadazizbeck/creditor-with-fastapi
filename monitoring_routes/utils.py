from models import Debt, DebtType
from database import session, engine


session = session(bind=engine)

def calculate_monitoring_stats(user_id: int):
    owed_to_sum = session.query(Debt).filter(
        Debt.owner_id == user_id,
        Debt.debt_type == DebtType.owed_to
    ).with_entities(Debt.amount).all()

    owed_by_sum = session.query(Debt).filter(
        Debt.owner_id == user_id,
        Debt.debt_type == DebtType.owed_by
    ).with_entities(Debt.amount).all()

    total_owed_to = sum([d[0] for d in owed_to_sum]) if owed_to_sum else 0.0
    total_owed_by = sum([d[0] for d in owed_by_sum]) if owed_by_sum else 0.0

    return {
        "total_owed_to": total_owed_to,
        "total_owed_by": total_owed_by,
        "balance": total_owed_to - total_owed_by
    }

