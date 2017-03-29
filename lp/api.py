# -*- coding: utf-8 -*-

import rest_framework
from rest_framework import (authentication, permissions, routers, serializers,
                            viewsets)
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import Http404

from lp.models import *

import types
import logging
logger = logging.getLogger(__name__)


class ParseParser(rest_framework.parsers.JSONParser):
    media_type = 'text/plain'


class SocialLogin(APIView):
    # No authentication, access to all (since this is a login view anyway).
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        from django.contrib.auth import login, logout, authenticate

        logout(request)
        try:
            fb_auth_data = request.data['authData']['facebook']
        except KeyError:
            raise AuthenticationFailed('No Facebook authData')

        logger.debug('fb_auth_data %r', fb_auth_data)
        try:
            access_token = fb_auth_data['access_token']
            fbid = fb_auth_data['id']
            expiration_date = fb_auth_data['expiration_date']
        except KeyError as ex:
            raise AuthenticationFailed('Missing %s in Facebook authData' % ex.args[0])  # From REST framework

        # New signups need an invite code in order to create a new account
        invite_code = fb_auth_data.get('invite_code')

        if invite_code == 'demo':
            try:
                mgr = User.objects.get(email='mgr.east@costavida.com')
            except User.DoesNotExist:
                pass
            else:
                try:
                    invite,_created = UserInvite.objects.get_or_create(user=mgr, defaults={'created_by': mgr})
                    invite_code = invite.invite_code
                except:
                    pass
        elif invite_code == 'demoemp':
            try:
                emp = User.objects.get(email='emp.north.east.1.1@costavida.com')
            except User.DoesNotExist:
                pass
            else:
                try:
                    invite,_created = UserInvite.objects.get_or_create(user=emp, defaults={'created_by': emp})
                    invite_code = invite.invite_code
                except:
                    pass
        
                

        user = authenticate(fbid=fbid,
                            access_token=access_token,
                            expiration_date=expiration_date,
                            invite_code=invite_code)
        if not user:
            raise AuthenticationFailed('Invalid Facebook credentials')  # From REST framework
        login(request, user)

        token = user.get_rest_token()
        serializer = UserSerializer(user, context={'request': request})
        data = serializer.data
        data['sessionToken'] = token.key
        data['authData'] = request.data['authData']
        return Response(data)


# class FacebookLogin(APIView):
#     """
#     Facebook login action. Call this after logging into Facebook using the
#     JavaScript SDK. Then POST the signed_request to this view.

#     If this is a new account, include the invite_code as well.

#     On success, the user will be logged in and the session cookie will be
#     set. Return value includes the id of the user.
#     """
#     # No authentication, access to all (since this is a login view anyway).
#     authentication_classes = (authentication.SessionAuthentication,)
#     permission_classes = (permissions.AllowAny,)

#     def post(self, request, format=None):
#         from django.contrib.auth import login, logout, authenticate

#         logout(request)
#         try:
#             signed_request = request.data['signed_request']
#         except KeyError:
#             raise AuthenticationFailed('No signed_request') # From REST framework

#         invite_code = request.data.get('invite_code')

#         user = authenticate(signed_request=signed_request, invite_code=invite_code)
#         if not user:
#             raise AuthenticationFailed('Invalid signed_request') # From REST framework
#         login(request, user)
#         return Response({'id':user.id})

