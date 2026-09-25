"""The category list the classifiers choose from, and which team owns each one.

Ownership follows support-policy.pdf §6. The five "owner groups" are what routing
is judged on: Chat, Email and Voice Frontline are one group because a ticket's
frontline team is decided by its channel, not by what the customer wrote.
"""

FRONTLINE = "Frontline"
BILLING = "Billing"
LOGISTICS = "Logistics"
RETURNS = "Returns Desk"
WARRANTY = "Escalations & Warranty"

OWNER_GROUPS = [FRONTLINE, BILLING, LOGISTICS, RETURNS, WARRANTY]

# category -> (owner group, one-line definition used in the LLM prompt)
CATEGORIES = {
    "Billing & Payments": (
        BILLING,
        "Money problems with no delivery problem: payment debited but no order created, "
        "charged twice, failed payment, invoice/GST bill, EMI, coupon or price difference.",
    ),
    "Delivery & Shipping": (
        LOGISTICS,
        "An order was placed but the parcel has not arrived, is late, tracking is stuck, "
        "it was marked delivered but not received, or it arrived to the wrong address. "
        "This applies even if the customer also says they paid.",
    ),
    "Returns & Refunds": (
        RETURNS,
        "Customer wants to return, cancel or exchange an order, or asks about a refund "
        "for something already returned or cancelled.",
    ),
    "Warranty & Repair": (
        WARRANTY,
        "Hardware is physically broken or dead (not a settings issue): dead on arrival, "
        "stopped working, water damage, needs repair or warranty replacement.",
    ),
    "Connectivity": (FRONTLINE, "Bluetooth pairing, disconnects, Wi-Fi, multi-device issues."),
    "Charging & Battery": (FRONTLINE, "Won't charge, battery drains fast, charging case issues."),
    "Audio Quality": (FRONTLINE, "Sound, microphone, noise cancellation, one side low or crackling."),
    "App & Firmware": (FRONTLINE, "Companion app, firmware update, app crashes or shows errors."),
    "Account & Login": (FRONTLINE, "Login, OTP, password, account or profile problems."),
    "Product Enquiry": (FRONTLINE, "Pre-sales or how-to questions: compatibility, features, stock."),
    "Other": (FRONTLINE, "Anything that genuinely fits none of the above."),
}

CATEGORY_NAMES = list(CATEGORIES)

# The helpdesk team names in agents.csv / tickets.csv, mapped to owner groups.
TEAM_TO_GROUP = {
    "Chat Frontline": FRONTLINE,
    "Email Frontline": FRONTLINE,
    "Voice Frontline": FRONTLINE,
    "Billing": BILLING,
    "Logistics": LOGISTICS,
    "Returns Desk": RETURNS,
    "Escalations & Warranty": WARRANTY,
}


def owner_group(category: str) -> str:
    """Owner group for a category name; unknown names fall back to Frontline."""
    return CATEGORIES.get(category, (FRONTLINE, ""))[0]
