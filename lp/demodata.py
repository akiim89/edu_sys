# -*- coding: utf-8 -*-
import decimal
import random

from .models import *

NAMES = [
    "Jaylan Frost",
    "Ava Haas",
    "Lane Terry",
    "Marvin Yu",
    "Nicolas Oconnell",
    "Helen Baker",
    "Akira Villa",
    "Deon Moyer",
    "Ana Simmons",
    "Aydan Acosta",
    "Kelvin Mcdonald",
    "Shayla Solis",
    "Mya Fernandez",
    "Tatum Beasley",
    "Yadiel Wong",
    "Devin Mccullough",
    "John Heath",
    "Hayden Mcbride",
    "Lawrence Marks",
    "Jacey Gillespie",
    "Ashton Lang",
    "Laney Lara",
    "Brisa Kennedy",
    "Kyra Simpson",
    "Emerson Marshall",
    "Eliana Mcguire",
    "Miriam Bates",
    "Jazmine Chavez",
    "Joy Houston",
    "Saige Mcdaniel",
    "Juliette Chapman",
    "Odin Vaughan",
    "Marcus Poole",
    "Brooklynn Proctor",
    "Elisa Michael",
    "Macy Haney",
    "Nyasia Huff",
    "Abbey Haynes",
    "Hassan Torres",
    "Frances Spears",
    "Emilee Estes",
    "Branden Horne",
    "Noemi Hinton",
    "Isabel Allison",
    "Jakobe Strickland",
    "Brayan Richmond",
    "Savanah Cochran",
    "Eliezer Pham",
    "Gracie Farrell",
    "Hillary Weber",
]

def delete_division(division):
    # Delete all employees
    division.employees.all().delete()
    # Recursively delete all child divisions
    for child in division.children.all():
        delete_division(child)
    # Delete this division.
    division.delete()

