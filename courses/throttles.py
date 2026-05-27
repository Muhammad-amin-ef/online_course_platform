from rest_framework.throttling import UserRateThrottle


class ReviewRateThrottle(UserRateThrottle):
    scope = 'review'