class Logout(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        from django.contrib.auth import logout
        logout(request)
        return Response({'success': True})


class EmailLogin(APIView):
    """
    Email/password login action.

    On success, the user will be logged in and the session cookie will be
    set. Return value includes the id of the user.
    """
    # No authentication, access to all (since this is a login view anyway).
    authentication_classes = [rest_framework.authentication.TokenAuthentication]
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        from django.contrib.auth import login, logout, authenticate

        logout(request)
        logger.info('EmailLogin.get: data %r', request.query_params)
        try:
            email = request.query_params['email']
        except KeyError:
            try:
                email = request.query_params['username']
            except KeyError:
                raise AuthenticationFailed('Email required')
        try:
            password = request.query_params['password']
        except KeyError:
            raise AuthenticationFailed('Password required')  # From REST framework

        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid login')  # From REST framework
        login(request, user)

        token = user.get_rest_token()
        serializer = UserSerializer(user, context={'request': request})
        data = serializer.data
        data['sessionToken'] = token.key
        return Response(data)


class CloudCode(APIView):
    '''
    Handles the "Cloud Code" functionality, just like Parse.

    Each method, other than post, is a Cloud Code function.

    I have named them in camelCase for consistency with the JavaScript API.
    '''
    def post(self, request, function, format=None):
        fn = getattr(self, function, None)
        if type(fn) is types.MethodType:
            return Response({'result':fn(request)})
        raise Http404('No such cloud function')

    def submitAnswer(self, request):
        '''
        Checks if the answer the user gave is correct.

        @param answerId The ID of the answer to check.
        @param quizAttemptId The ID of the quiz attempt. If -1, creates a new quiz attempt

        @return {isCorrect:<bool>, quizAttemptId:<int>}
        '''
        # ES: FIXME: Check the permission. Like do they have access to this lesson.
        quiz_attempt_id = request.data['quizAttemptId']
        answer_id = request.data['answerId']
        answer = QuizAnswer.objects.get(id=answer_id)
        if quiz_attempt_id == -1:
            quiz_attempt = QuizAttempt.objects.create(user=request.user, lesson=answer.question.lesson)
        else:
            quiz_attempt = QuizAttempt.objects.get(user=request.user,
                                                   lesson=answer.question.lesson,
                                                   id=quiz_attempt_id)
        answer_attempt = QuizAnswerAttempt.objects.create(quiz_attempt=quiz_attempt, answer=answer)
        quiz_attempt.update_score(save=True)
        return {'isCorrect':answer.is_correct, 'quizAttemptId':quiz_attempt.id}

    def didIPass(self, request):
        '''
        Checks if the user passed the specified test.

        @param lessonId The ID of the lesson to check.
        '''
        lesson_id = request.data['lessonId']
        attempts = QuizAttempt.objects.filter(lesson_id=lesson_id, user=request.user)
        for attempt in attempts:
            attempt.update_score(save=True)
            if attempt.passed:
                return True
        return False


    def manualResult(self, request):
        '''
        Called by a manager to mark an employee as having passed or failed a test.

        @param userId
        @param lessonId
        @param score
        '''
        qa = QuizAttempt.objects.create(user_id=request.data['userId'],
                                        lesson_id=request.data['lessonId'],
                                        score=request.data['score'],
                                        created_by=request.user)
        return {'quizAttemptId':qa.id}


################################################################################
# Object API.

router = routers.DefaultRouter()


class MyRelatedField(rest_framework.relations.HyperlinkedRelatedField):
    '''Provides Parse-like related-fields'''

    def __init__(self, view_name=None, **kwargs):
        self.init_kwargs = kwargs
        self.model_name = kwargs.pop('model_name', None)
        super().__init__(view_name, **kwargs)

    def get_actual_field_name(self):
        '''
        For some reason, ManyToManyField objects don't store the field_name in
        field_name, but it's in parent.field_name.
        '''
        return self.field_name or self.parent.field_name
    
    def use_pk_only_optimization(self):
        result = super().use_pk_only_optimization()
        if result:
            assert 'request' in self.context, (
                "`%s` requires the request in the serializer"
                " context. Add `context={'request': request}` when instantiating "
                "the serializer." % self.__class__.__name__
            )
            request = self.context['request']
            include = request.GET.get('include', '')
            if self.get_actual_field_name() in include.split(','):
                return False
        return result

    def get_model_name(self):
        if self.model_name:
            return self.model_name
        else:
            return self.get_queryset().model.__name__

    def to_internal_value(self, data):
        if isinstance(data, dict) and 'objectId' in data:
            logger.debug('setting %s to pointer %r', self.get_actual_field_name(), data)
            return self.get_queryset().get(id=data['objectId'])
        return super().to_internal_value(data)

    def to_representation(self, value):
        # In this class, `value` is the entire model object, not just the field
        # we're interested in.
        assert 'request' in self.context, (
            "`%s` requires the request in the serializer"
            " context. Add `context={'request': request}` when instantiating "
            "the serializer." % self.__class__.__name__
        )
        request = self.context['request']
        if request.method == 'GET' and '_InstallationId' in request.GET:
            # Check for the 'include' parameter. http://parseplatform.github.io/docs/rest/guide/#relational-queries
            include = self.context.get('include', request.GET.get('include', ''))
            include = include.split(',')
            actual_field_name = self.get_actual_field_name()
            logger.debug('got include %s, actual_field_name %s', include, actual_field_name)
            if actual_field_name in include:
                # Need to call the serializer on the related object and then add the __type and className fields
                # to the result.
                parent_cls = self.parent.__class__
                if isinstance(self.parent, rest_framework.relations.ManyRelatedField):
                    parent_cls = self.parent.parent.__class__
                parent_meta = getattr(parent_cls, 'Meta', None)
                nested_serializers = getattr(parent_meta, 'nested_serializers', {})
                serializer_class = nested_serializers.get(actual_field_name, None)
                logger.debug('serializer_class %s', serializer_class)
                # if self.get_model_name() == 'LessonModule':
                #     import pdb; pdb.set_trace()
                if serializer_class:  # If there's no nested serializer, nothing we can do.
                    if isinstance(serializer_class, str):
                        serializer_class = rest_framework.settings.perform_import(serializer_class,
                                                                                  'nested_serializers')
                    nested_context = dict(self.context)
                    # Create the "include" parameter for the nested context.
                    nested_include = ','.join([x.split('.',1)[1] for x in include if x.startswith(actual_field_name + '.')])
                    logger.debug('include was %s, nested_include is %s', include, nested_include)
                    nested_context['include'] = nested_include
                    ser = serializer_class(value, context=nested_context)
                    data = ser.data
                    data['__type'] = 'Object'
                    data['className'] = self.get_model_name()
                    return data
                else:
                    logger.error('No nested serializer for %s', actual_field_name)

            #logger.debug('Returning pointer for field %s - className %s - include is %s' % (self.get_actual_field_name(), self.get_model_name(), include))
            return {
                "__type": "Pointer",
                "className": self.get_model_name(),
                "objectId": str(value.pk)
            }
        else:
            return super().to_representation(value)


class MySerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super().__init__(*args, **kwargs)

    serializer_related_field = MyRelatedField

    objectId = serializers.CharField(source='id')
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='updated_at')

    class Meta:
        nested_serializers = {}


