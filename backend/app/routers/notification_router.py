from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.notification_service import notification_service
from app.models import UserDevice
from app.models import UserProfile
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class RegisterDeviceRequest(BaseModel):
    user_id: str
    push_token: str
    platform: Optional[str] = "unknown"
    device_name: Optional[str] = "unknown"

class SendNotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None

@router.post("/register")
async def register_device(
    request: RegisterDeviceRequest,
    db: Session = Depends(get_db)
):
    """
    Register a device push token for a user.
    """
    # Check if token exists
    existing_device = db.query(UserDevice).filter(
        UserDevice.push_token == request.push_token
    ).first()
    
    if existing_device:
        # Update existing
        existing_device.user_id = request.user_id
        existing_device.last_used_at = datetime.now()
        existing_device.is_active = True
        logger.info(f"Updated device token for user {request.user_id}")
    else:
        # Create new
        new_device = UserDevice(
            user_id=request.user_id,
            push_token=request.push_token,
            platform=request.platform,
            device_name=request.device_name
        )
        db.add(new_device)
        logger.info(f"Registered new device token for user {request.user_id}")
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error registering device: {e}")
        raise HTTPException(status_code=500, detail="Failed to register device")
        
    return {"status": "success", "message": "Device registered"}

@router.post("/send")
async def send_notification(
    request: SendNotificationRequest,
    db: Session = Depends(get_db)
):
    """
    Send a notification to a specific user (Admin/System use).
    """
    # Get user devices
    devices = db.query(UserDevice).filter(
        UserDevice.user_id == request.user_id,
        UserDevice.is_active == True
    ).all()
    
    if not devices:
        return {"status": "skipped", "reason": "User has no active devices"}
    
    tokens = [d.push_token for d in devices]
    
    result = await notification_service.send_push_notification(
        tokens=tokens,
        title=request.title,
        body=request.body,
        data=request.data
    )
    
    return result
