from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.review import Review
from app.models.order import Order, OrderItem
from app.models.user import User
from app.schemas.schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewOut, status_code=201)
def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Only allow review after delivered order
    order = db.query(Order).filter(
        Order.id == data.order_id,
        Order.user_id == current_user.id,
        Order.status == "delivered",
    ).first()
    if not order:
        raise HTTPException(400, "Can only review after order is delivered")

    # Check product was in order
    order_item = db.query(OrderItem).filter(
        OrderItem.order_id == data.order_id,
        OrderItem.product_id == data.product_id,
    ).first()
    if not order_item:
        raise HTTPException(400, "Product not in this order")

    # Check duplicate
    existing = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id == data.product_id,
        Review.order_id == data.order_id,
    ).first()
    if existing:
        raise HTTPException(400, "Already reviewed this product for this order")

    review = Review(user_id=current_user.id, **data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/product/{product_id}")
def get_product_reviews(product_id: str, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    total = len(reviews)
    avg = sum(r.rating for r in reviews) / total if total > 0 else 0
    return {
        "total": total,
        "average_rating": round(avg, 1),
        "reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "user_name": r.user.name if r.user else "User",
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ],
    }