def get_divisions_i_can_view(user):
    direct_perm_query = ObjectUserPermission.objects.filter(user=user, permission__in=['view', 'change'])
    direct_views = Division.objects.filter(permissions__in=direct_perm_query)

    # Custom query to get all divisions I have permission on and all
    # their descendants. It's unfortunate that we have to do this as a
    # raw query, but Django does not support recursive queries.
    # ES: TODO: Filter out deleted divisions.
    query = '''
    WITH RECURSIVE cte AS
      (SELECT lp_division.*
        FROM lp_division
        WHERE lp_division.id IN (%s)
        UNION ALL
          SELECT lp_division.*
            FROM lp_division
            INNER JOIN cte ON lp_division.parent_id=cte.id)
      SELECT * FROM cte;
    ''' % (','.join(str(d.id) for d in
                    direct_views),)  # I hate to interpolate in Python before calling SQL, but SQLite raw calls can't do arrays.

    divisions_i_can_view = Division.objects.raw(query)

    # SQLite driver crashes on an empty response. Work around that:
    try:
        divisions_i_can_view.columns
    except TypeError:
        return User.objects.none()

    return divisions_i_can_view


# class MarkDeletedMixin:
#     def perform_destroy(self, instance):
#         import pdb; pdb.set_trace()
#         instance.mark_deleted()

class MyModelViewSet(viewsets.ModelViewSet):
    def perform_destroy(self, instance):
        instance.mark_deleted()


# --------------------------------------------------------------------------------
# User

