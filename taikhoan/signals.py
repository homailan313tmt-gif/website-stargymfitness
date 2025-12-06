
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Profile

@receiver(pre_save, sender=Profile)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Profile.objects.get(pk=instance.pk)
        if old.anh_dai_dien and old.anh_dai_dien != instance.anh_dai_dien:
            old.anh_dai_dien.delete(save=False)
    except Profile.DoesNotExist:
        pass

@receiver(post_delete, sender=Profile)
def delete_avatar_on_delete(sender, instance, **kwargs):
    """Xóa ảnh khi xóa Profile"""
    if instance.anh_dai_dien:
        instance.anh_dai_dien.delete(save=False)