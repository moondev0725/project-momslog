from django.db import models
from django.conf import settings

class DailyQuest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()  # 오늘 날짜
    content = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    streak = models.PositiveIntegerField(default=0)  # 🔥 추가

    class Meta:
        unique_together = ("user", "date")  # 유저당 하루 1개

    def __str__(self):
        return f"{self.user_id} / {self.date} / {'done' if self.completed else 'todo'}"
