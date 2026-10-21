from django.core.exceptions import ValidationError
from django.db import models
from urllib import parse
# Create your models here.

class Video(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=400)
    notes = models.TextField(blank=True, null=True)
    video_id = models.CharField(max_length=40, unique=True)

    def save(self, *args, **kwargs):
        # extract the video id from youtube url

        # if not self.url.startswith('https://www.youtube.com/watch'):
        #     raise ValidationError(f'Not a YouTube URL: {self.url}')
        url_components = parse.urlparse(self.url)

        if url_components.scheme != 'https':
            raise ValidationError(f'Not a YouTube URL {self.url}')

        if url_components.netloc != 'www.youtube.com':
            raise ValidationError(f'Not a YouTube URL {self.url}')

        if url_components.path != '/watch':
            raise ValidationError(f'Not a YouTube URL {self.url}')


        query_string = url_components.query
        if not query_string:
            raise ValidationError(f'Invalid YouTube URL')

        try:
            parameters = parse.parse_qs(query_string, strict_parsing=True)
        except ValueError:  # e.g. watch?v1234 - a query field with no '='
            raise ValidationError(f'Invalid YouTube URL, can\'t parse query parameters')

        v_parameters_list = parameters.get('v')  # return if no key found
        if not v_parameters_list:  # checking if none or empty list
            raise ValidationError(f'Invalid YouTube URL, missing parameters')
        self.video_id = v_parameters_list[0]  # string

        super().save(*args, **kwargs)


    def __str__(self):
        notes = self.notes or ''  # notes can be None, and None[:200] would crash
        return f' ID: {self.pk}, Name: {self.name}, Video ID: {self.video_id}, URL: {self.url}, Notes: {notes[:200]}'