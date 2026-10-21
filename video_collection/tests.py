from .models import Video
from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction


class TestHomePageMessage(TestCase):

    def test_app_title_message_shown_on_home_page(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, 'Fish Tank Videos')


class TestAddVideos(TestCase):

    # Adding a video, added to DB and video_id created

    def test_add_video(self):

        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'How to Setup A Natural Aquarium | Low Maintenance Quick and Easy',
            'url': 'https://www.youtube.com/watch?v=3V4I6jFUyW0',
            'notes': 'testing this'
        }

        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video, follow=True)

        # redirect to video list
        self.assertTemplateUsed(response, 'video_collection/video_list.html')

        # video list shows new video
        self.assertContains(response, 'How to Setup A Natural Aquarium | Low Maintenance Quick and Easy')
        self.assertContains(response, 'https://www.youtube.com/watch?v=3V4I6jFUyW0')
        self.assertContains(response, 'testing this')

        # video count on page is correct
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        # one new video in the database
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first()

        self.assertEqual('How to Setup A Natural Aquarium | Low Maintenance Quick and Easy', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=3V4I6jFUyW0', video.url)
        self.assertEqual('testing this', video.notes)
        self.assertEqual('3V4I6jFUyW0', video.video_id)

        # add another video - both present?

        valid_video_2 = {
            'name': 'aquarium plants for beginners',
            'url': 'https://www.youtube.com/watch?v=IFQmOZqvtWg',
            'notes': 'easy low light plants'
        }

        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video_2, follow=True)

        # redirect to video list
        self.assertTemplateUsed(response, 'video_collection/video_list.html')

        # video count on page is correct
        self.assertContains(response, '2 videos')

        # video list shows both new videos

        # video 1,
        self.assertContains(response, 'How to Setup A Natural Aquarium | Low Maintenance Quick and Easy')
        self.assertContains(response, 'https://www.youtube.com/watch?v=3V4I6jFUyW0')
        self.assertContains(response, 'testing this')

        # and video 2
        self.assertContains(response, 'aquarium plants for beginners')
        self.assertContains(response, 'https://www.youtube.com/watch?v=IFQmOZqvtWg')
        self.assertContains(response, 'easy low light plants')

        # database contains two videos
        self.assertEqual(2, Video.objects.count())

        # both video present on page? Another way to check is to query for a video with all the expected data.
        # the get method will raise a DoesNotExist error if a matching video is not found, and that will cause the test to fail

        video_1_in_db = Video.objects.get(name='How to Setup A Natural Aquarium | Low Maintenance Quick and Easy',
                                          url='https://www.youtube.com/watch?v=3V4I6jFUyW0',
                                          notes='testing this', video_id='3V4I6jFUyW0')

        video_2_in_db = Video.objects.get(name='aquarium plants for beginners',
                                          url='https://www.youtube.com/watch?v=IFQmOZqvtWg',
                                          notes='easy low light plants', video_id='IFQmOZqvtWg')

        # how about the correct videos in the context?
        # the object in the response is from a database query, so it's a QuerySet object. Convert to a list
        videos_in_context = list(response.context['videos'])

        # in this order, because they'll be sorted by name, case insensitive ('aquarium...' before 'How...')
        expected_videos_in_context = [video_2_in_db, video_1_in_db]
        self.assertEqual(expected_videos_in_context, videos_in_context)

    # Notes are optional

    def test_add_video_no_notes_video_added(self):

        add_video_url = reverse('add_video')

        valid_video = {
            'name': 'How to Setup A Natural Aquarium',
            'url': 'https://www.youtube.com/watch?v=3V4I6jFUyW0',
            # no notes
        }

        # follow=True necessary because the view redirects to the video list after a video is successfully added.
        response = self.client.post(add_video_url, data=valid_video, follow=True)

        # redirect to video list
        self.assertTemplateUsed(response, 'video_collection/video_list.html')

        # video list shows new video
        self.assertContains(response, 'How to Setup A Natural Aquarium')
        self.assertContains(response, 'https://www.youtube.com/watch?v=3V4I6jFUyW0')

        # video count on page is correct
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # and the non-plural form is used

        # one new video in the database
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

        # get that video - if there's 1 video it must be the one added
        video = Video.objects.first()

        self.assertEqual('How to Setup A Natural Aquarium', video.name)
        self.assertEqual('https://www.youtube.com/watch?v=3V4I6jFUyW0', video.url)
        self.assertEqual('', video.notes)
        self.assertEqual('3V4I6jFUyW0', video.video_id)

    # Invalid videos not added

    def test_add_video_missing_fields(self):

        add_video_url = reverse('add_video')

        invalid_videos = [
            {
                'name': '',  # no name, should not be allowed
                'url': 'https://www.youtube.com/watch?v=3V4I6jFUyW0',
                'notes': 'testing this'
            },
            {
                # no name field
                'url': 'https://www.youtube.com/watch?v=3V4I6jFUyW0',
                'notes': 'testing this'
            },
            {
                'name': 'example',
                'url': '',  # no URL, should not be allowed
                'notes': 'testing this'
            },
            {
                'name': 'example',
                # no URL
                'notes': 'testing this'
            },
            {
                # no name
                # no URL
                'notes': 'testing this'
            },
            {
                'name': '',  # blank - not allowed
                'url': '',  # no URL, should not be allowed
                'notes': 'testing this'
            },
        ]

        for invalid_video in invalid_videos:
            # follow=True not necessary because if video not valid, will expect a simple response
            response = self.client.post(add_video_url, data=invalid_video)

            self.assertTemplateUsed(response, 'video_collection/add.html')  # still on add page
            self.assertEqual(0, Video.objects.count())  # no video added to database
            messages = response.context['messages']  # get the messages
            message_texts = [message.message for message in messages]  # and the message texts
            self.assertIn('Check data entered', message_texts)  # is this message one of the messages?

            # And we can also check that message is displayed on the page
            self.assertContains(response, 'Check data entered')

    #  Duplicates not allowed

    def test_add_duplicate_video_not_added(self):

        # Since an integrity error is raised, the database has to be rolled back to the state before this
        # action (here, adding a duplicate video) was attempted. This is a separate transaction so the
        # database might be in a weird state and future queries in this method can fail with atomic transaction errors.
        # the solution is to ensure the entire transaction is in an atomic block so the attempted save and subsequent
        # rollback are completely finished before more DB transactions - like the count query - are attempted.

        # Most of this is handled automatically in a view function, but we have to deal with it here.

        with transaction.atomic():
            new_video = {
                'name': 'How to Setup A Natural Aquarium',
                'url': 'https://www.youtube.com/watch?v=3V4I6jFUyW0',
                'notes': 'testing this'
            }

            # Create a video with this data in the database
            # the ** syntax unpacks the dictionary and converts it into function arguments
            # https://python-reference.readthedocs.io/en/latest/docs/operators/dict_unpack.html
            # Video.objects.create(**new_video)
            # with the new_video dictionary above is equivalent to
            # Video.objects.create(name='How to Setup A Natural Aquarium', url='https://www.youtube.com/watch?v=3V4I6jFUyW0', notes='testing this')
            Video.objects.create(**new_video)

            video_count = Video.objects.count()
            self.assertEqual(1, video_count)

        with transaction.atomic():
            # try to create it again
            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form
            self.assertTemplateUsed(response, 'video_collection/add.html')

            messages = response.context['messages']
            message_texts = [message.message for message in messages]
            self.assertIn('Video already added', message_texts)

            self.assertContains(response, 'Video already added')  # and message displayed on page

        # still one video in the database
        video_count = Video.objects.count()
        self.assertEqual(1, video_count)

    def test_add_video_invalid_url_not_added(self):

        # what other invalid strings shouldn't be allowed?
        # (a blank URL is covered by test_add_video_missing_fields - the form rejects it before the model sees it)

        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.facebook.com/',
            'https://www.facebook.com/watch?v=3V4I6jFUyW0',
            'https://github.com',
            '12345678',
            'hhhhhhhhttps://www.youtube.com/watch',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=123456',
            '    sdfsdf sdfsdf   sfsdfsdf',
            '    https://minneapolis.edu?v=123456     ',
            '[',
            '☂️🌟🌷',
            '!@#$%^&*(',
            '//',
            'file://sdfsdf',
        ]

        for invalid_url in invalid_video_urls:
            new_video = {
                'name': 'How to Setup A Natural Aquarium',
                'url': invalid_url,
                'notes': 'testing this'
            }

            response = self.client.post(reverse('add_video'), data=new_video)

            # same template, the add form
            self.assertTemplateUsed(response, 'video_collection/add.html')

            # Messages set correctly?
            messages = response.context['messages']
            message_texts = [message.message for message in messages]
            self.assertIn('Check data entered', message_texts)
            self.assertIn('Invalid YouTube URL', message_texts)

            # and messages displayed on page
            self.assertContains(response, 'Check data entered')
            self.assertContains(response, 'Invalid YouTube URL')

            # no videos in the database
            video_count = Video.objects.count()
            self.assertEqual(0, video_count)


