import csv
import random
from faker                  import Faker

from django.db              import IntegrityError
from django.core.exceptions import MultipleObjectsReturned

from users.models           import User
from projects.models        import Project, Category, FundingOption, Donation

NUM_USERS        = 100
NUM_DONATION_USERS = 30
CATEGORIES       = ["tteokbok", "rameon", "soondae", "fried", "kimbab"]
SAMPLE_DATA_PATH = "./data/sample_data.csv"

def populate_db():
    data_factory = DataFactory()

    DataFactory.populate_category(CATEGORIES)
    DataFactory.populate_user(NUM_USERS)

    sample_data = data_factory.load_data(SAMPLE_DATA_PATH)

    for data in sample_data:
        DataFactory.gen_project(data)
        DataFactory.link_funding_option(data)

    DataFactory.populate_donations()

    return

class DataFactory:
    
    fake = Faker('ko_KR')

    def load_data(self, path):
        data = []
        with open(path, "r", encoding="utf-8-sig") as f:
            reader  = csv.reader(f)
            headers = next(reader)

            for line in reader:
                data.append({k: v for k, v in zip(headers, line)})
        
        return data

    @classmethod
    def populate_category(cls, category_list):
        for category_name in category_list:
            Category.objects.get_or_create(name=category_name)
        return

    @classmethod
    def populate_user(cls, num_users):
        if len(User.objects.all()) > num_users:
            return

        for _ in range(num_users):
            profile   = cls.fake.profile()
            if User.objects.filter(email=profile['mail']).exists():
                continue
            user_data = {
                        'email'   : profile['mail'],
                        'password': cls.fake.password(),
                        'username': profile['name'],
                        }
            User.objects.get_or_create(**user_data)
        
        return User.objects.all()

    @classmethod
    def gen_project(cls, data):
        creater_name         = data['creater']
        creater_email        = data['creater_email']
        creater_introduction = data['creater_introduction']
        
        if User.objects.filter(username=creater_name).exists():
            creater = User.objects.filter(username=creater_name)[0]
        
        else:
            creater, _ = User.objects.get_or_create(email=creater_email, password="password", username=creater_name, introduction=creater_introduction)
        
        input_data = {
            "title"          : data["title"],
            "creater"        : creater,
            "summary"        : data["summary"],
            "category"       : Category.objects.get(name=data["category"]),
            "title_image_url": data["title_image_url"],
            "target_fund"    : float(data["target_fund"].replace(",","")),
            "launch_date"    : data["launch_date"],
            "end_date"       : data["end_date"]
        }

        if Project.objects.filter(title=input_data["title"]).exists():
            return
        else:
            return Project.objects.create(**input_data)

    @classmethod
    def link_funding_option(cls, data):
        project = Project.objects.get(title=data["title"])

        default_option = {
                            "amount"     : 1000.0,
                            "project"    : project,
                            "remains"    : 1000,
                            "title"      : "선물을 선택하지 않고 밀어만 줍니다.",
                            "description": "기본 선물"
                        }
        FundingOption.objects.create(**default_option)
        
        options = []

        if data.get("funding_option_title_1"):
            option = {
                "amount"     : float(data["funding_option_amount_1"].replace(",","")),
                "project"    : project,
                "remains"    : int(data["funding_option_remains_1"]),
                "title"      : data["funding_option_title_1"],
                "description": data["funding_option_description_1"]
            }
            options.append(option)

        if data.get("funding_option_title_2"):
            option = {
                "amount"     : float(data["funding_option_amount_2"].replace(",","")),
                "project"    : project,
                "remains"    : int(data["funding_option_remains_2"]),
                "title"      : data["funding_option_title_2"],
                "description": data["funding_option_description_2"]
            }
            options.append(option)
        
        for option in options:
            if FundingOption.objects.filter(description = option["description"]).exists():
                continue
            else:
                FundingOption.objects.create(**option)
        
        return
    
    @classmethod
    def populate_donations(cls):
        user_list    = User.objects.all()
        project_list = Project.objects.all()

        random_user_index     = [ random.randint(0, len(user_list)-1) for _ in range(NUM_DONATION_USERS)]
        random_projects_index = [ random.randint(0, len(project_list)-1) for _ in range(NUM_DONATION_USERS) ]

        for i, user_idx in enumerate(random_user_index):
            user            = user_list[user_idx]
            project         = project_list[random_projects_index[i]]
            options         = project.fundingoption_set.all()
            option_selected = options[random.randint(0, len(options)-1)]

            Donation.objects.create(user = user, project = project, funding_option=option_selected)
            option_selected.remains -= 1
            option_selected.save()