class UserSerializer(MySerializer):
    company = MyRelatedField('company-detail', read_only=True, model_name='Company')

    profile_picture = serializers.SerializerMethodField()

    def get_profile_picture(self, obj):
        # ES: TODO: Fill in a real picture.
        if obj.email.startswith('mgr'):
            return '/static/img/profile1.png'
        else:
            return '/static/img/profile2.png'

    class Meta:
        model = User
        fields = (
        'objectId', 'createdAt', 'updatedAt', 'url', 'name', 'email', 'is_staff', 'division', 'profile_picture',
        'company', 'roles')
        nested_serializers = {'division': 'lp.api.DivisionSerializer',
                              'company': 'lp.api.CompanySerializer',
                              'roles': 'lp.api.RoleSerializer'}


class UserViewSet(MyModelViewSet):
    queryset = User.active_objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Limit it to users this user can view.
        if self.action == 'list' and not self.request.user.is_superuser:
            # Can view users that belong to a division we have 'view' or
            # 'change' permission on, or that belong to any children of those
            # divisions, or that we directly have 'view' or 'change' permissions
            # on.

            direct_perm_query = ObjectUserPermission.objects.filter(user=user, permission__in=['view', 'change'])
            direct_views = Q(permissions__in=direct_perm_query)

            divisions_i_can_view = get_divisions_i_can_view(user)
            queryset = queryset.filter(direct_views |
                                       Q(division__in=divisions_i_can_view))

        return queryset


router.register(r'User', UserViewSet)
# Also include the underscore version, for the Parse API
router.register(r'_User', UserViewSet)


# --------------------------------------------------------------------------------
# Role

# Read-only
class RoleSerializer(MySerializer):
    class Meta:
        model = Role
        fields = ('objectId', 'createdAt', 'updatedAt', 'company', 'name')
        nested_serializers = {'company': 'lp.api.CompanySerializer'}


# Read only: Can only list and retrieve.
class RoleViewSet(rest_framework.mixins.RetrieveModelMixin,
                  rest_framework.mixins.ListModelMixin,
                  rest_framework.viewsets.GenericViewSet):
    queryset = Role.active_objects.all()
    serializer_class = RoleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(company=self.request.user.company)


router.register(r'Role', RoleViewSet)


# --------------------------------------------------------------------------------
# UserInvite

# -- Not accessible via API


# --------------------------------------------------------------------------------
# Division

class DivisionSerializer(MySerializer):
    class Meta:
        model = Division
        fields = ('objectId', 'createdAt', 'updatedAt', 'name', 'description', 'parent', 'company', 'employees')
        nested_serializers = {'parent': 'lp.api.DivisionSerializer',
                              'company': 'lp.api.CompanySerializer',
                              'employees':'lp.api.UserSerializer'}


class DivisionViewSet(MyModelViewSet):
    queryset = Division.active_objects.all()
    serializer_class = DivisionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        # Limit it to divisions this user can view.
        if self.action == 'list' and not user.is_superuser:
            divisions_i_can_view = get_divisions_i_can_view(user)
            queryset = queryset.filter(pk__in=[d.id for d in divisions_i_can_view])

        return queryset


router.register(r'Division', DivisionViewSet)


# --------------------------------------------------------------------------------
# Company

class CompanySerializer(MySerializer):
    class Meta:
        model = Company
        fields = ('objectId', 'createdAt', 'updatedAt', 'name', 'slug', 'top_division')
        nested_serializers = {'top_division': 'lp.api.DivisionSerializer'}


class CompanyViewSet(rest_framework.mixins.RetrieveModelMixin,
                     rest_framework.viewsets.GenericViewSet):
    '''
    Company view set. You can only get info for the current company.
    '''
    queryset = Company.active_objects.all()
    serializer_class = CompanySerializer


router.register(r'Company', CompanyViewSet)


# --------------------------------------------------------------------------------
# PerformanceMetric

class PerformanceMetricSerializer(MySerializer):
    class Meta:
        model = PerformanceMetric
        fields = ('objectId', 'createdAt', 'updatedAt', 'name', 'company')


class PerformanceMetricViewSet(rest_framework.mixins.RetrieveModelMixin,
                               rest_framework.mixins.ListModelMixin,
                               rest_framework.viewsets.GenericViewSet):
    queryset = PerformanceMetric.active_objects.all()
    serializer_class = PerformanceMetricSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(company=self.request.user.company)


