# -*- coding: utf-8 -*-
import binascii
import hashlib
import os
from decimal import Decimal

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import logging
logger = logging.getLogger(__name__)

INVITE_HASH_LEN = 10

################################################################################
# Time-stamp our models

class TimeStampModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

################################################################################
# A model base class that lets you mark objects as "deleted" without actually
# removing them from the database.

class SoftDeleteQuerySet(models.query.QuerySet):
    def mark_deleted(self):
        self.update(deleted_at=timezone.now())

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

class SoftDeleteModel(TimeStampModel):
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    active_objects = SoftDeleteManager()

    def mark_deleted(self, *_args):
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True

################################################################################
# Per-object permissions.

class ObjectUserPermission(models.Model):
    user=models.ForeignKey('User')
    permission=models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return '%s:%s' % (self.user, self.permission)

    
################################################################################
# Custom user model.

class UserConnectedMixin:
    '''
    Simple mixin for models whose permissions are based on an associated user
    object. Meaning, for example, if you have permission to see that user, you
    have permission to see this connected object, like the user's test scores or
    something.
    '''
    def user_has_perm_in(self, user, perms):
        return self.user.user_has_perm_in(user, perms)

class UserManager(BaseUserManager):
    def _create_user(self, email, name, password, division=None, is_manager=False, roles=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, division=division, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        if division and is_manager:
            perm,_created = ObjectUserPermission.objects.get_or_create(user=user, permission='change')
            division.permissions.add(perm)
            perm,_created = ObjectUserPermission.objects.get_or_create(user=user, permission='delete')
            division.permissions.add(perm)
        if roles:
            role_objects = Role.active_objects.filter(name__in=roles)
            user.roles.add(*role_objects)
        return user

    def create_user(self, email, name, division, password=None, **extra_fields):
        '''
        Create a new User object. Division is required for non-superusers.
        '''
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, name, password, division=division, **extra_fields)

    def create_superuser(self, email, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, name, password, **extra_fields)

    # def get_from_invite_code(self, code):
    #     try:
    #         invite = UserInvite.objects.get_from_invite_code(code)
    #         return (invite.user, invite)
    #     except UserInvite.DoesNotExist:
    #         raise User.DoesNotExist()


