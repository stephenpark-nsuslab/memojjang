from django.contrib import admin
from .models import Memo

# Memo 모델을 Admin에 등록
@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title', 'content')