class TestVideoList(TestCase):

    # All videos shown on list page, sorted by name, case insensitive

    def test_all_videos_displayed_in_correct_order(self):
        v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=124')
        v3 = Video.objects.create(name='AAA', notes='example', url='https://www.youtube.com/watch?v=125')
        v4 = Video.objects.create(name='lmn', notes='example', url='https://www.youtube.com/watch?v=126')

        expected_video_order = [v3, v2, v4, v1]
        response = self.client.get(reverse('video_list'))
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    # No video message

    def test_no_video_message(self):
        response = self.client.get(reverse('video_list'))
        videos_in_template = response.context['videos']
        self.assertContains(response, 'No videos')
        self.assertEqual(0, len(videos_in_template))

    # 1 video vs 2 videos vs 4 videos message

    def test_video_number_message_single_video(self):
        v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '1 video')
        self.assertNotContains(response, '1 videos')  # check this, because '1 videos' contains '1 video'

    def test_video_number_message_two_videos(self):
        v1 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ZYX', notes='example', url='https://www.youtube.com/watch?v=124')
        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '2 videos')

    def test_video_number_message_multiple_videos(self):
        v1 = Video.objects.create(name='XYZ', notes='example', url='https://www.youtube.com/watch?v=123')
        v2 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v3 = Video.objects.create(name='uvw', notes='example', url='https://www.youtube.com/watch?v=789')
        v4 = Video.objects.create(name='def', notes='example', url='https://www.youtube.com/watch?v=101')

        response = self.client.get(reverse('video_list'))
        self.assertContains(response, '4 videos')


