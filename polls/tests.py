import datetime
from django.test import TestCase
from django.utils import timezone
from .models import Question
from django.urls import reverse

# Create your tests here.
# * Model Tests
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
            was_published_recently() returns False for questions
            whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
    
    def test_was_published_recently_with_old_question(self):
        """
            was_published_recently() returns False for questions
            whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question =  Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)
    
    def test_was_published_recently_with_recent_question(self):
        """
            was_published_recently() returns True for questions
            whose pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
        Create a question with the given `question_text` and published
        the given number of `days` offset to now (negative for  questions
        published in the past, positive for questions not yet published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


# * View Tests
class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
            If no questions exist, display the appropriate message.
        """
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])
    
    def test_past_question(self):
        """
            Question with pub_date in the past should be displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question]
        )

    def test_future_question(self):
        """
            Question with pub_date in the future should not be displayed.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls available.")
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            []
        )

    def test_future_and_past_question(self):
        """
            Even if both past and future questions exist, only past questions
            will be displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question]    
        )

    def test_multiple_past_questions(self):
        """
            Page may display multiple past questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [question2, question1]
        )

class QuestionDetailViewTests(TestCase):
    def test_future_questions(self):
        """
            View of a question that's published in a future date
            returns a 404 not found error.
        """
        future_question = create_question(question_text="Future question.", days=30)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_questions(self):
        """
            View of a question that's published in a past date
            returns the question's text.
        """
        past_question = create_question(question_text="Past question.", days=-30)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)