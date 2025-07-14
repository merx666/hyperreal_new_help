from django import forms
from .models import Comment, RatingCategory

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Wpisz swój komentarz...'}),
        }
        labels = {
            'content': 'Twój komentarz',
        }

class RatingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rating_categories = RatingCategory.objects.all()
        for category in rating_categories:
            self.fields[category.slug] = forms.ChoiceField(
                label=category.name,
                choices=[(i, str(i)) for i in range(1, 11)],
                widget=forms.Select(attrs={'class': 'form-select'}),
                help_text=category.description
            )
