from django.conf import settings
from django.db import models


# 25-12-29 슬기 수정: 성장 기록 모델 추가 (날짜별 키/몸무게)
class GrowthRecord(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='growth_records', verbose_name='사용자')
	record_date = models.DateField(verbose_name='기록 날짜')
	height_cm = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='키(cm)')
	weight_kg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='몸무게(kg)')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = '성장 기록'
		verbose_name_plural = '성장 기록'
		unique_together = ('user', 'record_date')
		ordering = ['record_date']

	def __str__(self):
		return f"{self.user} - {self.record_date}"


# 26-01-09: 달력 육아 기록 모델 추가
class CalendarRecord(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='calendar_records', verbose_name='사용자')
	record_date = models.DateField(verbose_name='기록 날짜')
	content = models.TextField(verbose_name='기록 내용')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = '달력 기록'
		verbose_name_plural = '달력 기록'
		unique_together = ('user', 'record_date')
		ordering = ['-record_date']

	def __str__(self):
		return f"{self.user} - {self.record_date}"