router.register(r'PerformanceMetric', PerformanceMetricViewSet)


# --------------------------------------------------------------------------------
# PerformanceScore

class PerformanceScoreSerializer(MySerializer):
    class Meta:
        model = PerformanceScore
        fields = ('objectId', 'createdAt', 'updatedAt', 'user', 'metric', 'created_by', 'score')
        nested_serializers = {'user': 'lp.api.UserSerializer',
                              'metric': 'lp.api.PerformanceMetricSerializer',
                              'created_by': 'lp.api.UserSerializer'}


class PerformanceScoreViewSet(MyModelViewSet):
    queryset = PerformanceScore.active_objects.all()
    serializer_class = PerformanceScoreSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if self.action == 'list' and not user.is_superuser:
            direct_perm_query = ObjectUserPermission.objects.filter(user=user, permission__in=['view', 'change'])
            direct_views = Q(user__permissions__in=direct_perm_query)

            divisions_i_can_view = get_divisions_i_can_view(user)
            queryset = queryset.filter(direct_views |
                                       Q(user__division__in=divisions_i_can_view))

        return queryset


router.register(r'PerformanceScore', PerformanceScoreViewSet)


# --------------------------------------------------------------------------------
# Lesson

class LessonSerializer(MySerializer):
    class Meta:
        model = Lesson
        fields = ('objectId', 'createdAt', 'updatedAt', 'name', 'passing_score', 'module', 'questions')
        nested_serializers = {
            'questions': 'lp.api.QuizQuestionSerializer',
            'module': 'lp.api.LessonModuleSerializer',
        }


class LessonViewSet(rest_framework.mixins.RetrieveModelMixin,
                    rest_framework.mixins.ListModelMixin,
                    rest_framework.viewsets.GenericViewSet):
    queryset = Lesson.active_objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(module__category__company=self.request.user.company)


router.register(r'Lesson', LessonViewSet)


# --------------------------------------------------------------------------------
# LessonModule

class LessonModuleSerializer(MySerializer):
    class Meta:
        model = LessonModule
        fields = ('objectId', 'createdAt', 'updatedAt', 'name', 'lessons')
        nested_serializers = {'lessons':'lp.api.LessonSerializer'}


class LessonModuleViewSet(rest_framework.mixins.RetrieveModelMixin,
                          rest_framework.mixins.ListModelMixin,
                          rest_framework.viewsets.GenericViewSet):
    queryset = LessonModule.active_objects.all()
    serializer_class = LessonModuleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(category__company=self.request.user.company)


router.register(r'LessonModule', LessonModuleViewSet)


# --------------------------------------------------------------------------------
# LessonModuleCategory

class LessonModuleCategorySerializer(MySerializer):
    class Meta:
        model = LessonModuleCategory
        fields = ('objectId', 'createdAt', 'updatedAt', 'name', 'company', 'modules')
        nested_serializers = {'modules': 'lp.api.LessonModuleSerializer',
                              'company': 'lp.api.CompanySerializer'}


class LessonModuleCategoryViewSet(rest_framework.mixins.RetrieveModelMixin,
                                  rest_framework.mixins.ListModelMixin,
                                  rest_framework.viewsets.GenericViewSet):
    queryset = LessonModuleCategory.active_objects.all()
    serializer_class = LessonModuleCategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(company=self.request.user.company)


router.register(r'LessonModuleCategory', LessonModuleCategoryViewSet)


# --------------------------------------------------------------------------------
# LessonRequest

# class LessonRequestSerializer(MySerializer):
#     class Meta:
#         model = LessonRequest
#         fields = ('objectId', 'createdAt', 'updatedAt', 'user', 'created_by', 'lesson')
#         nested_serializers = {
#             'user':'lp.api.UserSerializer',
#             'created_by':'lp.api.UserSerializer',
#             'lesson':'lp.api.LessonSerializer',
#             }

# class LessonRequestViewSet(MyModelViewSet):
#     queryset = LessonRequest.active_objects.all()
#     serializer_class = LessonRequestSerializer

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         return queryset.filter(lesson__module__company=self.request.user.company)