class DemoDataMaker:
    '''
    Factory class to make some demo data.

    Uses Unicode characters in various places to make sure it is handled
    correctly by the database and API.
    '''

    def __init__(self,
                 user_name='Demo CEO',
                 user_email='ceo@example.com',
                 password='Phace Demo',
                 company_name='Costa Vida',
                 slug='costavida'):
        self.user_name = user_name
        self.user_email = user_email
        self.password = password
        self.company_name = company_name
        self.company_slug = slug
        self.name_index = 0

        self.company = None
        self.ceo = None
        self.domain = '%s.com' % self.company_slug

    def get_name(self):
        self.name_index = (self.name_index + 1) % len(NAMES)
        return NAMES[self.name_index]
    

    def delete_company(self):
        '''
        Deletes the company named by company_name and all it's divisions and
        employees.
        '''
        try:
            company = Company.objects.get(name=self.company_name)
        except Company.DoesNotExist:
            print('No company to delete')
            return
        # Recursively delete all divisions and employees.
        Role.objects.filter(company=company).delete()
        delete_division(company.top_division)
        company.delete()

      
    def email(self, part):
        return '%s@%s' % (part, self.domain)

    def make_metrics(self, company):
        result = []
        for n in range(0, 5):
            result.append(PerformanceMetric.objects.create(company=company,
                                                           name='%s Metric %s' % (company.name, n+1)))
        return result
                          

    def make_performance_scores(self, user, metrics, managers):
        managers_or_none = [None] + managers
        for _n in range(0, 5):
            PerformanceScore.objects.create(user=user,
                                            metric = random.choice(metrics),
                                            created_by = random.choice(managers_or_none),
                                            score = decimal.Decimal(random.randint(20, 100)))

    def make_roles(self):
        Role.objects.bulk_create([
            Role(company=self.company,
                 name='CEO'),
            Role(company=self.company,
                 name='Regional Manager'),
            Role(company=self.company,
                 name='Sub-regional Manager'),
            Role(company=self.company,
                 name='Store Manager'),
            Role(company=self.company,
                 name='Team Member'),
            ])

    def make_lesson(self, module, name):
        questions_and_answers = [{'question':'What is the answer to %s #%s?' % (name,i),
                                  'answers':[
                                      '%s: Correct answer to #%s' % (name,i),
                                      '%s: Wrong answer to #%s' % (name,i),
                                      '%s: Another wrong answer to #%s' % (name,i),
                                      '%s: Yet another wrong answer to #%s' % (name,i),
                                  ]
        } for i in range(1,5)]


        lesson = Lesson.objects.create_lesson(name=name,
                                              template=name + '.html',
                                              module=module,
                                              questions_and_answers=questions_and_answers[:10])
        return lesson
        

    def make_module_category(self, name):
        category = LessonModuleCategory.objects.create(company=self.company, name=name)
        return category

    def make_module(self, category, name):
        lessons = []
        module = LessonModule.objects.create(category=category, name=name);
        for i in range(1,5):
            lessons.append(self.make_lesson(module, '%s Lesson %s' % (name, i)))
        return lessons

    def make_company(self):
        from django.db import transaction
        self.delete_company()

        with transaction.atomic():
            top_division = Division.objects.create()
            self.company = Company.objects.create(name=self.company_name,
                                                  top_division=top_division,
                                                  slug=self.company_slug)

            self.make_roles()

            self.ceo = User.objects.create_user(name=self.user_name,
                                                email=self.user_email,
                                                password=self.password,
                                                division=top_division,
                                                is_manager=True,
                                                roles=['CEO'])

            self.metrics = self.make_metrics(self.company)

            lessons = []
            
            for category_name in ['Front of House', 'Back of House']:
                category = self.make_module_category('%s' % (category_name,))
                for module_name in ['People', 'New Hire Packet', 'Training',
                                    'Drive-Thru', 'Manager', 'Pride', 'Product', 'Profitability', 'Catering']:
                    lessons.extend(self.make_module(category, '%s' % (module_name,)))
                
                             

            # Make the organizational structure:
            #                   Global
            #         East                  West
            # Northeast  Southeast  Northwest  Southwest
            # 1 2 3 4    1 2 3 4    1 2 3 4    1 2 3 4
            #
            # Each division gets a manager. Each location (the bottom nodes in the
            # tree) gets a couple non-manager employees.

            name_index = 0
            for ew in ['East', 'West']:
                # Regional division
                ewdiv = Division.objects.create(name=ew,
                                                parent=top_division,
                                                description="Regional division")
                # Regional manager
                ewuser = User.objects.create_user(email=self.email('mgr.%s' % ew.lower()),
                                                  name=self.get_name(),
                                                  password=self.password,
                                                  division=ewdiv,
                                                  is_manager=True,
                                                  roles=['Regional Manager'])
                ewinvite = UserInvite.objects.create(user=ewuser, created_by=self.ceo)
                print('***** REGIONAL MANAGER Invite code for %s: %s' % (ew, ewinvite.invite_code))
                for ns in ['North', 'South']:
                    # Sub-Regional division
                    nsname = '%s %s' % (ns, ew)
                    nsdiv = Division.objects.create(name=nsname,
                                                    parent=ewdiv,
                                                    description='Sub-regional division')
                    # Sub-Regional manager
                    nsuser = User.objects.create_user(email=self.email('mgr.%s' % nsname.lower().replace(' ', '.')),
                                                      name=self.get_name(),
                                                      password=self.password,
                                                      division=nsdiv,
                                                      is_manager=True,
                                                      roles=['Sub-regional Manager'])
                    nsinvite = UserInvite.objects.create(user=nsuser, created_by=ewuser)
                    print('***** MANAGER Invite code for %s: %s' % (nsname, nsinvite.invite_code))

                    for n in range(1,5):
                        # Single location
                        locname = '%s %s' % (nsname, n)
                        locdiv = Division.objects.create(name=locname,
                                                         parent=nsdiv,
                                                         description='Single location')
                        # Single location manager
                        locmgr = User.objects.create_user(email=self.email('mgr.%s' % locname.lower().replace(' ', '.')),
                                                          name=self.get_name(),
                                                          password=self.password,
                                                          division=locdiv,
                                                          is_manager=True,
                                                          roles=['Store Manager'])
                        # Some employees
                        for emp in range(1,3):
                            empname = '%s %s' % (locname, emp)
                            empuser = User.objects.create_user(email=self.email('emp.%s' % empname.lower().replace(' ', '.')),
                                                               name=self.get_name(),
                                                               password=self.password,
                                                               division = locdiv,
                                                               roles=['Team Member'])
                            empinvite = UserInvite.objects.create(user=empuser, created_by=locmgr)
                            print('Invite code for %s: %s' % (empname, empinvite.invite_code))

                            # Each employee takes some of the tests.
                            for lesson in random.sample(lessons, 3):
                                quiz_attempt = QuizAttempt.objects.create(user=empuser, lesson=lesson)

                                answer_attempts = [QuizAnswerAttempt(quiz_attempt=quiz_attempt,
                                                                     answer=random.choice(question.answers.all()))
                                                   for question in lesson.questions.all()]

                                QuizAnswerAttempt.objects.bulk_create(answer_attempts)
                                quiz_attempt.update_score()
                                quiz_attempt.save()

                            self.make_performance_scores(empuser, self.metrics, [locmgr, nsuser, ewuser])
        return self.company
