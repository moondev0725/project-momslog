from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # is_active가 바뀌면 기존 토큰 자동 무효화
        return f"{user.pk}{user.is_active}{timestamp}"

email_verification_token = EmailVerificationTokenGenerator()
