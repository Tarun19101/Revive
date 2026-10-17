from django.db import migrations

NEW_SKILL_KEYS = ['battle_iq', 'body_aptitude', 'walking_library', 'artist', 'master_mind', 'magician']


def switch_to_new_skills(apps, schema_editor):
    PlayerSkill = apps.get_model('accounts', 'PlayerSkill')
    User = apps.get_model('auth', 'User')

    # Skills that are no longer in the game are removed. Skills that keep their key
    # (battle_iq, walking_library, master_mind) keep their level and XP.
    PlayerSkill.objects.exclude(skill_key__in=NEW_SKILL_KEYS).delete()

    # Every player gets any new skill they don't have yet, starting at level 0.
    for user_id in User.objects.values_list('id', flat=True):
        for key in NEW_SKILL_KEYS:
            PlayerSkill.objects.get_or_create(user_id=user_id, skill_key=key)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_playerachievement'),
    ]

    operations = [
        # Deleted skills cannot be brought back by reversing this: restore a backup instead.
        migrations.RunPython(switch_to_new_skills, migrations.RunPython.noop),
    ]