class TestVideoSearch(TestCase):

    # search only shows matching videos, partial case-insensitive matches

    def test_video_search_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = [v1, v3, v4]
        response = self.client.get(reverse('video_list') + '?search_term=abc')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)

    def test_video_search_no_matches(self):
        v1 = Video.objects.create(name='ABC', notes='example', url='https://www.youtube.com/watch?v=456')
        v2 = Video.objects.create(name='nope', notes='example', url='https://www.youtube.com/watch?v=789')
        v3 = Video.objects.create(name='abc', notes='example', url='https://www.youtube.com/watch?v=123')
        v4 = Video.objects.create(name='hello aBc!!!', notes='example', url='https://www.youtube.com/watch?v=101')

        expected_video_order = []  # empty list
        response = self.client.get(reverse('video_list') + '?search_term=kittens')
        videos_in_template = list(response.context['videos'])
        self.assertEqual(expected_video_order, videos_in_template)
        self.assertContains(response, 'No videos')


class TestVideoModel(TestCase):

    def test_create_id(self):
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        self.assertEqual('IODxDxX7oi4', video.video_id)

    def test_create_id_valid_url_with_time_parameter(self):
        # a video that is playing and paused may have a timestamp in the query
        video = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4&ts=14')
        self.assertEqual('IODxDxX7oi4', video.video_id)

    def test_create_video_notes_optional(self):
        v1 = Video.objects.create(name='example', url='https://www.youtube.com/watch?v=67890')
        v2 = Video.objects.create(name='different example', notes='example',
                                  url='https://www.youtube.com/watch?v=12345')
        expected_videos = [v1, v2]
        database_videos = Video.objects.all()
        # check contents of two lists/iterables but order doesn't matter.
        self.assertCountEqual(expected_videos, database_videos)

    def test_invalid_urls_raise_validation_error(self):
        invalid_video_urls = [
            'https://www.youtube.com/watch',
            'https://www.youtube.com/watch/somethingelse',
            'https://www.youtube.com/watch/somethingelse?v=1234567',
            'https://www.youtube.com/watch?',
            'https://www.youtube.com/watch?abc=123',
            'https://www.youtube.com/watch?v=',
            'https://www.youtube.com/watch?v1234',
            'https://www.facebook.com/',
            'https://www.facebook.com/watch?v=3V4I6jFUyW0',
            'https://github.com',
            '12345678',
            '1342678',
            'bsfdjgh',
            '21345ghjk',
            'hhhhhhhhttps://www.youtube.com/watch',
            'hhhhhhhhhhhttps://www.youtube.com/watch?v=',
            'http://www.youtube.com/watch/somethingelse?v=1234567',
            'https://minneapolis.edu',
            'https://minneapolis.edu?v=123456',
            '',
        ]

        for invalid_url in invalid_video_urls:
            with self.assertRaises(ValidationError):
                Video.objects.create(name='example', url=invalid_url, notes='example notes')

        video_count = Video.objects.count()
        self.assertEqual(0, video_count)

    def test_duplicate_video_raises_integrity_error(self):
        Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')
        with self.assertRaises(IntegrityError):
            Video.objects.create(name='example', url='https://www.youtube.com/watch?v=IODxDxX7oi4')