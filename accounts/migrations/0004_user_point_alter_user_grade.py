from django.db import migrations, models


def map_old_grade(apps, schema_editor):
    User = apps.get_model("accounts", "User")

    mapping = {
        "seed": "start",
        "general": "join",
        "vip": "talk",
        "admin": "core",
    }

    for u in User.objects.all().only("id", "grade"):
        if u.grade in mapping:
            u.grade = mapping[u.grade]
            u.save(update_fields=["grade"])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_remove_user_child_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='point',
            field=models.PositiveIntegerField(default=0, verbose_name='포인트'),
        ),
        migrations.AlterField(
            model_name='user',
            name='grade',
            field=models.CharField(
                choices=[
                    ('start', '🌱 시작'),
                    ('join', '✍ 참여'),
                    ('talk', '💬 소통'),
                    ('empathy', '🤝 공감'),
                    ('core', '⭐ 핵심')
                ],
                default='start',
                max_length=10,
                verbose_name='회원 등급'
            ),
        ),

        # ✅ 여기! operations 안에 있어야 실행됨
        migrations.RunPython(map_old_grade, migrations.RunPython.noop),
    ]
