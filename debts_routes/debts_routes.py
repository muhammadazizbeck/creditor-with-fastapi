from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_jwt_auth import AuthJWT
from database import session, engine
from models import Debt, User, DebtType
from schemas import DebtCreate, DebtResponse, DebtUpdate
from fastapi.encoders import jsonable_encoder

debts_router = APIRouter(
    prefix="/api/debts",
    tags=["Debts"]
)

session = session(bind=engine)

@debts_router.get("/", response_model=list[DebtResponse])
def list_debts(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        current_user = Authorize.get_jwt_subject()
        user = session.query(User).filter(User.username == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        debts = session.query(Debt).filter(Debt.owner_id == user.id).all()
        return debts
    except Exception:
        raise HTTPException(status_code=401, detail="Token is invalid or missing")


@debts_router.post("/", status_code=201, response_model=DebtResponse)
def create_debt(debt: DebtCreate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    new_debt = Debt(
        full_name=debt.full_name,
        amount=debt.amount,
        currency=debt.currency,
        description=debt.description,
        debt_type=debt.debt_type,
        return_date=debt.return_date,
        owner_id=user.id
    )
    session.add(new_debt)
    session.commit()
    session.refresh(new_debt)
    return new_debt


@debts_router.get("/{id}", response_model=DebtResponse)
def get_debt(id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    debt = session.query(Debt).filter(Debt.id == id, Debt.owner_id == user.id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt


@debts_router.put("/{id}", response_model=DebtResponse)
def update_debt(id: int, updated_data: DebtUpdate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    debt = session.query(Debt).filter(Debt.id == id, Debt.owner_id == user.id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    for field, value in updated_data.dict(exclude_unset=True).items():
        setattr(debt, field, value)

    session.commit()
    return debt


@debts_router.delete("/{id}", status_code=204)
def delete_debt(id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    debt = session.query(Debt).filter(Debt.id == id, Debt.owner_id == user.id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")

    session.delete(debt)
    session.commit()
    return {"message": "Debt deleted successfully"}