class User(AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
    name = models.CharField(blank=False, max_length=255)
    email = models.EmailField(unique=True, blank=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    division = models.ForeignKey('Division',
                                 blank=True,
                                 null=True,
                                 related_name='employees',
                                 help_text=_('Company division where this user works. Can be blank for site admins'))
                                    
    roles = models.ManyToManyField('Role', related_name='users')
    permissions = models.ManyToManyField(ObjectUserPermission, related_name='user_set')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    class Meta:
        permissions = (
            ("view", "Can see the user"),
            ("change", "Can change the user or its things"),
        )

    def user_has_perm_in(self, user, perms):
        # Users can view themselves.
        if 'view' in perms and self == user:
            return True
        divisions = self.division.get_ancestors(True)
        return ObjectUserPermission.objects.filter(Q(division_set__in=divisions, user=user, permission__in=perms) |
                                                   Q(user_set=self, user=user, permission__in=perms)).exists()

    # Implement the 'is_active' property using the SoftDeleteModel's `deleted_at` field.
    @property
    def is_active(self):
        return (self.deleted_at is None)

    def set_is_active(self, val):
        if val:
            self.deleted_at = timezone.now()
        else:
            self.deleted_at = None

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_hash_for_invite(self):
        # Not going for a ton of security here. They just need to be able to
        # verify that they got an invite. They still have to log in via Facebook.
        return hashlib.sha1(self.email.encode('utf-8') + self.division.name.encode('utf-8') + b'Shaker of salt').hexdigest()[:INVITE_HASH_LEN]

    def get_ancestors(self):
        '''
        Used by the PerObjectPermissionsMixin. Get's `self`'s division and all
        parent divisions.
        '''
        return self.division.get_ancestors(True)

    @property
    def company(self):
        if self.division:
            return self.division.get_company()
        else:
            return None

    @property
    def company_id(self):
        company = self.company
        if company:
            return company.id
        return None

    def get_rest_token(self):
        from rest_framework.authtoken.models import Token
        # Parse looks for 'r:' in the session string to decide if it's
        # revokable or not. We want it to decide yes, so prepend
        # 'r:' to the session token.
        token,_created = Token.objects.get_or_create(user=self,
                                                     defaults={'key': 'r:' + binascii.hexlify(os.urandom(19)).decode()})
        return token
        

    def __str__(self):
        return self.name

################################################################################
# Roles.

class Role(SoftDeleteModel):
    '''
    Represents a user's role in the organization. Like CEO or "Line Chef". A
    User can have multiple roles.
    '''
    company=models.ForeignKey('Company', related_name='roles', on_delete=models.CASCADE)
    name=models.CharField(max_length=255, null=False, blank=False)

################################################################################

class UserInviteManager(models.Manager):
    def get_from_invite_code(self, code):
        if not code:
            raise UserInvite.DoesNotExist()
        try:
            invite_id = int(code[INVITE_HASH_LEN:])
        except ValueError:
            logger.error('UserInviteManager.get_from_invite_code. No valid id')
            raise UserInvite.DoesNotExist()
        user_invite = UserInvite.objects.get(id=invite_id)
        if user_invite.user.get_hash_for_invite() != code[:INVITE_HASH_LEN]:
            raise UserInvite.DoesNotExist()
        return user_invite


class UserInvite(TimeStampModel):
    '''
    Represents an invite to a new user to join. The user gets an email with the
    invite code, then they need to log in via Facebook.
    '''
    user = models.OneToOneField(User,
                                related_name='invite')
    created_by = models.ForeignKey(User,
                                   related_name='created_invites')


    objects = UserInviteManager()

    @property
    def invite_code(self):
        # Get the invite_code from the id, but make it look more interesting than just an integer, and less guessable.
        # Five 
        return '%s%s' % (self.user.get_hash_for_invite(), self.id)

################################################################################
# Company org

class Division(SoftDeleteModel):
    '''
    A way to group together multiple units of the company, for example, by city
    or region, all the way down to an individual location. Divisions can be
    hierarchical. There must be at least one Division per company. Many
    different company organization schemes can be represented using this simple
    hierarchical model.

    Here is some info on Multiunit Enterprises: https://hbr.org/2008/06/the-multiunit-enterprise
    '''
    name = models.CharField(blank=False, max_length=255, default='Global')
    description = models.TextField(blank=True, null=False, default='')
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    permissions = models.ManyToManyField(ObjectUserPermission,
                                         related_name='division_set',
                                         help_text='Tells which users have access to which divisions.')

    def user_has_perm_in(self, user, perms):
        ancestors = self.get_ancestors(True)
        return ObjectUserPermission.objects.filter(division_set__in=ancestors, user=user, permission__in=perms).exists()

    def get_ancestors(self, with_self=False):
        '''
        Used by the PerObjectPermissionsMixin. Get's the parent division and all
        ancestor divisions.
        '''
        # It's unfortunate that we have to do this as a raw query, but Django
        # does not support recursive queries.
        query = '''
        WITH RECURSIVE cte AS
          (SELECT lp_division.*
            FROM lp_division
            WHERE lp_division.id=%s
            UNION ALL
              SELECT lp_division.*
                FROM lp_division
                INNER JOIN cte ON lp_division.id=cte.parent_id)
          SELECT * FROM cte;
        '''        
        start_division = self if with_self else self.parent
        return Division.objects.raw(query, [start_division.id])

    def get_company(self):
        '''
        Traverse the hierarchy to find the company that this division belongs to.
        '''
        # It's unfortunate that we have to do this as a raw query, but Django
        # does not support recursive queries.
        query = '''
        SELECT * FROM lp_company WHERE top_division_id IN
          (WITH RECURSIVE cte AS
            (SELECT lp_division.*
              FROM lp_division
              WHERE lp_division.id=%s
              UNION ALL
                SELECT lp_division.*
                  FROM lp_division
                  INNER JOIN cte ON lp_division.id=cte.parent_id)
            SELECT id FROM cte);
        '''        
        return Company.objects.raw(query, [self.id])[0]
        

    def __str__(self):
        return self.name

class Company(SoftDeleteModel):
    '''
    A company, like Applebee's. Can have multiple locations. Must have one top division.
    '''
    name = models.CharField(blank=False, unique=True, max_length=255)
    slug = models.SlugField(unique=True, blank=False)
    top_division = models.OneToOneField(Division, blank=False, on_delete=models.CASCADE, related_name='company')

    def __str__(self):
        return self.name

    def user_has_perm_in(self, user, perms):
        if 'view' in perms:
            # Only if the user belongs to this company.
            divisions = user.division.get_ancestors(True)
            return divisions.filter(company=self).exists()
        return False

################################################################################
# Performance metrics come from the Polish backend. It is the scores created by
# the Phaceology face recognition technology.

class PerformanceMetric(SoftDeleteModel):
    company=models.ForeignKey(Company)
    name = models.CharField(blank=False, unique=True, max_length=255)
    
    def user_has_perm_in(self, user, perms):
        return self.company.user_has_perm_in(user, perms)

class PerformanceScore(SoftDeleteModel, UserConnectedMixin):
    user = models.ForeignKey(User,
                             blank=False,
                             related_name='performance_scores')
    
    metric = models.ForeignKey(PerformanceMetric)

    created_by = models.ForeignKey(User,
                                   blank=True,
                                   null=True,
                                   help_text=_('The manager who entered this score, if applicable.'),
                                   related_name='entered_performance_scores')
    
    score = models.DecimalField(blank=False,
                                max_digits=6,
                                decimal_places=3)


################################################################################
# Lessons are what employees come to this site for. Pretty simple for now: A
# template file, stored in version control, created by a dev. It's just a HTML
# file. In the future, we may allow dynamic editing of lessons.
#
# After reading a lesson, the employee can take a quiz. The quiz is also very
# simple for now: A list of single-answer multiple-choice questions, each of
# which is a plain text question and plain text answers.
#
# Lessons are grouped into modules.

class LessonManager(models.Manager):
    def create_lesson(self,
                      name,
                      template,
                      module,
                      questions_and_answers):
        '''
        Create a lesson with a bunch of questions and answers.

        @param questions_and_answers A list of dicts, each with a 'question' and
        'answer' entry. The question entry is a string question for creating a
        QuizQuestion. The answer entry is an array of strings, with the correct
        answer first.
        '''
        lesson = self.create(name=name, template=template, module=module)
        questions = []
        answers = []
        # First create the questions, then bulk-create the answers. The
        # questions can't be bulk-created, because that doesn't populate the
        # auto-id field, which we need.
        questions = [QuizQuestion.objects.create(lesson=lesson, order=i, text=qdef['question'])
                     for i,qdef in enumerate(questions_and_answers)]
        for qdef,question in zip(questions_and_answers, questions):
            is_correct = True
            for adef in qdef['answers']:
                answer = QuizAnswer(question=question, text=adef, is_correct=is_correct)
                is_correct = False
                answers.append(answer)
        QuizAnswer.objects.bulk_create(answers)
        return lesson

class Lesson(SoftDeleteModel):
    name = models.CharField(blank=False, max_length=255)
    template = models.CharField(blank=False, max_length=255)
    # ES: TODO: Actually reference this passing score value when checking whether a user passed the test.
    passing_score = models.DecimalField(blank=False,
                                        max_digits=6,
                                        decimal_places=3,
                                        default=Decimal(100))
    module = models.ForeignKey('LessonModule', blank=False, related_name='lessons')

    objects = LessonManager()

    class Meta:
        unique_together = (('name', 'module'),)

    def user_has_perm_in(self, user, perms):
        return self.company.user_has_perm_in(user, perms)

class LessonModule(SoftDeleteModel):
    '''
    A group of lessons.
    '''
    category = models.ForeignKey('LessonModuleCategory', related_name='modules')
    name = models.CharField(blank=False, max_length=255)

    class Meta:
        unique_together = (('name', 'category'),)

    def user_has_perm_in(self, user, perms):
        return self.category.company.user_has_perm_in(user, perms)


    def user_percent_passed(self, user):
        '''
        Returns a Decimal telling what percentage of the tests in this module `user`
        has passed.
        '''
        nlessons = self.lessons.filter(deleted__isnull=True).count()
        from django.db.models import F
        npassed = QuizAttempt.active_objects.filter(user=user, lesson_in=self.lessons, score__gte=F(lesson__passing_score)).count()
        return Decimal(100) * Decimal(nlessons) / Decimal(npassed)

class LessonModuleCategory(SoftDeleteModel):
    '''
    A group of Lesson Modules. Like "Front of House" or "Back of House"
    '''
    company = models.ForeignKey('Company', related_name='lesson_module_categories')
    name = models.CharField(blank=False, max_length=255)

    class Meta:
        unique_together = (('name', 'company'),)

    def user_has_perm_in(self, user, perms):
        return self.company.user_has_perm_in(user, perms)

# class LessonRequest(SoftDeleteModel, UserConnectedMixin):
#
#        '''
#     Created by a manager to tell the user that he/she must take the specified
#     lesson.
#     '''
#     created_by = models.ForeignKey(User,
#                                    related_name='created_lesson_requests')
#     user = models.ForeignKey(User,
#                              blank=False,
#                              related_name='lesson_requests')
#     lesson = models.ForeignKey(Lesson)

#     # ES: TODO: Add a signal to automatically email the user when one of these
#     # is created.

#     def __str__(self):
#         return '%s requested %s take %s on %s' % (
#             self.created_by, self.user, self.lesson, self.created_at)

class QuizQuestion(SoftDeleteModel):
    lesson = models.ForeignKey(Lesson, related_name='questions')
    text = models.TextField()
    order = models.SmallIntegerField()

    class Meta:
        ordering = ('order',)
        unique_together = (('lesson', 'order'),)

    def user_has_perm_in(self, user, perms):
        return self.lesson.company.user_has_perm_in(user, perms)

class QuizAnswer(SoftDeleteModel):
    question = models.ForeignKey(QuizQuestion, related_name='answers')
    text = models.TextField()
    is_correct = models.BooleanField(help_text=_('One correct answer per question.'))

    class Meta:
        unique_together = (('question', 'text'),)
        ordering = ['?']

    def user_has_perm_in(self, user, perms):
        return self.question.lesson.module.category.company.user_has_perm_in(user, perms)

class QuizAttempt(SoftDeleteModel, UserConnectedMixin):
    '''
    Represents an attempt by a user to take a quiz after reading a lesson.
    '''
    user = models.ForeignKey(User,
                             blank=False)
    lesson = models.ForeignKey(Lesson)
    score = models.DecimalField(blank=False,
                                max_digits=6,
                                decimal_places=3,
                                default=Decimal(-1))
    created_by = models.ForeignKey(User,
                                   blank=True,
                                   null=True,
                                   help_text=_('The manager who entered this score, if applicable.'),
                                   related_name='entered_quiz_scores')

    def update_score(self, save=False):
        ncorrect = self.answers.filter(answer__is_correct=True).count()
        ntotal = self.answers.count()
        old_score = self.score
        self.score = Decimal(ncorrect * 100) / Decimal(ntotal) # In percentage
        if save and self.score != old_score:
            self.save()

    @property
    def passed(self):
        # ES: TODO: What is a passing percentage?
        return (self.score > Decimal(50))
    
    def __str__(self):
        ret =  'User %s, Lesson %s, Score %s' % (self.user, self.lesson, self.score)
        if self.deleted_at:
            ret += ' Deleted at %s' % self.deleted_at
        return ret

class QuizAnswerAttempt(SoftDeleteModel, UserConnectedMixin):
    '''
    Represents one attempted by a user to one question while taking a quiz.
    '''
    quiz_attempt = models.ForeignKey(QuizAttempt, related_name='answers')
    answer = models.ForeignKey(QuizAnswer)

    # Django doesn't support this uniqueness constraint. We could enforce it
    # manually but that would add an extra DB query. Just make sure in the UI there's only
    # one right answer. For now, only site admins are adding questions anyway.
    #
    # class Meta:
    #     unique_together = (('quiz_attempt', 'answer__question'),)
        
    @property
    def user(self):
        return self.quiz_attempt.user

class FacebookProfile(TimeStampModel, UserConnectedMixin):
    facebook_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(User, related_name='facebook_profile', primary_key=True)

    name = models.CharField(max_length=255, blank=True)
    access_token = models.CharField(max_length=255, blank=True)
    access_token_expires = models.DateTimeField(blank=True, null=True)

    def access_token_valid(self):
        '''
        Returns True if the facebook access token is valid.
        '''
        return self.access_token and self.access_token_expires and self.access_token_expires > timezone.now()

    def get_graph_api(self):
        '''
        Returns a facebook.GraphAPI object initialized with this user's access
        token.
        '''
        import facebook
        assert self.access_token_valid()
        return facebook.GraphAPI(self.access_token)
