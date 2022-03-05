class CommodoreOrderCommand:
    def __init__(self, isTimeToOrder: bool, decisionPayload: dict, oldDecisionPayloadString=""):
        self.isTimeToOrder = isTimeToOrder
        self.decisionPayload = decisionPayload
        self.oldDecisionPayloadString = oldDecisionPayloadString