# router.register(r'LessonRequest', LessonRequestViewSet)

# --------------------------------------------------------------------------------
# QuizQuestion

class QuizQuestionSerializer(MySerializer):
    class Meta:
        model = QuizQuestion
        fields = ('objectId', 'createdAt', 'updatedAt', 'lesson', 'text', 'order', 'answers')
        nested_serializers = {'lesson': 'lp.api.LessonSerializer',
                              'answers': 'lp.api.QuizAnswerSerializer',
        }


class QuizQuestionViewSet(rest_framework.mixins.RetrieveModelMixin,
                          rest_framework.mixins.ListModelMixin,
                          rest_framework.viewsets.GenericViewSet):
    queryset = QuizQuestion.active_objects.all()
    serializer_class = QuizQuestionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(lesson__module__company=self.request.user.company)


router.register(r'QuizQuestion', QuizQuestionViewSet)


# --------------------------------------------------------------------------------
# QuizAnswer

class QuizAnswerSerializer(MySerializer):
    class Meta:
        model = QuizAnswer
        fields = ('objectId', 'createdAt', 'updatedAt', 'question',
                  'text')  # Don't include the 'is_correct' field because then people will be able to cheat!
        nested_serializers = {'question': 'lp.api.QuizQuestionSerializer'}


class QuizAnswerViewSet(rest_framework.mixins.RetrieveModelMixin,
                        rest_framework.mixins.ListModelMixin,
                        rest_framework.viewsets.GenericViewSet):
    queryset = QuizAnswer.active_objects.all()
    serializer_class = QuizAnswerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(question__lesson__module__company=self.request.user.company)


router.register(r'QuizAnswer', QuizAnswerViewSet)


# --------------------------------------------------------------------------------
# QuizAttempt

class QuizAttemptSerializer(MySerializer):
    passed = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ('objectId', 'createdAt', 'updatedAt', 'user', 'lesson', 'score', 'created_by', 'passed')
        nested_serializers = {'user': 'lp.api.UserSerializer',
                              'lesson': 'lp.api.LessonSerializer',
                              'created_by': 'lp.api.UserSerializer'}


class QuizAttemptViewSet(MyModelViewSet):
    queryset = QuizAttempt.active_objects.all()
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if self.action == 'list' and not user.is_superuser:
            direct_perm_query = ObjectUserPermission.objects.filter(user=user, permission__in=['view', 'change'])
            direct_views = Q(user__permissions__in=direct_perm_query)

            divisions_i_can_view = list(get_divisions_i_can_view(user))
            queryset = queryset.filter(Q(user=user) |
                                       direct_views |
                                       Q(user__division__in=divisions_i_can_view))
        return queryset


router.register(r'QuizAttempt', QuizAttemptViewSet)


# --------------------------------------------------------------------------------
# QuizAnswerAttempt

class QuizAnswerAttemptSerializer(MySerializer):
    user = MyRelatedField('user-detail', read_only=True, model_name='User')

    class Meta:
        model = QuizAnswerAttempt
        fields = ('objectId', 'createdAt', 'updatedAt', 'quiz_attempt', 'answer', 'user')
        nested_serializers = {'quiz_attempt': 'lp.api.QuizAttemptSerializer',
                              'answer': 'lp.api.QuizAnswerSerializer',
                              'user': 'lp.api.UserSerializer'}


class QuizAnswerAttemptViewSet(MyModelViewSet):
    queryset = QuizAnswerAttempt.active_objects.all()
    serializer_class = QuizAnswerAttemptSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if self.action == 'list' and not user.is_superuser:
            direct_perm_query = ObjectUserPermission.objects.filter(user=user, permission__in=['view', 'change'])
            direct_views = Q(quiz_attempt__user__permissions__in=direct_perm_query)

            divisions_i_can_view = list(get_divisions_i_can_view(user))
            queryset = queryset.filter(Q(quiz_attempt__user=user) |
                                       direct_views |
                                       Q(quiz_attempt__user__division__in=divisions_i_can_view))
        return queryset


router.register(r'QuizAnswerAttempt', QuizAnswerAttemptViewSet)
