from django import forms
from .models import GrowthRecord


# 25-12-29 슬기 수정: 성장 기록 입력 폼
class GrowthRecordForm(forms.ModelForm):
	class Meta:
		model = GrowthRecord
		fields = ['record_date', 'height_cm', 'weight_kg']
		widgets = {
			'record_date': forms.DateInput(attrs={'type': 'date'}),
		}

	def clean(self):
		cleaned = super().clean()
		height = cleaned.get('height_cm')
		weight = cleaned.get('weight_kg')
		if height is not None and height <= 0:
			self.add_error('height_cm', '키는 0보다 커야 합니다.')
		if weight is not None and weight <= 0:
			self.add_error('weight_kg', '몸무게는 0보다 커야 합니다.')
		return cleaned
