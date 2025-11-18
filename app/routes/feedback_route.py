from flask import Blueprint, request, redirect, url_for
from app.decorator.auth_decorator import login_required
from app.models import Manager, ErrorMessage
from app.sendmessages import send_to_telegram


feedback_bp = Blueprint("feedback_bp", __name__)

@feedback_bp.route("/feedback", methods = ["GET", "POST"])
@login_required
def feedback():
    mannager = Manager(ErrorMessage())

    if request.method == "POST":
        userfeedback = request.form.get('Feedback')
        message = userfeedback.strip()
        if message:
            mannager.add_feedbacks(message)
            send_to_telegram(message)
        return redirect(url_for('user_bp.home'))
    
