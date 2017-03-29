# -*- coding: utf-8 -*-

import json
from unittest.mock import patch

from django.core.urlresolvers import reverse
from django.test import TestCase

from lp import models
from lp.demodata import DemoDataMaker


def pointer(obj):
    return {'__type':'Pointer',
            'className':obj.__class__.__name__,
            'objectId':str(obj.id)}

class FacebookLoginTest(TestCase):

    def test_api(self):
        ddm = DemoDataMaker(user_name='DĔМŐ ČĔŐ',
                            user_email='veronica@example.com',
                            password='Phace Demo',
                            company_name='Veridian Dynamics',
                            slug='veridian-dynamics')
        company = ddm.make_company()

        company2 = DemoDataMaker(user_name='ceo 2',
                                 user_email='ceo@company2.com',
                                 password='Phace Demo',
                                 company_name='company2',
                                 slug='company2').make_company()

        manager = models.User.objects.get(email='veronica@example.com')
        other_user = models.User.objects.exclude(id=manager.id).first()
        user = models.User.objects.get(email='emp.south.west.4.2@veridian-dynamics.com')
#        user = models.User.objects.create_user(email='test@example.com', name='Test User', division=company.top_division)
        invite = models.UserInvite.objects.create(user=user, created_by=manager)
        invite_code = invite.invite_code()

        url = reverse('api-social-login')

        # Try with no facebook authData. Should fail with 401
        response = self.client.post(url,
                                    json.dumps({
                                        'authData':{
                                        },
                                        'invite_code':invite_code,                                            
                                    }),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 401)

        # Try with no facebook id. Should fail with 401
        response = self.client.post(url,
                                    json.dumps({
                                        'authData':{
                                            'facebook':{
                                                'access_token':'Can put anything here',
                                                'expiration_date':'2020-08-27T01:23:45.678Z',
                                                'invite_code':invite_code
                                            }
                                        },
                                        'invite_code':invite_code,                                            
                                    }),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 401)

        # Try with credentials that are (mocked to be) invalid.
        with patch('fb.access_token_is_valid', return_value=False):
            # Try and succeed.
            response = self.client.post(url,
                                        json.dumps({
                                            'authData':{
                                                'facebook':{
                                                    'id':'FAKEID',
                                                    'access_token':'Can put anything here',
                                                    'expiration_date':'2020-08-27T01:23:45.678Z',
                                                    'invite_code':invite_code
                                                }
                                            },
                                            'invite_code':invite_code,                                            
                                        }),
                                        content_type="application/json")
            
            self.assertEqual(response.status_code, 401)
        

        # Try with credentials that are (mocked to be) valid.
        with patch('fb.access_token_is_valid', return_value=True):
            # Try and succeed.
            response = self.client.post(url,
                                        json.dumps({
                                            'authData':{
                                                'facebook':{
                                                    'id':'FAKEID',
                                                    'access_token':'Can put anything here',
                                                    'expiration_date':'2020-08-27T01:23:45.678Z',
                                                    'invite_code':invite_code
                                                }
                                            },
                                            'invite_code':invite_code,                                            
                                        }),
                                        content_type="application/json")
            
            self.assertEqual(response.status_code, 200)

        # Now logged in.

        # Should be able to get info about myself, but no other user.
        url = reverse('user-detail', args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('user-detail', args=[manager.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        url = reverse('user-detail', args=[other_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # Should be able to get all Roles for this company.
        url = reverse('role-list')
        response = self.client.get(url, {'_InstallationId':'123'})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(len(response.data), company.roles.count())
        for r in response.data:
            c = r['company']
            self.assertEqual(c['objectId'], str(company.id))
            self.assertEqual(c['__type'], 'Pointer')
            self.assertEqual(c['className'], 'Company')
        
        # Should be able to get all PerformanceMetrics for this company.
        url = reverse('performancemetric-list')
        response = self.client.get(url, {'_InstallationId':'123'})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(len(response.data), company.roles.count())
        for r in response.data:
            c = r['company']
            self.assertEqual(c['objectId'], str(company.id))
            self.assertEqual(c['__type'], 'Pointer')
            self.assertEqual(c['className'], 'Company')

        # Should be able to get all LessonModules for this company.
        url = reverse('lessonmodule-list')
        response = self.client.get(url, {'_InstallationId':'123'})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(len(response.data), company.lesson_modules.count())
        for r in response.data:
            c = r['company']
            self.assertEqual(c['objectId'], str(company.id))
            self.assertEqual(c['__type'], 'Pointer')
            self.assertEqual(c['className'], 'Company')

        # Should be able to see all the lessons in this company.
        url = reverse('lesson-list')
        response = self.client.get(url, {'_InstallationId':'123'})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(len(response.data), models.Lesson.objects.filter(module__company=company).count())
        for r in response.data:
            m = r['module']
            self.assertEqual(m['__type'], 'Pointer')
            self.assertEqual(m['className'], 'LessonModule')
            module = models.LessonModule.objects.get(id=m['objectId'])
            self.assertEqual(module.company, company)

        # Should be able to get all questions for each lesson.
        lessons = models.Lesson.objects.filter(module__company=company)
        for lesson in lessons:
            response = self.client.get(reverse('quizquestion-list'), {'_InstallationId':'122',
                                                                      'where':json.dumps({
                                                                          'lesson':{'__type':'Pointer',
                                                                                    'objectId':str(lesson.id),
                                                                                    'className':'Lesson'},
                                                                          }),
                                                                      })
            questions = models.QuizQuestion.objects.filter(lesson=lesson)
            question_ids = sorted(str(q.id) for q in questions)
            self.assertEqual(len(response.data), len(question_ids))
            self.assertEqual(sorted(d['objectId'] for d in response.data),
                             question_ids)
            # Should be able to get all the answers for each question.
            for question in questions:
                response = self.client.get(reverse('quizanswer-list'), {'_InstallationId':'122',
                                                                      'where':json.dumps({
                                                                          'question':{'__type':'Pointer',
                                                                                      'objectId':str(question.id),
                                                                                      'className':'QuizQuestion'},
                                                                          }),
                                                                      })
                self.assertEqual(len(response.data), 4)

        # Should only see my quiz attempts
        response = self.client.get(reverse('quizattempt-list'))
        self.assertEqual(sorted(d['objectId'] for d in response.data), sorted(str(qa.id) for qa in models.QuizAttempt.objects.filter(user=user)))

        # Should only see my answer attempts
        response = self.client.get(reverse('quizanswerattempt-list'))
        self.assertEqual(sorted(d['objectId'] for d in response.data), sorted(str(qa.id) for qa in models.QuizAnswerAttempt.objects.filter(quiz_attempt__user=user)))

        # Post an answer attempt.
        quiz_attempts = models.QuizAttempt.objects.filter(user=user)
        quiz_attempt = list(quiz_attempts)[0]
        question = list(quiz_attempt.lesson.questions.all())[0]
        answer = list(question.answers.all())[0]
        response = self.client.post(reverse('quizanswerattempt-list'), json.dumps({
            'quiz_attempt':{'__type':'Pointer',
                            'className':'QuizAttempt',
                            'objectId':str(quiz_attempt.id)},
            'user':{'__type':'Pointer',
                    'className':'_User',
                    'objectId':str(user.id)},
            'answer':reverse('quizanswer-detail', args=[answer.id])
            # 'answer':{'__type':'Pointer',
            #           'className':'Answer',
            #           'objectId':str(answer.id)}
            }),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(models.QuizAnswerAttempt.objects.filter(answer__question=question, quiz_attempt__user=user).count(), 2)
        
        # Log out.
        response = self.client.post(reverse('api-logout'))
        self.assertEqual(response.status_code, 200)

        # Should not be able to get info about myself.
        url = reverse('user-detail', args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        url = reverse('api-login')
        # Try to log in as manager, but forget username/email.
        response = self.client.get(url, {'password':'Phace Demo'})
        self.assertEqual(response.status_code, 401)
        
        # Try to log in as manager, but forget password.
        response = self.client.get(url, {'email':manager.email})
        self.assertEqual(response.status_code, 401)

        # Try to log in as manager, but invalid password.
        response = self.client.get(url, {'email':manager.email, 'password':'wrong'})
        self.assertEqual(response.status_code, 401)

        # Log in as manager.
        response = self.client.get(url, {'email':manager.email, 'password':'Phace Demo'})
        self.assertEqual(response.status_code, 200)
        #self.client.login(email=manager.email, password='Phace Demo')

        # Should be able to get info about any user.
        url = reverse('user-detail', args=[user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('user-detail', args=[manager.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('user-detail', args=[other_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Log in as East region manager. Should only see users in that region.
        self.client.logout()
        url = reverse('api-login')
        response = self.client.get(url, {'username':'mgr.east@veridian-dynamics.com', 'password':'Phace Demo'})
        self.assertEqual(response.status_code, 200)
        #self.client.login(email='mgr.east@veridian-dynamics.com', password='Phace Demo')

        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for u in response.data:
            self.assertTrue('East' in u['name'])

        # Likewise should only see divisions in that region.
        response = self.client.get(reverse('division-list'))
        self.assertEqual(response.status_code, 200)
        for d in response.data:
            self.assertTrue('East' in d['name'])
            
        # Get all the PerformanceScore objects I can.
        url = reverse('performancescore-list')
        response = self.client.get(url, {'_InstallationId':'123'})
        self.assertEqual(response.status_code, 200)

        for ps in response.data:
            user = models.User.objects.get(id=ps['user']['objectId'])
            self.assertTrue('East' in user.name)


        # Create a lesson score for an employee.
        emp = models.User.objects.get(email='emp.south.east.4.2@veridian-dynamics.com')
        n_attempts = models.QuizAttempt.objects.filter(user=emp).count()
        lesson = models.Lesson.objects.filter(module__company=company)[0]
        response = self.client.post(reverse('quizattempt-list'), json.dumps({'user':pointer(emp),
                                                                             'lesson':pointer(lesson),
                                                                             'created_by':pointer(user),
                                                                             'score':'45'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        new_n_attempts = models.QuizAttempt.objects.filter(user=emp).count()
        self.assertEqual(new_n_attempts, n_attempts + 1)
                                    

        # Now delete that quiz attempt.
        new_attempt = models.QuizAttempt.active_objects.get(id=response.data['objectId'])
        self.assertFalse(new_attempt.deleted_at)
        response = self.client.delete(reverse('quizattempt-detail', args=[new_attempt.id]))
        self.assertEqual(response.status_code, 204)
        # Object should still be there, but should be marked as deleted.
        # Reload it.
        new_attempt = models.QuizAttempt.objects.get(id=new_attempt.id)
        self.assertTrue(new_attempt.deleted_at)
        active_attempts = models.QuizAttempt.active_objects.filter(user=user) 
        self.assertEqual(active_attempts.count(), n_attempts)

        # Log in as North East region manager. Should only see users in that region.
        self.client.logout()
        self.client.login(email='mgr.north.east@veridian-dynamics.com', password='Phace Demo')

        # First without division objects
        url = reverse('user-list')
        response = self.client.get(url, {'_InstallationId':'123'})
        self.assertEqual(response.status_code, 200)
        for u in response.data:
            self.assertTrue('North East' in u['name'])
            self.assertEqual(u['division']['__type'], 'Pointer')
            self.assertEqual(u['division']['className'], 'Division')

        # Now with division objects included.
        response = self.client.get(url, {'_InstallationId':'123', 'include':'division'})
        self.assertEqual(response.status_code, 200)
        for u in response.data:
            self.assertTrue('North East' in u['name'])
            self.assertEqual(u['division']['__type'], 'Object')
            self.assertEqual(u['division']['className'], 'Division')
            self.assertTrue('North East' in u['division']['name'])

        # Likewise should only see divisions in that region.
        response = self.client.get(reverse('division-list'))
        self.assertEqual(response.status_code, 200)
        for d in response.data:
            self.assertTrue('North East' in d['name'])

        # Log in as West region manager. Should only see users in that region.
        self.client.logout()
        self.client.login(email='mgr.west@veridian-dynamics.com', password='Phace Demo')

        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        for u in response.data:
            self.assertTrue('West' in u['name'])

        # Likewise should only see divisions in that region.
        response = self.client.get(reverse('division-list'))
        self.assertEqual(response.status_code, 200)
        for d in response.data:
            self.assertTrue('West' in d['name'])
            
        # Try a limited query.
        divisionNW1 = models.Division.objects.get(name='company2 North West 1')
        divisionSW2 = models.Division.objects.get(name='company2 South West 2')
        response = self.client.get(reverse('user-list'), {
            'where':json.dumps({'division':
                                {'$in':[divisionNW1.id,
                                        divisionSW2.id]}
            })
        })
        self.assertEqual(response.status_code, 200)
        for d in response.data:
            u = models.User.objects.get(id=d['objectId'])
            with self.subTest(u=u):
                self.assertTrue(u.division == divisionNW1 or u.division == divisionSW2)
